from flask import Blueprint, request, render_template, redirect, url_for, session
from app.services.auth_service import register_user, authenticate_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        user = authenticate_user(email, password)

        if user:
            session["email"] = user.email
            session["username"] = user.username
            session["user_id"] = user.id
            return redirect(url_for("marketing.dashboard"))
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        pw = request.form["password"]
        pw2 = request.form["passwordAgain"]

        if pw != pw2:
            return "Passwords do not match. <a href='/register'>Try again</a>"

        success = register_user(email, username, pw)
        if success:
            return "Registered! <a href='/login'>Login</a>"
        else:
            return "Email already exists. <a href='/register'>Try again</a>"
        
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
    

    return render_template("register.html")
