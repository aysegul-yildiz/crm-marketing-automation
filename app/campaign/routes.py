from flask import render_template, request, redirect, url_for, flash
from . import campaign_bp
from app.services.CampaignManagementService import CampaignManagementService

@campaign_bp.route("/", endpoint="new_campaign") 
def index():
    return render_template("campaign/create_campaign.html")

@campaign_bp.route("/create", methods=["POST"], endpoint="create_campaign")
def create_campaign():
    try:
        name = request.form.get("name", "").strip()
        status = request.form.get("status", "").strip()

        # Call service layer
        CampaignManagementService.create_campaign(name, status)

        flash("Campaign created successfully!", "success")
        return redirect(url_for("campaign.new_campaign"))

    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for("campaign.new_campaign"))
        