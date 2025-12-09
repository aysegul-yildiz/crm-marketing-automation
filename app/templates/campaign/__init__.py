from flask import Blueprint

campaign_bp = Blueprint(
    "campaign",
    __name__,
    url_prefix="/campaign"
)

from . import routes  # make sure routes are loaded
