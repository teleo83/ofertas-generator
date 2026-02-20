from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import mongo
from bson.objectid import ObjectId

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    user = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})

    if request.method == "POST":
        update_data = {
            "shopee_client_id": request.form.get("shopee_client_id"),
            "shopee_client_secret": request.form.get("shopee_client_secret"),
            "telegram_token": request.form.get("telegram_token"),
            "telegram_chat_id": request.form.get("telegram_chat_id"),
            "mercado_livre_token": request.form.get("mercado_livre_token"),
            "amazon_key": request.form.get("amazon_key")
        }

        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v}

        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )

        flash("Configurações salvas com sucesso!", "success")
        return redirect(url_for("settings.settings"))

    user = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})

    shopee_ok = bool(user.get("shopee_client_id") and user.get("shopee_client_secret"))
    telegram_ok = bool(user.get("telegram_token") and user.get("telegram_chat_id"))
    ml_ok = bool(user.get("mercado_livre_token"))
    amazon_ok = bool(user.get("amazon_key"))

    return render_template(
        "settings.html",
        user=user,
        shopee_ok=shopee_ok,
        telegram_ok=telegram_ok,
        ml_ok=ml_ok,
        amazon_ok=amazon_ok
    )