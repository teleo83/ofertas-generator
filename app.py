from flask import Flask
from config import Config
from extensions import login_manager, mongo
from routes.telegram import telegram_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensões
    mongo.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # Importar modelo User
    from models.user_model import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Registrar Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.settings import settings_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(telegram_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)