# app/services/analytics_service.py

from pathlib import Path
from typing import List, Dict
import pandas as pd
from datetime import date

# -------------------------------------------------------------------
# Always load CSVs from:  app/data/
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]     # -> app/
DATA_DIR = BASE_DIR / "data"                       # -> app/data/



def _load_csv(filename: str) -> pd.DataFrame:
    """
    Loads a mock CSV from app/data with safe error messages.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"[analytics_service] CSV not found: {path}")
    return pd.read_csv(path)

def load_leads() -> pd.DataFrame:
    return _load_csv("lead_data.csv")


# ---- CSV loaders --------------------------------------------------- #

def load_customers() -> pd.DataFrame:
    return _load_csv("customer_data.csv")


def load_campaigns() -> pd.DataFrame:
    return _load_csv("campaign_data.csv")


def load_campaign_events() -> pd.DataFrame:
    return _load_csv("campaign_event_data.csv")


def load_conversion_events() -> pd.DataFrame:
    return _load_csv("conversion_event_data.csv")


# ---- High-level KPIs ----------------------------------------------- #

def get_kpis() -> Dict:
    """
    Returns top-level KPIs for the dashboard:
      - total_customers
      - total_segments
      - active_campaigns
      - roi (very simple mock)
    """
    customers = load_customers()
    campaigns = load_campaigns()
    conversions = load_conversion_events()

    # total customers
    total_customers = len(customers)

    # number of segments
    seg_col = "segment" if "segment" in customers.columns else None
    total_segments = customers[seg_col].nunique() if seg_col else 0

    # active campaigns
    if "status" in campaigns.columns:
        active_campaigns = int((campaigns["status"] == "Active").sum())
    else:
        active_campaigns = 0

       # ROI = total revenue / total spend * 100 (never negative)
    total_revenue = conversions["revenue"].sum() if "revenue" in conversions.columns else 0.0

    # prefer 'spend'; fall back to 'budget' if needed
    if "spend" in campaigns.columns:
        total_spend = campaigns["spend"].sum()
    elif "budget" in campaigns.columns:
        total_spend = campaigns["budget"].sum()
    else:
        total_spend = 0.0

    roi = (total_revenue / total_spend * 100) if total_spend > 0 else 0.0

    return{
        "total_customers": int(total_customers),
        "total_segments": int(total_segments),
        "active_campaigns": int(active_campaigns),
        "roi": round(float(roi), 1),
    }


# ---- Segment distribution ------------------------------------------ #

def get_segment_distribution() -> Dict:
    """
    Returns names and counts per segment for the 'Audience Breakdown' chart.
    """
    customers = load_customers()
    seg_col = None
    if "segment" in customers.columns:
        seg_col = "segment"
    elif "Segment" in customers.columns:
        seg_col = "Segment"

    if not seg_col:
        return {"names": [], "counts": []}

    vc = customers[seg_col].value_counts()

    return {
        "names": vc.index.tolist(),
        "counts": [int(v) for v in vc.values],
    }


# ---- Conversion funnel --------------------------------------------- #

def get_conversion_funnel() -> Dict:
    """
    Overall funnel totals across all campaigns.
    Expects campaign_event_data.csv to have column 'event_type'
    with values like: delivered, opened, clicked, converted.
    """
    events = load_campaign_events()
    if "event_type" not in events.columns:
        return {"labels": [], "values": []}

    stages = ["delivered", "opened", "clicked", "converted"]
    counts = [
        int((events["event_type"] == stage).sum())
        for stage in stages
    ]

    return {"labels": stages, "values": counts}


def get_revenue_over_time() -> Dict:
    conversions = load_conversion_events()

    # Support both 'conversion_date' and 'event_date'
    date_col = None
    if "conversion_date" in conversions.columns:
        date_col = "conversion_date"
    elif "event_date" in conversions.columns:
        date_col = "event_date"

    if not date_col or "revenue" not in conversions.columns:
        return {"labels": [], "values": []}

    conversions[date_col] = pd.to_datetime(
        conversions[date_col], errors="coerce", dayfirst=True
    )

    series = (
        conversions.dropna(subset=[date_col])
        .groupby(conversions[date_col].dt.date)["revenue"]
        .sum()
        .sort_index()
    )

    return {
        "labels": [str(d) for d in series.index],
        "values": [float(v) for v in series.values],
    }


# ---- Campaign effectiveness ---------------------------------------- #

def get_campaign_effectiveness() -> List[Dict]:
    """
    Returns one row per campaign with:
      - sent (delivered)
      - opened
      - clicked
      - converted
      - open_rate, click_rate, conversion_rate  (as %)
      - revenue  (sum of conversion_event.revenue)
    """
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()

    if "id" not in campaigns.columns:
        return []

    # Group events by campaign_id & event_type
    if {"campaign_id", "event_type"}.issubset(events.columns):
        grouped = (
            events.groupby(["campaign_id", "event_type"])["id"]
            .count()
            .unstack(fill_value=0)
        )
    else:
        grouped = pd.DataFrame()


    for col in ["delivered", "opened", "clicked", "converted"]:
        if col not in grouped.columns:
            grouped[col] = 0

    grouped = grouped.rename(
        columns={
            "delivered": "sent",
            "opened": "opened",
            "clicked": "clicked",
            "converted": "converted",
        }
    )

    # Revenue per campaign
    if {"campaign_id", "revenue"}.issubset(conversions.columns):
        revenue_by_campaign = (
            conversions.groupby("campaign_id")["revenue"]
            .sum()
            .rename("revenue")
        )
    else:
        revenue_by_campaign = pd.Series(dtype=float, name="revenue")

    # Merge everything with the campaigns table
    df = campaigns.set_index("id")
    if not grouped.empty:
        df = df.join(grouped, how="left")
    if not revenue_by_campaign.empty:
        df = df.join(revenue_by_campaign, how="left")

    # Fill missing numeric columns
    for col in ["sent", "opened", "clicked", "converted", "revenue"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    sent = df["sent"].replace(0, pd.NA)
    df["open_rate"] = (df["opened"] / sent * 100).fillna(0)
    df["click_rate"] = (df["clicked"] / sent * 100).fillna(0)
    df["conversion_rate"] = (df["converted"] / sent * 100).fillna(0)


    df["open_rate"] = df["open_rate"].round(1)
    df["click_rate"] = df["click_rate"].round(1)
    df["conversion_rate"] = df["conversion_rate"].round(1)
    df["revenue"] = df["revenue"].round(2)

    results: List[Dict] = []
    for _, row in df.reset_index().iterrows():
        results.append(
            {
                "id": int(row["id"]),
                "name": row.get("name", ""),
                "objective": row.get("objective", ""),
                "segment": row.get("segment", ""),
                "status": row.get("status", ""),
                "sent": int(row["sent"]),
                "open_rate": float(row["open_rate"]),
                "click_rate": float(row["click_rate"]),
                "conversion_rate": float(row["conversion_rate"]),
                "revenue": float(row["revenue"]),
            }
        )

    return results

def get_campaign_listing(status_filter: str = "all", segment_filter: str = "all"):
    """
    Return all campaigns with basic effectiveness metrics
    for the 'See all campaigns' page.

    status_filter: "all" | "active" | "completed"
    segment_filter: "all" | <exact segment name>
    """
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()
    leads_df = load_leads()

    # ---- pre-aggregate leads ---------------------------------------- #
    if not leads_df.empty and {"campaign_id", "id"}.issubset(leads_df.columns):
        leads_by_campaign = (
            leads_df.groupby("campaign_id")["id"].count().to_dict()
        )
        if "is_converted" in leads_df.columns:
            converted_leads_by_campaign = (
                leads_df[leads_df["is_converted"] == 1]
                .groupby("campaign_id")["id"]
                .count()
                .to_dict()
            )
        else:
            converted_leads_by_campaign = {}
    else:
        leads_by_campaign = {}
        converted_leads_by_campaign = {}

    rows = []

    for _, camp in campaigns.iterrows():
        cid = camp["id"]

        ev = events[events["campaign_id"] == cid]
        conv = conversions[conversions["campaign_id"] == cid]

        delivered = (ev["event_type"] == "delivered").sum()
        opened = (ev["event_type"] == "opened").sum()
        clicked = (ev["event_type"] == "clicked").sum()
        converted = (ev["event_type"] == "converted").sum()

        revenue = float(conv["revenue"].sum()) if not conv.empty else 0.0
        spend = float(camp.get("spend", 0) or 0)

        open_rate = opened / delivered if delivered else 0
        click_rate = clicked / delivered if delivered else 0
        conv_rate = converted / delivered if delivered else 0
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0

        # leads & lead conversion
        leads = int(leads_by_campaign.get(cid, 0))
        converted_leads = int(converted_leads_by_campaign.get(cid, 0))
        lead_conv_rate = (converted_leads / leads * 100) if leads else 0.0

        segment = camp["segment"] if "segment" in campaigns.columns else ""
        status = camp["status"] if "status" in campaigns.columns else ""

        row = {
            "id": int(cid),
            "name": camp.get("name", f"Campaign {cid}"),
            "segment": segment,
            "status": status,
            "sent": int(delivered),
            "open_rate": round(open_rate * 100, 1),
            "click_rate": round(click_rate * 100, 1),
            "conversion_rate": round(conv_rate * 100, 1),
            "revenue": round(revenue, 2),
            "spend": round(spend, 2),
            "roi": round(roi, 1),
            "start_date": camp.get("start_date"),
            "leads": leads,
            "lead_conversion_rate": round(lead_conv_rate, 1),
        }

        rows.append(row)

    # --- apply filters -------------------------------------------------
    if status_filter != "all":
        sf = status_filter.lower()
        rows = [r for r in rows if r["status"].lower() == sf]

    if segment_filter != "all":
        rows = [r for r in rows if r["segment"] == segment_filter]

    try:
        rows = sorted(rows, key=lambda r: r["start_date"] or "", reverse=True)
    except Exception:
        pass

    return rows

def get_segment_options() -> list[str]:
    """
    Return a sorted list of distinct segment names from campaign_data.csv,
    used to populate the 'Segment' filter dropdown.
    """
    campaigns = load_campaigns()

    if "segment" not in campaigns.columns:
        return []

    # unique, non-empty segments
    segs = (
        campaigns["segment"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    segs = [s for s in segs.unique().tolist() if s]

    return sorted(segs)


def get_lead_conversion_by_campaign() -> Dict[int, Dict]:

    customers = load_customers()
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()

    # figure out which column holds segment name
    seg_col = None
    if "segment" in customers.columns:
        seg_col = "segment"
    elif "Segment" in customers.columns:
        seg_col = "Segment"

    if not seg_col:
        # we can't compute lead metrics without segment info
        return {}

    # Leads = "New Signups (Last 30 Days)"
    lead_mask = customers[seg_col] == "New Signups (Last 30 Days)"
    leads_df = customers[lead_mask]

    if leads_df.empty:
        return {}

    lead_ids = set(leads_df["id"].astype(int).tolist())

    # Events that involve leads only
    if not {"customer_id", "campaign_id"}.issubset(events.columns):
        return {}

    events["customer_id"] = events["customer_id"].astype(int)
    events["campaign_id"] = events["campaign_id"].astype(int)

    lead_events = events[events["customer_id"].isin(lead_ids)]

    # Conversions that involve leads only
    if not {"customer_id", "campaign_id"}.issubset(conversions.columns):
        return {}

    conversions["customer_id"] = conversions["customer_id"].astype(int)
    conversions["campaign_id"] = conversions["campaign_id"].astype(int)

    lead_conversions = conversions[conversions["customer_id"].isin(lead_ids)]

    metrics: Dict[int, Dict] = {}

    for _, camp in campaigns.iterrows():
        cid = int(camp["id"])

        # all leads this campaign touched (any event type)
        ev_camp = lead_events[lead_events["campaign_id"] == cid]
        leads_touched_ids = ev_camp["customer_id"].dropna().unique()
        leads_touched = int(len(leads_touched_ids))

        # leads that actually converted, attributed to this campaign id
        conv_camp = lead_conversions[lead_conversions["campaign_id"] == cid]
        leads_converted_ids = conv_camp["customer_id"].dropna().unique()
        leads_converted = int(len(leads_converted_ids))

        if leads_touched > 0:
            lead_conv_rate = leads_converted / leads_touched * 100.0
        else:
            lead_conv_rate = 0.0

        lead_revenue = (
            float(conv_camp["revenue"].sum())
            if "revenue" in conv_camp.columns and not conv_camp.empty
            else 0.0
        )

        metrics[cid] = {
            "leads_touched": leads_touched,
            "leads_converted": leads_converted,
            "lead_conversion_rate": round(lead_conv_rate, 1),
            "lead_revenue": round(lead_revenue, 2),
        }

    return metrics


def _apply_common_filters(
    campaigns: pd.DataFrame,
    events: pd.DataFrame,
    conversions: pd.DataFrame,
    start_date: date | None = None,
    end_date: date | None = None,
    segment: str | None = None,
    campaign_id: int | None = None,
):
    campaigns = campaigns.copy()
    events = events.copy()
    conversions = conversions.copy()

    # ---- campaign filter ---------------------------------------------
    if campaign_id is not None:
        campaigns = campaigns[campaigns["id"] == campaign_id]
        events = events[events["campaign_id"] == campaign_id]
        conversions = conversions[conversions["campaign_id"] == campaign_id]

    # ---- segment filter ----------------------------------------------
    if segment:
        campaigns = campaigns[campaigns["segment"] == segment]
        valid_ids = set(campaigns["id"])
        events = events[events["campaign_id"].isin(valid_ids)]
        conversions = conversions[conversions["campaign_id"].isin(valid_ids)]

    # ---- date filters -------------------------------------------------
    def _filter_by_date(df: pd.DataFrame, col: str):
        if col not in df.columns or df.empty:
            return df
        d = pd.to_datetime(df[col], dayfirst=True, errors="coerce").dt.date
        mask = pd.Series(True, index=df.index)
        if start_date:
            mask &= d >= start_date
        if end_date:
            mask &= d <= end_date
        return df[mask]

    # events always use event_date
    events = _filter_by_date(events, "event_date")

    # conversions use conversion_date if available, otherwise fall back
    conv_date_col = None
    if "conversion_date" in conversions.columns:
        conv_date_col = "conversion_date"
    elif "event_date" in conversions.columns:
        conv_date_col = "event_date"

    if conv_date_col:
        conversions = _filter_by_date(conversions, conv_date_col)

    return campaigns, events, conversions



def get_analytics_totals(
    start_date: date | None = None,
    end_date: date | None = None,
    segment: str | None = None,
    campaign_id: int | None = None,
) -> Dict:
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()

    campaigns, events, conversions = _apply_common_filters(
        campaigns, events, conversions,
        start_date=start_date,
        end_date=end_date,
        segment=segment,
        campaign_id=campaign_id,
    )

    total_revenue = float(conversions["revenue"].sum()) if "revenue" in conversions.columns else 0.0

    # prefer 'spend', fall back to budget
    if "spend" in campaigns.columns:
        total_spend = float(campaigns["spend"].sum())
    elif "budget" in campaigns.columns:
        total_spend = float(campaigns["budget"].sum())
    else:
        total_spend = 0.0

    if total_spend > 0:
        overall_roi = (total_revenue - total_spend) / total_spend * 100.0
    else:
        overall_roi = 0.0

    # simple lead model:
    # - total leads: all "clicked"
    # - converted leads: all "converted"
    if "event_type" in events.columns:
        total_leads = int((events["event_type"] == "clicked").sum())
        converted_leads = int((events["event_type"] == "converted").sum())
    else:
        total_leads = 0
        converted_leads = 0

    return {
        "total_revenue": round(total_revenue, 1),
        "total_spend": round(total_spend, 1),
        "overall_roi": round(overall_roi, 1),
        "total_leads": total_leads,
        "converted_leads": converted_leads,
    }


# --------- filtered funnel -------------------------------------------

def get_conversion_funnel_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
    segment: str | None = None,
    campaign_id: int | None = None,
) -> Dict:
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()  # not used, but kept for symmetry

    campaigns, events, _ = _apply_common_filters(
        campaigns, events, conversions,
        start_date=start_date,
        end_date=end_date,
        segment=segment,
        campaign_id=campaign_id,
    )

    if "event_type" not in events.columns:
        return {"labels": [], "values": []}

    stages = ["delivered", "opened", "clicked", "converted"]
    counts = [
        int((events["event_type"] == stage).sum())
        for stage in stages
    ]
    return {"labels": stages, "values": counts}


# --------- filtered revenue over time --------------------------------
def get_revenue_over_time_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
    segment: str | None = None,
    campaign_id: int | None = None,
) -> Dict:
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()

    campaigns, _, conversions = _apply_common_filters(
        campaigns, events, conversions,
        start_date=start_date,
        end_date=end_date,
        segment=segment,
        campaign_id=campaign_id,
    )

    # pick correct date column
    date_col = None
    if "conversion_date" in conversions.columns:
        date_col = "conversion_date"
    elif "event_date" in conversions.columns:
        date_col = "event_date"

    if not date_col or "revenue" not in conversions.columns:
        return {"labels": [], "values": []}

    conversions[date_col] = pd.to_datetime(
        conversions[date_col], dayfirst=True, errors="coerce"
    )

    series = (
        conversions.dropna(subset=[date_col])
        .groupby(conversions[date_col].dt.date)["revenue"]
        .sum()
        .sort_index()
    )

    return {
        "labels": [str(d) for d in series.index],
        "values": [float(v) for v in series.values],
    }

# --------- filtered revenue by segment -------------------------------

def get_revenue_by_segment_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
    segment: str | None = None,
    campaign_id: int | None = None,
) -> Dict:
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()

    campaigns, _, conversions = _apply_common_filters(
        campaigns, events, conversions,
        start_date=start_date,
        end_date=end_date,
        segment=segment,
        campaign_id=campaign_id,
    )

    if conversions.empty:
        return {"labels": [], "values": []}

    # join conversions with campaigns to know which segment each conversion belongs to
    merged = conversions.merge(
        campaigns[["id", "segment"]],
        left_on="campaign_id",
        right_on="id",
        how="left",
        suffixes=("", "_camp"),
    )

    if "segment" not in merged.columns:
        return {"labels": [], "values": []}

    grouped = merged.groupby("segment")["revenue"].sum().sort_values(ascending=False)

    return {
        "labels": grouped.index.tolist(),
        "values": [float(v) for v in grouped.values],
    }


# --------- filtered top campaigns by revenue -------------------------

def get_top_campaigns_by_revenue_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
    segment: str | None = None,
    campaign_id: int | None = None,
    limit: int = 5,
) -> list[Dict]:
    campaigns = load_campaigns()
    events = load_campaign_events()
    conversions = load_conversion_events()

    campaigns, events, conversions = _apply_common_filters(
        campaigns, events, conversions,
        start_date=start_date,
        end_date=end_date,
        segment=segment,
        campaign_id=campaign_id,
    )

    if campaigns.empty:
        return []

    # basic metrics per campaign
    ev_group = (
        events.groupby(["campaign_id", "event_type"])["id"]
        .count()
        .unstack(fill_value=0)
    ) if not events.empty else pd.DataFrame()

    for col in ["delivered", "opened", "clicked", "converted"]:
        if col not in ev_group.columns:
            ev_group[col] = 0

    ev_group = ev_group.rename(
        columns={
            "delivered": "sent",
            "opened": "opened",
            "clicked": "clicked",
            "converted": "converted",
        }
    )

    rev_group = (
        conversions.groupby("campaign_id")["revenue"].sum()
        if not conversions.empty and "revenue" in conversions.columns
        else pd.Series(dtype=float, name="revenue")
    )

    df = campaigns.set_index("id")
    if not ev_group.empty:
        df = df.join(ev_group, how="left")
    if not rev_group.empty:
        df = df.join(rev_group, how="left")

    for col in ["sent", "opened", "clicked", "converted", "revenue"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    sent = df["sent"].replace(0, pd.NA)
    df["open_rate"] = (df["opened"] / sent * 100).fillna(0)
    df["click_rate"] = (df["clicked"] / sent * 100).fillna(0)
    df["conversion_rate"] = (df["converted"] / sent * 100).fillna(0)

    spend = df.get("spend", pd.Series(0, index=df.index))
    df["roi"] = ((df["revenue"] - spend) / spend * 100).where(spend > 0, 0)

    df = df.sort_values(by="revenue", ascending=False).head(limit)

    results = []
    for idx, row in df.reset_index().iterrows():
        results.append(
            {
                "id": int(row["id"]),
                "name": row.get("name", ""),
                "segment": row.get("segment", ""),
                "status": row.get("status", ""),
                "sent": int(row["sent"]),
                "open_rate": float(row["open_rate"]),
                "click_rate": float(row["click_rate"]),
                "conversion_rate": float(row["conversion_rate"]),
                "revenue": float(row["revenue"]),
                "spend": float(row.get("spend", 0.0)),
                "roi": float(row["roi"]),
            }
        )
    return results
