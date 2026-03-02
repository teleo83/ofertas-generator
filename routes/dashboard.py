import requests
import time
import hashlib
import json
import re
from urllib.parse import urlparse
from datetime import datetime

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from extensions import mongo
from bson.objectid import ObjectId

dashboard_bp = Blueprint("dashboard", __name__)


# ==========================================
# FUNÇÃO GERAR OFERTA REAL
# ==========================================
def gerar_oferta_real(link, user):

    CLIENT_ID = user.get("shopee_client_id")
    CLIENT_SECRET = user.get("shopee_client_secret")

    if not CLIENT_ID or not CLIENT_SECRET:
        return None, "⚠ Configure a API da Shopee primeiro."

    try:
        if "s.shopee.com.br" in link:
            response = requests.get(link, allow_redirects=True, timeout=10)
            link = response.url
    except:
        return None, "Erro ao expandir link da Shopee."

    shop_id = None
    item_id = None

    try:
        parsed = urlparse(link)
        path = parsed.path

        match_product = re.search(r"/product/(\d+)/(\d+)", path)
        if match_product:
            shop_id = match_product.group(1)
            item_id = match_product.group(2)

        if not shop_id:
            match_slug = re.search(r"-i\.(\d+)\.(\d+)", path)
            if match_slug:
                shop_id = match_slug.group(1)
                item_id = match_slug.group(2)

        if not shop_id:
            parts = path.strip("/").split("/")
            if len(parts) >= 2 and parts[-1].isdigit() and parts[-2].isdigit():
                shop_id = parts[-2]
                item_id = parts[-1]

        if not shop_id or not item_id:
            return None, f"❌ Não foi possível extrair IDs desse link.\n\nLink recebido:\n{link}"

    except Exception as e:
        return None, f"Erro ao processar link: {str(e)}"

    query = f"""
    query {{
      productOfferV2(
        shopId: {int(shop_id)},
        itemId: {int(item_id)},
        limit: 1
      ){{
        nodes{{
          productName
          imageUrl
          priceMin
          offerLink
          sales
        }}
      }}
    }}
    """

    payload = {"query": query}
    body = json.dumps(payload, separators=(',', ':'))
    timestamp = int(time.time())

    fator = CLIENT_ID + str(timestamp) + body + CLIENT_SECRET
    signature = hashlib.sha256(fator.encode("utf-8")).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={CLIENT_ID}, Timestamp={timestamp}, Signature={signature}"
    }

    try:
        response = requests.post(
            "https://open-api.affiliate.shopee.com.br/graphql",
            headers=headers,
            data=body,
            timeout=15
        )
        data = response.json()
    except:
        return None, "❌ Erro ao conectar com API Shopee."

    nodes = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])

    if not nodes:
        return None, "❌ Produto não encontrado na API."

    produto = nodes[0]

    nome = produto.get("productName", "Produto")
    preco_raw = produto.get("priceMin", 0)
    link_final = produto.get("offerLink", link)
    vendas = produto.get("sales", 0)
    imagem_url = produto.get("imageUrl")

    try:
        preco = f"R$ {float(preco_raw):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        preco = "R$ --"

    mensagem = f"""🔥 <b>OFERTA DO DIA</b> 🔥

🛍 {nome}
💰 {preco}

🔥 +{vendas} vendidos

👉 <a href="{link_final}">🎯 VER OFERTA COMPLETA AQUI</a>
"""

    return imagem_url, mensagem


# ==========================================
# ROTA DASHBOARD
# ==========================================
@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    mensagem = None
    imagem_url = None

    user = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})

    plano = user.get("plan", "free")
    ofertas_dia = user.get("ofertas_dia", 0)
    ultimo_reset = user.get("ultimo_reset")

    now = datetime.utcnow()

    if isinstance(ultimo_reset, str):
        try:
            ultimo_reset = datetime.fromisoformat(ultimo_reset)
        except:
            ultimo_reset = None

    if not ultimo_reset or ultimo_reset.date() != now.date():
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {
                "$set": {
                    "ofertas_dia": 0,
                    "ultimo_reset": now
                }
            }
        )
        ofertas_dia = 0

    if request.method == "POST":
        link = request.form.get("link")

        if link:
            imagem_url, mensagem = gerar_oferta_real(link, user)

            if mensagem and "OFERTA DO DIA" in mensagem:
                mongo.db.users.update_one(
                    {"_id": ObjectId(current_user.id)},
                    {"$inc": {"ofertas_geradas": 1}}
                )

    return render_template(
        "dashboard.html",
        mensagem=mensagem,
        imagem_url=imagem_url,
        telegram_posts_today=ofertas_dia,
        plano=plano
    )