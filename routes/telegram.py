import requests
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

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
    )

    if response.status_code == 200:
        flash("Publicado no Telegram com sucesso!", "success")
    else:
        flash("Erro ao publicar no Telegram.", "danger")

    return redirect(url_for("dashboard.dashboard"))