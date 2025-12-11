from flask import url_for


def test_dashboard_page_renders(logged_in_client):
    response = logged_in_client.get("/marketing/")
    assert response.status_code == 200

    html = response.data.decode("utf-8")
    assert "Marketing Overview" in html
    assert "Total Customers" in html
    assert "Active Campaigns" in html
    assert "Marketing ROI" in html


def test_campaigns_page_renders_with_defaults(logged_in_client):
    response = logged_in_client.get("/marketing/campaigns")
    assert response.status_code == 200

    html = response.data.decode("utf-8")
    assert "All campaigns" in html or "All Campaigns" in html
    assert "Status" in html
    assert "ROI %" in html or "ROI" in html


def test_campaigns_page_filters_by_status(logged_in_client):
    response = logged_in_client.get("/marketing/campaigns?status=active")
    assert response.status_code == 200


def test_analytics_page_renders_without_filters(logged_in_client):
    response = logged_in_client.get("/marketing/analytics")
    assert response.status_code == 200

    html = response.data.decode("utf-8")
    assert "Marketing Analytics" in html
    assert "Total Revenue" in html
    assert "Total Spend" in html
    assert "Overall Marketing ROI" in html or "Overall Marketing Roi" in html

    assert "Conversion Funnel" in html
    assert "Revenue Over Time" in html
    assert "Revenue by Segment" in html


def test_analytics_page_supports_filters(logged_in_client):

    response = logged_in_client.get(
        "/marketing/analytics?from=2025-01-01&to=2025-12-31&segment=New+Signups+%28Last+30+Days%29&campaign_id=1"
    )
    assert response.status_code == 200
