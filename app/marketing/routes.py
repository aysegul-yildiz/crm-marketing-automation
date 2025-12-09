# app/marketing/routes.py
from flask import Blueprint, render_template, session, request
from app.auth.decorators import login_required

from app.services.analytics_service import (
    get_kpis,
    get_campaign_effectiveness,
    get_conversion_funnel,
    get_revenue_over_time,
    get_segment_distribution,
    get_campaign_listing,
)

marketing_bp = Blueprint(
    "marketing",
    __name__,
    url_prefix="/marketing",
)


@marketing_bp.route("/")
@login_required
def dashboard():
    # 1) Load analytics from CSV-based service
    kpis = get_kpis()
    campaigns = get_campaign_effectiveness()
    conversion_funnel = get_conversion_funnel()
    revenue_over_time = get_revenue_over_time()
    seg_dist = get_segment_distribution()

    # 2) Simple "Recent activity" derived from top campaigns
    recent_activity = [
        f'Campaign "{c["name"]}" ({c["status"]}) – '
        f'{c["open_rate"]}% open, {c["click_rate"]}% click'
        for c in campaigns[:5]
    ]

    # 3) Render dashboard
    return render_template(
        "marketing/dashboard.html",
        username=session.get("username"),
        kpis=kpis,
        campaigns=campaigns,
        conversion_funnel=conversion_funnel,
        revenue_over_time=revenue_over_time,
        segment_names=seg_dist["names"],
        segment_counts=seg_dist["counts"],
        recent_activity=recent_activity,
    )


@marketing_bp.route("/campaigns")
@login_required
def campaigns():
    status_filter = request.args.get("status", "all")
    segment_filter = request.args.get("segment", "all")

    campaigns = get_campaign_listing(
        status_filter=status_filter,
        segment_filter=segment_filter,
    )

    username = session.get("username") or session.get("email")

    return render_template(
        "marketing/campaigns.html",
        username=username,
        campaigns=campaigns,
        status_filter=status_filter,
        segment_filter=segment_filter,
    )
