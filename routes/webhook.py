import mercadopago
from flask import Blueprint, request
from extensions import mongo
from config import Config

webhook_bp = Blueprint("webhook", __name__)
sdk = mercadopago.SDK(Config.MP_ACCESS_TOKEN)


@webhook_bp.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("=== WEBHOOK RECEBIDO ===")
    print(data)

    if data.get("type") == "payment":

        payment_id = data["data"]["id"]

        payment_response = sdk.payment().get(payment_id)
        payment = payment_response["response"]

        print("=== DETALHES PAGAMENTO ===")
        print(payment)

        if payment.get("status") == "approved":

            user_id = payment.get("external_reference")
            plano = payment.get("metadata", {}).get("plan")

            if user_id and plano:

                mongo.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"plan": plano}}
                )

                print(f"Plano {plano} atualizado via webhook ✅")

    return "OK", 200