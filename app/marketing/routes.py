from flask import Blueprint, render_template, session

marketing_bp = Blueprint("marketing", __name__, url_prefix="/marketing")


@marketing_bp.route("/")
def dashboard():
    # ---- MOCK DATA ----
    kpis = {
        "total_customers": 18200,
        "total_segments": 12,
        "active_campaigns": 3,
        "conversion_rate": 4.7,   # %
        "roi": 205,               # %
    }

    segments = [
        {"name": "High CLV Customers", "customer_count": 3200, "status": "Active"},
        {"name": "Churn Risk", "customer_count": 850, "status": "Active"},
        {"name": "New Signups (Last 30 Days)", "customer_count": 1450, "status": "Active"},
        {"name": "Inactive > 90 Days", "customer_count": 2100, "status": "Needs Attention"},
    ]

    campaigns = [
        {
            "name": "Welcome Series",
            "objective": "Onboarding",
            "status": "Active",
            "segment": "New Signups (Last 30 Days)",
            "start_date": "2025-11-01",
            "end_date": "2025-12-31",
            "sent": 4500,
            "open_rate": 62.5,
            "click_rate": 24.3,
            "conversion_rate": 7.1,
            "revenue": 24000,
        },
        {
            "name": "Winback (90+ Days Inactive)",
            "objective": "Reactivation",
            "status": "Scheduled",
            "segment": "Inactive > 90 Days",
            "start_date": "2025-12-10",
            "end_date": "2026-01-10",
            "sent": 0,
            "open_rate": 0,
            "click_rate": 0,
            "conversion_rate": 0,
            "revenue": 0,
        },
        {
            "name": "End-of-Year Upsell",
            "objective": "Upsell",
            "status": "Completed",
            "segment": "High CLV Customers",
            "start_date": "2025-10-01",
            "end_date": "2025-11-15",
            "sent": 3800,
            "open_rate": 55.1,
            "click_rate": 19.4,
            "conversion_rate": 9.3,
            "revenue": 52000,
        },
    ]

    # Charts – mock data
    conversion_funnel = {
        "labels": ["Delivered", "Opened", "Clicked", "Converted"],
        "values": [10000, 6500, 2300, 700],
    }

    revenue_over_time = {
        "labels": ["Nov 1", "Nov 5", "Nov 10", "Nov 15", "Nov 20", "Nov 25", "Nov 30"],
        "values": [1200, 2500, 4100, 5300, 6200, 7800, 9200],
    }

    top_segments = {
        "labels": ["High CLV Customers", "New Signups", "Churn Risk", "Inactive > 90 Days"],
        "values": [52000, 18000, 9500, 3100],
    }

    campaign_comparison = {
        "labels": [c["name"] for c in campaigns],
        "open_rates": [c["open_rate"] for c in campaigns],
        "click_rates": [c["click_rate"] for c in campaigns],
        "conversion_rates": [c["conversion_rate"] for c in campaigns],
    }

    # For the segment chart
    segment_names = [s["name"] for s in segments]
    segment_counts = [s["customer_count"] for s in segments]

    recent_activity = [
        "Campaign 'Welcome Series' sent Step 2 to 1,943 customers.",
        "Segment 'Churn Risk' updated with 45 new customers.",
        "Campaign 'End-of-Year Upsell' generated 12 conversions today.",
        "Workflow 'Winback Journey' activated for segment 'Inactive > 90 Days'.",
    ]

    return render_template(
        "marketing/dashboard.html",
        username=session.get("username"),
        kpis=kpis,
        segments=segments,
        campaigns=campaigns,
        conversion_funnel=conversion_funnel,
        revenue_over_time=revenue_over_time,
        top_segments=top_segments,
        campaign_comparison=campaign_comparison,
        segment_names=segment_names,
        segment_counts=segment_counts,
        recent_activity=recent_activity,
    )
