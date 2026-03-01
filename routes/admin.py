from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from extensions import mongo
from bson.objectid import ObjectId

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        abort(403)

    usuarios = list(mongo.db.users.find())

    total_usuarios = len(usuarios)

    total_api_configurada = mongo.db.users.count_documents({
        "shopee_client_id": {"$ne": None},
        "shopee_client_secret": {"$ne": None}
    })

    return render_template(
        "admin_dashboard.html",
        usuarios=usuarios,
        total_usuarios=total_usuarios,
        total_api_configurada=total_api_configurada
    )


@admin_bp.route("/toggle-user/<user_id>")
@login_required
def toggle_user(user_id):

    if current_user.role != "admin":
        abort(403)

    usuario = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not usuario:
        abort(404)

    if usuario["role"] == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    status_atual = usuario.get("ativo", True)
    novo_status = not status_atual

    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"ativo": novo_status}}
    )

    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/toggle-plan/<user_id>")
@login_required
def toggle_plan(user_id):

    if current_user.role != "admin":
        abort(403)

    usuario = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not usuario:
        abort(404)

    if usuario["role"] == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    plano_atual = usuario.get("plan", "free")
    novo_plano = "vitalicio" if plano_atual == "free" else "free"

    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"plan": novo_plano}}
    )

    return redirect(url_for("admin.admin_dashboard"))