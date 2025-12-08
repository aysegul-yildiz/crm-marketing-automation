from flask import Blueprint, request, render_template, redirect, url_for, session
from app.services.auth_service import authenticate_user  # no register_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        user = authenticate_user(email, password)

        if user:
            session["email"] = user.email
            session["username"] = user.name
            session["user_id"] = user.id
            return redirect(url_for("marketing.dashboard"))
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")




@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
