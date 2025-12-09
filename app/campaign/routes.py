from flask import render_template
from . import campaign_bp

@campaign_bp.route("/", endpoint="new_campaign") 
def index():
    return render_template("campaign/create_campaign.html")