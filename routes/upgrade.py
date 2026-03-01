import mercadopago
from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import mongo
from bson.objectid import ObjectId
from config import Config

upgrade_bp = Blueprint("upgrade", __name__)

sdk = mercadopago.SDK(Config.MP_ACCESS_TOKEN)


# ===============================
# PÁGINA DE PLANOS
# ===============================
@upgrade_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template("upgrade.html")


# ===============================
# CRIAR CHECKOUT
# ===============================
@upgrade_bp.route("/create-checkout", methods=["POST"])
@login_required
def create_checkout():

    plano = request.form.get("plano")

    if plano == "premium":
        titulo = "Plano Premium - Ofertas Generator"
        preco = 1.90  # TESTE SANDBOX
    elif plano == "vitalicio":
        titulo = "Plano Vitalício - Ofertas Generator"
        preco = 5.00
    else:
        return redirect(url_for("upgrade.upgrade"))

    preference_data = {
        "items": [
            {
                "title": titulo,
                "quantity": 1,
                "unit_price": preco,
                "currency_id": "BRL"
            }
        ],
        # 🔥 Guarda qual plano foi comprado
        "metadata": {
            "plan": plano
        },
        # 🔥 Guarda qual usuário pagou
        "external_reference": str(current_user.id),
        "back_urls": {
            "success": url_for("upgrade.success", _external=True),
            "failure": url_for("upgrade.upgrade", _external=True),
            "pending": url_for("upgrade.upgrade", _external=True)
        },
        # 🔥 Webhook automático
        "notification_url": url_for("upgrade.webhook", _external=True)
    }

    preference_response = sdk.preference().create(preference_data)

    print("=== RESPOSTA MERCADO PAGO ===")
    print(preference_response)

    if preference_response.get("status") != 201:
        flash("Erro ao criar pagamento no Mercado Pago.", "danger")
        return redirect(url_for("upgrade.upgrade"))

    preference = preference_response["response"]

    checkout_url = preference.get("sandbox_init_point")

    if not checkout_url:
        flash("Erro ao gerar link de pagamento.", "danger")
        return redirect(url_for("upgrade.upgrade"))

    return redirect(checkout_url)


# ===============================
# SUCCESS (APENAS VISUAL)
# NÃO ATUALIZA PLANO
# ===============================
@upgrade_bp.route("/success")
@login_required
def success():
    return render_template("payment_success.html")


# ===============================
# WEBHOOK REAL
# ===============================
@upgrade_bp.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("=== WEBHOOK RECEBIDO ===")
    print(data)

    if not data:
        return jsonify({"status": "no data"}), 400

    # Apenas pagamentos
    if data.get("type") == "payment":

        payment_id = data.get("data", {}).get("id")

        if not payment_id:
            return jsonify({"status": "no payment id"}), 400

        payment_response = sdk.payment().get(payment_id)
        payment = payment_response.get("response", {})

        print("=== DETALHES PAGAMENTO ===")
        print(payment)

        # 🔥 Só atualiza se aprovado
        if payment.get("status") == "approved":

            user_id = payment.get("external_reference")
            plano = payment.get("metadata", {}).get("plan")

            if user_id and plano:
                mongo.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"plan": plano}}
                )

                print(f"Plano {plano} atualizado via webhook ✅")

    return jsonify({"status": "ok"}), 200