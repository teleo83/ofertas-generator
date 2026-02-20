from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo
from models.user_model import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user_data = mongo.db.users.find_one({"email": email})

        if user_data and check_password_hash(user_data["password"], password):

            if not user_data.get("ativo", True):
                flash("Conta desativada.")
                return redirect(url_for("auth.login"))

            user = User(user_data)
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))

        flash("Email ou senha inválidos.")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        password = request.form.get("password")

        if mongo.db.users.find_one({"email": email}):
            flash("Email já cadastrado.")
            return redirect(url_for("auth.register"))

        usuario = {
            "nome": nome,
            "email": email,
            "password": generate_password_hash(password),
            "role": "user",
            "ativo": True,
            "plano": "free",
            "ofertas_geradas": 0
        }

        mongo.db.users.insert_one(usuario)

        flash("Cadastro realizado com sucesso!")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))