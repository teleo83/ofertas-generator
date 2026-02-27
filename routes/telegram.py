import requests
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import mongo
from bson.objectid import ObjectId

telegram_bp = Blueprint("telegram", __name__)


@telegram_bp.route("/publish", methods=["POST"])
@login_required
def publish():

    user = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})

    token = user.get("telegram_token")
    chat_id = user.get("telegram_chat_id")
    message = request.form.get("message")

    if not token or not chat_id:
        flash("Telegram não configurado.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # ==========================================
    # 🔥 CONTROLE PLANO FREE (3 POR DIA)
    # ==========================================

    plano = user.get("plan", "free")
    ofertas_dia = user.get("ofertas_dia", 0)
    ultimo_reset = user.get("ultimo_reset")

    now = datetime.utcnow()

    # Reset diário automático
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

    # Se for FREE e já atingiu limite
    if plano == "free" and ofertas_dia >= 3:
        flash("❌ Limite diário de 3 envios atingido. Faça upgrade para Premium.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # ==========================================
    # 🚀 ENVIO TELEGRAM
    # ==========================================

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
    )

    if response.status_code == 200:

        # Incrementar contador apenas se FREE
        if plano == "free":
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$inc": {"ofertas_dia": 1}}
            )

        flash("Publicado no Telegram com sucesso!", "success")
    else:
        flash("Erro ao publicar no Telegram.", "danger")

    return redirect(url_for("dashboard.dashboard"))