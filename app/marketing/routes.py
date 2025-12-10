# app/marketing/routes.py
from flask import Blueprint, render_template, session, request
from app.auth.decorators import login_required
from datetime import datetime

from app.services.analytics_service import (
    get_kpis,
    get_campaign_effectiveness,
    get_conversion_funnel,
    get_revenue_over_time,
    get_segment_distribution,
    get_campaign_listing,
    get_segment_options,
    get_analytics_totals,
    get_conversion_funnel_filtered,
    get_revenue_over_time_filtered,
    get_revenue_by_segment_filtered,
    get_top_campaigns_by_revenue_filtered,
    load_campaigns, 
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
    """
    Detailed marketing analytics with filters:
    - from (YYYY-MM-DD)
    - to   (YYYY-MM-DD)
    - segment (exact segment name or 'all')
    - campaign_id (numeric or 'all')
    """
    # ---- read filters from query string -------------------------------
    date_from_str = request.args.get("from") or ""
    date_to_str = request.args.get("to") or ""
    segment = request.args.get("segment", "all")
    campaign_id_str = request.args.get("campaign_id", "all")

    def _parse_date(s: str):
        if not s:
            return None
        # HTML date inputs send YYYY-MM-DD
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None

    date_from = _parse_date(date_from_str)
    date_to = _parse_date(date_to_str)

    campaign_id = None
    if campaign_id_str not in ("", "all"):
        try:
            campaign_id = int(campaign_id_str)
        except ValueError:
            campaign_id = None

    # normalize segment
    if segment == "all":
        segment_filter = None
    else:
        segment_filter = segment

    # ---- load data for the page --------------------------------------
    totals = get_analytics_totals(
        start_date=date_from,
        end_date=date_to,
        segment=segment_filter,
        campaign_id=campaign_id,
    )

    funnel = get_conversion_funnel_filtered(
        start_date=date_from,
        end_date=date_to,
        segment=segment_filter,
        campaign_id=campaign_id,
    )

    revenue_time = get_revenue_over_time_filtered(
        start_date=date_from,
        end_date=date_to,
        segment=segment_filter,
        campaign_id=campaign_id,
    )

    revenue_by_segment = get_revenue_by_segment_filtered(
        start_date=date_from,
        end_date=date_to,
        segment=segment_filter,
        campaign_id=campaign_id,
    )

    top_campaigns = get_top_campaigns_by_revenue_filtered(
        start_date=date_from,
        end_date=date_to,
        segment=segment_filter,
        campaign_id=campaign_id,
        limit=5,
    )

    # ---- build dropdown options --------------------------------------
    campaigns_df = load_campaigns()

    # distinct ordered segments from campaigns
    segment_options = sorted(campaigns_df["segment"].dropna().unique().tolist())

    # campaign dropdown: (id, name)
    campaign_options = [
        (int(row.id), f"{row.name} ({row.segment})")
        for row in campaigns_df.itertuples(index=False)
    ]

    username = session.get("username") or session.get("email")

    return render_template(
        "marketing/analytics.html",
        username=username,
        # filters (so template can keep them selected)
        date_from=date_from_str,
        date_to=date_to_str,
        current_segment=segment,
        current_campaign_id=campaign_id_str,
        segment_options=segment_options,
        campaign_options=campaign_options,
        # totals
        total_revenue=totals["total_revenue"],
        total_spend=totals["total_spend"],
        overall_roi=totals["overall_roi"],
        converted_leads=totals["converted_leads"],
        total_leads=totals["total_leads"],
        # charts – IMPORTANT: names match analytics.html
        funnel_labels=funnel["labels"],
        funnel_values=funnel["values"],
        revenue_over_time_labels=revenue_time["labels"],
        revenue_over_time_values=revenue_time["values"],
        revenue_by_segment_labels=revenue_by_segment["labels"],
        revenue_by_segment_values=revenue_by_segment["values"],
        top_campaigns=top_campaigns,
    )
