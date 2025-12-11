from flask import render_template, request, redirect, url_for, flash
from . import campaign_bp
from app.services.CampaignManagementService import CampaignManagementService
from app.services.SegmentationMaintainerService import SegmentationMaintainerService

@campaign_bp.route("/", endpoint="new_campaign") 
def index():
    status_filter = request.args.get("status", "")
    campaigns = CampaignManagementService.filterCampaigns(status_filter)

    return render_template(
        "campaign/create_campaign.html",
        campaigns=campaigns,
        selected_status=status_filter
    )

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
        
@campaign_bp.route("/edit", methods=["GET"], endpoint="edit_campaign")
def edit_campaign():
    campaign_id = request.args.get("campaign_id")
    
    if not campaign_id:
        flash("No campaign selected!", "error")
        return redirect(url_for("campaign.new_campaign"))
    
    campaign = CampaignManagementService.get_campaign_by_id(int(campaign_id))

    if not campaign:
        flash("Campaign not found!", "error")
        return redirect(url_for("campaign.new_campaign"))

    return render_template(
        "campaign/edit_campaign.html",
        campaign=campaign
    )

@campaign_bp.route("/update", methods=["POST"], endpoint="update_campaign")
def update_campaign():
    campaign_id = request.form.get("campaign_id")
    name = request.form.get("name", "").strip()
    status = request.form.get("status", "").strip()

    if not campaign_id:
        flash("Invalid campaign ID!", "error")
        return redirect(url_for("campaign.new_campaign"))

    try:
        # call service update method (you will implement soon)
        CampaignManagementService.update_campaign(int(campaign_id), name, status)

        flash("Campaign updated successfully!", "success")
        return redirect(url_for("campaign.new_campaign"))

    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for("campaign.edit_campaign", campaign_id=campaign_id))


@campaign_bp.route("/workflows", endpoint="workflows_page")
def workflows_page():
    campaigns = CampaignManagementService.filterCampaigns("")

    # Get the selected ID from URL
    selected_campaign_id = request.args.get("selected_campaign_id", type=int)

    workflows = []
    if selected_campaign_id:
        workflows = CampaignManagementService.get_workflows_by_campaign_id(selected_campaign_id)

    print("URL argument:", request.args)
    return render_template(
        "campaign/workflows.html",
        campaigns=campaigns,
        workflows=workflows,
        selected_campaign_id=selected_campaign_id
    )


@campaign_bp.route("/create_workflow", methods=["POST"], endpoint="create_workflow")
def create_workflow():
    campaign_id = request.form.get("campaign_id")
    workflow_name = request.form.get("workflow_name")

    CampaignManagementService.create_workflow(workflow_name, campaign_id)

    # Redirect back to workflow page with selected campaign
    return redirect(url_for("campaign.workflows_page", selected_campaign_id=campaign_id))


@campaign_bp.route("/workflow/<int:workflow_id>/steps", endpoint="workflow_steps_page")
def workflow_steps_page(workflow_id):
    workflow = CampaignManagementService.get_workflow_by_id(workflow_id)

    if not workflow:
        flash("Workflow not found!", "error")
        return redirect(url_for("campaign.workflows_page"))

    workflow_steps = CampaignManagementService.get_workflow_steps(workflow_id)
    segmentation_groups= SegmentationMaintainerService.get_all_groups()

    return render_template("campaign/workflow_steps.html",
        workflow=workflow,
        steps=workflow_steps,
        segmentation_groups=segmentation_groups
    )



@campaign_bp.route("/add_step", methods=["POST"], endpoint="add_workflow_step")
def add_workflow_step():
    workflow_id = int(request.form.get("workflow_id"))
    step_order = int(request.form.get("step_order"))
    action_type = request.form.get("action_type")
    action_payload = request.form.get("action_payload")
    delay = int(request.form.get("delay_minutes_after_prev", 0))

    CampaignManagementService.add_workflow_step(
        workflow_id=workflow_id,
        step_order=step_order,
        action_type=action_type,
        action_payload=action_payload,
        delay_minutes_after_prev=delay
    )

    return redirect(url_for("campaign.workflow_steps_page", workflow_id=workflow_id))


@campaign_bp.route("/campaign_segments")
def campaign_segments_page():
    # Fetch data needed for the page
    campaigns = CampaignManagementService.get_all_campaigns()
    segmentation_groups = SegmentationMaintainerService.get_all_groups()
    
    return render_template(
        "campaign/campaign_segments.html",
        campaigns=campaigns,
        segmentation_groups=segmentation_groups
    )

@campaign_bp.route("/<int:campaign_id>/workflows")
def ajax_get_workflows(campaign_id):
    workflows = CampaignManagementService.get_workflows_by_campaign_id(campaign_id)
    return render_template("partials/workflow_list.html", workflows=workflows)
