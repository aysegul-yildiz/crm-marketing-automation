from flask import render_template, request, redirect, url_for, flash
from . import segmentation_bp
from app.services.SegmentationMaintainerService import SegmentationMaintainerService
from app.services.ExternalService import ExternalService


@segmentation_bp.route("/", endpoint="new_group")
def index():
    """Displays segmentation group creation page"""

    groups = SegmentationMaintainerService.get_all_groups()  # Add this if not exists
    customers = ExternalService.get_all_customers()
    listings = ExternalService.get_all_listings()

    return render_template(
        "segmentation/create_group.html",
        groups=groups,
        users=customers,
        listings=listings
    )


@segmentation_bp.route("/create", methods=["POST"], endpoint="create_group")
def create_group():
    """Handles form submission for creating segmentation group"""
    try:
        name = request.form.get("name", "").strip()

        SegmentationMaintainerService.create_segmentation_group(name)

        flash("Segmentation group created successfully!", "success")
        return redirect(url_for("segmentation.new_group"))

    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for("segmentation.new_group"))

@segmentation_bp.route("/edit/<int:group_id>", methods=["GET"], endpoint="edit_group")
def edit_group(group_id: int):
    """Redirect to edit page for selected group"""
    return render_template("segmentation/edit_group.html", group_id=group_id)