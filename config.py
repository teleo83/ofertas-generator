import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/ofertas_saas"
    )

    # ============================
    # Mercado Pago
    # ============================
    MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
    MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")