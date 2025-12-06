from flask import Blueprint, render_template, session
from app.auth.routes import login_required

marketing_bp = Blueprint(
    "marketing",
    __name__,
    url_prefix="/marketing"
)


@marketing_bp.route("/")
@login_required
def dashboard():
    return render_template(
        "marketing/dashboard.html",
        username=session.get("username"),
    )
