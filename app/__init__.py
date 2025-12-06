import os
from flask import Flask, redirect, url_for, session

from .auth.routes import auth_bp
from .marketing.routes import marketing_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-change-me")

    # register modules
    app.register_blueprint(auth_bp)
    app.register_blueprint(marketing_bp)

    @app.route("/")
    def index():
        if session.get("email"):
            return redirect(url_for("marketing.dashboard"))
        return redirect(url_for("auth.login"))

    return app

