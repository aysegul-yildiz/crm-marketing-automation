def test_campaigns_page_default(logged_in_client):
    resp = logged_in_client.get("/marketing/campaigns")
    assert resp.status_code == 200
    assert b"All Campaigns" in resp.data

def test_campaigns_filter_by_status(logged_in_client):
    resp_all = logged_in_client.get("/marketing/campaigns")
    assert resp_all.status_code == 200
    full_html = resp_all.data.decode()

    resp_active = logged_in_client.get("/marketing/campaigns?status=active")
    assert resp_active.status_code == 200
    active_html = resp_active.data.decode()

    assert full_html != active_html, \
        "Filtering by status should change the visible campaign cards."

def test_campaigns_filter_by_segment(logged_in_client):
    resp_all = logged_in_client.get("/marketing/campaigns")
    html_all = resp_all.data.decode()

    resp_segment = logged_in_client.get("/marketing/campaigns?segment=VIP")
    html_segment = resp_segment.data.decode()

    assert html_all != html_segment, \
        "Filtering by segment must reduce campaign results."
