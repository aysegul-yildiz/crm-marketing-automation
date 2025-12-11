
def test_analytics_filters_change_values(logged_in_client):

    resp = logged_in_client.get("/marketing/analytics")
    assert resp.status_code == 200
    html_no_filter = resp.data.decode()

    assert "Total Revenue" in html_no_filter

    resp_filtered = logged_in_client.get("/marketing/analytics?segment=VIP")
    assert resp_filtered.status_code == 200
    html_filtered = resp_filtered.data.decode()

    assert "Total Revenue" in html_filtered

    assert html_no_filter != html_filtered, \
        "Segment filter should change analytics output."

def test_analytics_date_filter_changes_values(logged_in_client):
    resp_all = logged_in_client.get("/marketing/analytics")
    assert resp_all.status_code == 200
    html_all = resp_all.data.decode()

    resp_filtered = logged_in_client.get(
        "/marketing/analytics?from=2024-01-01&to=2024-01-15"
    )
    assert resp_filtered.status_code == 200
    html_filtered = resp_filtered.data.decode()

    assert "Total Revenue" in html_filtered

    assert html_all != html_filtered, \
        "Date filters should change the rendered analytics page."
