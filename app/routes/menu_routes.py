from flask import Blueprint, render_template, redirect, url_for, session
from ..services.user_service import UserService

menu_routes = Blueprint('menu_routes', __name__)

@menu_routes.route("/menu")
def menu():
    if "user_id" not in session:
        return redirect(url_for("auth_routes.welcome"))

    if UserService.is_admin(session["user_id"]):
        return redirect(url_for("admin_routes.panel"))
    else:
        return redirect(url_for("user_routes.find"))
