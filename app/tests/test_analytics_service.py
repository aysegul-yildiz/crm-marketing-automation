
from app.services.analytics_service import (
    get_kpis,
    get_conversion_funnel,
    get_revenue_over_time,
    get_campaign_listing,
    get_analytics_totals,
)


def test_get_kpis_basic_shape():
    kpis = get_kpis()

    for key in ["total_customers", "total_segments", "active_campaigns", "roi"]:
        assert key in kpis

    assert isinstance(kpis["total_customers"], int)
    assert isinstance(kpis["total_segments"], int)
    assert isinstance(kpis["active_campaigns"], int)
    assert isinstance(kpis["roi"], float) or isinstance(kpis["roi"], int)

    assert kpis["total_customers"] >= 0
    assert kpis["total_segments"] >= 0
    assert kpis["active_campaigns"] >= 0


def test_get_conversion_funnel_stages_fixed():
    funnel = get_conversion_funnel()
    assert funnel["labels"] == ["delivered", "opened", "clicked", "converted"]
    assert len(funnel["values"]) == 4
    for v in funnel["values"]:
        assert isinstance(v, int)
        assert v >= 0


def test_get_revenue_over_time_monotonic_dates():
    rot = get_revenue_over_time()
    labels = rot["labels"]
    values = rot["values"]

    assert len(labels) == len(values)
    if len(labels) >= 2:
        assert labels == sorted(labels)


def test_get_campaign_listing_default_filters():
    campaigns = get_campaign_listing()

    assert isinstance(campaigns, list)
    if campaigns:
        row = campaigns[0]
        for key in [
            "id",
            "name",
            "segment",
            "status",
            "sent",
            "open_rate",
            "click_rate",
            "conversion_rate",
            "revenue",
            "spend",
            "roi",
            "leads",
            "lead_conversion_rate",
        ]:
            assert key in row

        assert row["sent"] >= 0
        assert 0 <= row["open_rate"] <= 100
        assert 0 <= row["click_rate"] <= 100
        assert 0 <= row["conversion_rate"] <= 100


def test_get_analytics_totals_basic():
    totals = get_analytics_totals()

    for key in [
        "total_revenue",
        "total_spend",
        "overall_roi",
        "total_leads",
        "converted_leads",
    ]:
        assert key in totals

    assert totals["total_spend"] >= 0
    assert totals["total_leads"] >= 0
    assert totals["converted_leads"] >= 0
