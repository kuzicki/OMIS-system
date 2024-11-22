from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from ..services.user_service import UserService

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route("/")
def welcome():
    return render_template("welcome.html")


@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_routes.welcome"))


@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        errors = []
        if not password or not email:
            errors.append("All fields are required")
            return render_template("login.html", errors=errors)

        found_user = UserService.login(email, password)
        if found_user is None:
            errors.append("No user found with these credentials")
            return render_template("login.html", errors=errors)

        session["user_id"] = found_user.id

        flash("Log in successful", "success")
        return redirect(url_for("menu_routes.menu"))

    return render_template("login.html")


@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        errors = []

        if not username or not email or not password:
            errors.append("All fields are required")
            return render_template("register.html", errors=errors)

        if UserService.exists(email):
            errors.append("Email is already in use")
            return render_template("register.html", errors=errors)

        new_user = UserService.create_user(
            email,
            password,
            username,
        )

        session["user_id"] = new_user.id

        return redirect(url_for("menu_routes.menu"))

    return render_template("register.html")
