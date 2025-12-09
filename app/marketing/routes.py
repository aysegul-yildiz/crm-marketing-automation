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
    get_segment_options,
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

    # NEW: all distinct segments for the dropdown
    segment_options = get_segment_options()

    username = session.get("username") or session.get("email")

    return render_template(
        "marketing/campaigns.html",
        username=username,
        campaigns=campaigns,
        status_filter=status_filter,
        segment_filter=segment_filter,
        segment_options=segment_options,   # <-- pass here
    )

@marketing_bp.route("/analytics")
@login_required
def analytics():
    # High-level metrics
    kpis = get_kpis()
    funnel = get_conversion_funnel()
    revenue_time = get_revenue_over_time()
    seg_dist = get_segment_distribution()

    # Use the same rows as the Campaigns page, so numbers line up
    campaign_rows = get_campaign_listing(
        status_filter="all",
        segment_filter="all",
    )

    # ---- Aggregate revenue & ROI ------------------------------------
    total_revenue = sum(row["revenue"] for row in campaign_rows)
    total_spend = sum(row["spend"] for row in campaign_rows)

    overall_roi = (
        (total_revenue - total_spend) / total_spend * 100.0
        if total_spend > 0
        else 0.0
    )

    # ---- Aggregate leads & lead conversions -------------------------
    total_leads = sum(row["leads"] for row in campaign_rows)

    # approximate converted leads from per-campaign lead conversion %
    converted_leads = sum(
        int(round(row["leads"] * (row["lead_conversion_rate"] / 100.0)))
        for row in campaign_rows
    )

    # ---- Revenue by segment -----------------------------------------
    segment_revenue = {}
    for row in campaign_rows:
        seg = row["segment"] or "Unknown"
        segment_revenue[seg] = segment_revenue.get(seg, 0.0) + row["revenue"]

    rev_seg_names = list(segment_revenue.keys())
    rev_seg_values = [round(v, 2) for v in segment_revenue.values()]

    # Top 5 campaigns by revenue (for the table)
    top_campaigns = sorted(
        campaign_rows,
        key=lambda r: r["revenue"],
        reverse=True,
    )[:5]

    username = session.get("username") or session.get("email")

    return render_template(
        "marketing/analytics.html",
        username=username,
        # KPI tiles from kpis helper
        kpis=kpis,
        # Funnel
        funnel_labels=funnel["labels"],
        funnel_values=funnel["values"],
        # Revenue over time
        rev_time_labels=revenue_time["labels"],
        rev_time_values=revenue_time["values"],
        # Audience / segment distribution (by customer count)
        segment_names=seg_dist["names"],
        segment_counts=seg_dist["counts"],
        # Revenue by segment
        rev_seg_names=rev_seg_names,
        rev_seg_values=rev_seg_values,
        # Campaign-level list & top performers
        top_campaigns=top_campaigns,
        # High-level aggregates
        total_revenue=round(total_revenue, 2),
        total_spend=round(total_spend, 2),
        overall_roi=round(overall_roi, 1),
        total_leads=int(total_leads),
        converted_leads=int(converted_leads),
    )
