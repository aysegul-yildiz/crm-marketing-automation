"""
Tests for the main marketing pages:
- /marketing/           (dashboard)
- /marketing/campaigns  (campaign listing)
- /marketing/analytics  (detailed analytics)
"""

from flask import url_for


def test_dashboard_page_renders(logged_in_client):
    """
    The dashboard should load successfully and contain key KPI texts.
    """
    response = logged_in_client.get("/marketing/")
    assert response.status_code == 200

    html = response.data.decode("utf-8")
    # Check for main section titles rendered by dashboard.html
    assert "Marketing Overview" in html
    assert "Total Customers" in html
    assert "Active Campaigns" in html
    assert "Marketing ROI" in html


def test_campaigns_page_renders_with_defaults(logged_in_client):
    """
    /marketing/campaigns should load and show the campaigns table.
    """
    response = logged_in_client.get("/marketing/campaigns")
    assert response.status_code == 200

    html = response.data.decode("utf-8")
    assert "All campaigns" in html or "All Campaigns" in html
    assert "Status" in html
    assert "ROI %" in html or "ROI" in html


def test_campaigns_page_filters_by_status(logged_in_client):
    """
    Basic smoke test that the status filter query param is accepted.
    We only check that the page still renders (200) with a filter applied.
    """
    response = logged_in_client.get("/marketing/campaigns?status=active")
    assert response.status_code == 200


def test_analytics_page_renders_without_filters(logged_in_client):
    """
    /marketing/analytics should load and show high-level metrics and charts.
    """
    response = logged_in_client.get("/marketing/analytics")
    assert response.status_code == 200

    html = response.data.decode("utf-8")
    # Top KPIs
    assert "Marketing Analytics" in html
    assert "Total Revenue" in html
    assert "Total Spend" in html
    assert "Overall Marketing ROI" in html or "Overall Marketing Roi" in html

    # Chart labels
    assert "Conversion Funnel" in html
    assert "Revenue Over Time" in html
    assert "Revenue by Segment" in html


def test_analytics_page_supports_filters(logged_in_client):
    """
    Check that date / segment / campaign filters in query string
    are accepted and the page still renders correctly.
    """
    response = logged_in_client.get(
        "/marketing/analytics?from=2025-01-01&to=2025-12-31&segment=New+Signups+%28Last+30+Days%29&campaign_id=1"
    )
    assert response.status_code == 200
