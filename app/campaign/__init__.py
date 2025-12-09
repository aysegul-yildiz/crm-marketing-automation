from flask import Blueprint

campaign_bp = Blueprint(
    "campaign",        # used in url_for()
    __name__,
    url_prefix="/campaign"
)

from . import routes
