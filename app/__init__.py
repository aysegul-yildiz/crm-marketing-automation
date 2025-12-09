import os
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv

from .auth.routes import auth_bp
from .marketing.routes import marketing_bp
from .campaign.routes import campaign_bp 

def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-change-me")

    # register modules
    app.register_blueprint(auth_bp)
    app.register_blueprint(marketing_bp)
    app.register_blueprint(campaign_bp)

    @app.route("/")
    def index():
        if session.get("email"):
            return redirect(url_for("marketing.dashboard"))
        return redirect(url_for("auth.login"))

    return app
