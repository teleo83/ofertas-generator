import requests
import time
import hashlib
import json
import re
from urllib.parse import urlparse

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from extensions import mongo
from bson.objectid import ObjectId

# 🔥 PRIMEIRO declarar blueprint
dashboard_bp = Blueprint("dashboard", __name__)


# ==========================================
# FUNÇÃO GERAR OFERTA REAL
# ==========================================
def gerar_oferta_real(link, user):

    CLIENT_ID = user.get("shopee_client_id")
    CLIENT_SECRET = user.get("shopee_client_secret")

    if not CLIENT_ID or not CLIENT_SECRET:
        return "⚠ Configure a API da Shopee primeiro."

    # ------------------------------------------------
    # 1️⃣ Expandir link curto
    # ------------------------------------------------
    try:
        if "s.shopee.com.br" in link:
            response = requests.get(link, allow_redirects=True, timeout=10)
            link = response.url
    except:
        return "Erro ao expandir link da Shopee."

    shop_id = None
    item_id = None

    try:
        parsed = urlparse(link)
        path = parsed.path

        # ------------------------------------------------
        # FORMATO 1 → /product/shop_id/item_id
        # ------------------------------------------------
        match_product = re.search(r"/product/(\d+)/(\d+)", path)
        if match_product:
            shop_id = match_product.group(1)
            item_id = match_product.group(2)

        # ------------------------------------------------
        # FORMATO 2 → slug-i.shopid.itemid
        # ------------------------------------------------
        if not shop_id:
            match_slug = re.search(r"-i\.(\d+)\.(\d+)", path)
            if match_slug:
                shop_id = match_slug.group(1)
                item_id = match_slug.group(2)

        # ------------------------------------------------
        # FORMATO 3 → /shopid/itemid direto
        # ------------------------------------------------
        if not shop_id:
            parts = path.strip("/").split("/")
            if len(parts) >= 2 and parts[-1].isdigit() and parts[-2].isdigit():
                shop_id = parts[-2]
                item_id = parts[-1]

        if not shop_id or not item_id:
            return f"❌ Não foi possível extrair IDs desse link.\n\nLink recebido:\n{link}"

    except Exception as e:
        return f"Erro ao processar link: {str(e)}"

    # ------------------------------------------------
    # 2️⃣ Montar Query
    # ------------------------------------------------
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
        return "❌ Erro ao conectar com API Shopee."

    nodes = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])

    if not nodes:
        return "❌ Produto não encontrado na API."

    produto = nodes[0]

    nome = produto.get("productName", "Produto")
    preco_raw = produto.get("priceMin", 0)
    link_final = produto.get("offerLink", link)
    vendas = produto.get("sales", 0)

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

    return mensagem
    CLIENT_ID = user.get("shopee_client_id")
    CLIENT_SECRET = user.get("shopee_client_secret")

    if not CLIENT_ID or not CLIENT_SECRET:
        return "⚠ Configure a API da Shopee primeiro."

    # Expandir link curto
    try:
        if "s.shopee.com.br" in link:
            response = requests.get(link, allow_redirects=True, timeout=10)
            link = response.url
    except:
        return "Erro ao expandir link."

    shop_id = None
    item_id = None

    try:
        parsed = urlparse(link)
        path = parsed.path

        # Formato /product/shop/item
        if "/product/" in path:
            parts = path.strip("/").split("/")
            if len(parts) >= 3:
                shop_id = parts[-2]
                item_id = parts[-1]

        # Formato slug-i.shop.item
        if not shop_id and "-i." in path:
            match = re.search(r"-i\.(\d+)\.(\d+)", path)
            if match:
                shop_id = match.group(1)
                item_id = match.group(2)

        if not shop_id or not item_id:
            return "❌ Link inválido da Shopee."

    except:
        return "❌ Erro ao processar link."

    # GraphQL
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
        return "❌ Erro na API Shopee."

    nodes = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])

    if not nodes:
        return "❌ Produto não encontrado."

    produto = nodes[0]

    nome = produto.get("productName", "Produto")
    preco_raw = produto.get("priceMin", 0)
    link_final = produto.get("offerLink", link)
    vendas = produto.get("sales", 0)

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

    return mensagem


# ==========================================
# ROTA DASHBOARD
# ==========================================
@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    mensagem = None

    if request.method == "POST":
        link = request.form.get("link")

        if link:
            user = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
            mensagem = gerar_oferta_real(link, user)

            # 🔥 contador de ofertas
            if mensagem and "OFERTA DO DIA" in mensagem:
                mongo.db.users.update_one(
                    {"_id": ObjectId(current_user.id)},
                    {"$inc": {"ofertas_geradas": 1}}
                )

    return render_template("dashboard.html", mensagem=mensagem)