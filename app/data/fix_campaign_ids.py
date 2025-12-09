import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# ----------------- CONFIG -----------------
BASE_DIR = Path(__file__).resolve().parent

CUSTOMER_CSV = BASE_DIR / "customer_data.csv"
CAMPAIGN_CSV = BASE_DIR / "campaign_data.csv"
CAMPAIGN_EVENT_CSV = BASE_DIR / "campaign_event_data.csv"
CONVERSION_EVENT_CSV = BASE_DIR / "conversion_event_data.csv"

# how many customers per campaign to target (max)
TARGET_CUSTOMERS_PER_CAMPAIGN = 80

# funnel probabilities
P_OPEN = 0.6
P_CLICK = 0.35
P_CONVERT = 0.15

# revenue range per conversion
REVENUE_MIN = 300
REVENUE_MAX = 5000

random.seed(42)  # deterministic

# --------------- HELPERS ------------------

def parse_date(d: str) -> datetime:
    """
    Parses dates like 21/01/2025, 7/9/2025, etc. (dayfirst).
    Falls back to today if parsing fails.
    """
    if pd.isna(d):
        return datetime.today()
    d = str(d).strip()
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(d, fmt)
        except ValueError:
            continue
    return datetime.today()


def random_date_between(start: datetime, end: datetime) -> datetime:
    if end < start:
        start, end = end, start
    delta_days = (end - start).days
    if delta_days <= 0:
        return start
    offset = random.randint(0, delta_days)
    return start + timedelta(days=offset)


# --------------- MAIN LOGIC ----------------

def main():
    customers = pd.read_csv(CUSTOMER_CSV)
    campaigns = pd.read_csv(CAMPAIGN_CSV)

    # Make sure we have required columns
    assert "id" in customers.columns
    assert "segment" in customers.columns
    assert {"id", "segment", "start_date", "end_date"}.issubset(campaigns.columns)

    campaign_events_rows = []
    conversion_events_rows = []

    campaign_event_id = 1
    conversion_event_id = 1

    for _, camp in campaigns.iterrows():
        cid = int(camp["id"])
        csegment = str(camp["segment"]).strip()

        # customers in the same segment; fallback to all customers if empty
        seg_customers = customers[customers["segment"] == csegment]
        if seg_customers.empty:
            seg_customers = customers

        seg_customers = seg_customers.sample(
            n=min(TARGET_CUSTOMERS_PER_CAMPAIGN, len(seg_customers)),
            replace=False,
            random_state=42 + cid,  # deterministic per campaign
        )

        start_dt = parse_date(camp.get("start_date"))
        end_dt = parse_date(camp.get("end_date"))

        for _, cust in seg_customers.iterrows():
            cust_id = int(cust["id"])
            event_date = random_date_between(start_dt, end_dt)

            # delivered (== sent)
            campaign_events_rows.append(
                {
                    "id": campaign_event_id,
                    "customer_id": cust_id,
                    "campaign_id": cid,
                    "event_type": "delivered",
                    "event_date": event_date.strftime("%d/%m/%Y"),
                }
            )
            campaign_event_id += 1

            # opened?
            if random.random() < P_OPEN:
                campaign_events_rows.append(
                    {
                        "id": campaign_event_id,
                        "customer_id": cust_id,
                        "campaign_id": cid,
                        "event_type": "opened",
                        "event_date": event_date.strftime("%d/%m/%Y"),
                    }
                )
                campaign_event_id += 1

                # clicked?
                if random.random() < P_CLICK:
                    campaign_events_rows.append(
                        {
                            "id": campaign_event_id,
                            "customer_id": cust_id,
                            "campaign_id": cid,
                            "event_type": "clicked",
                            "event_date": event_date.strftime("%d/%m/%Y"),
                        }
                    )
                    campaign_event_id += 1

                    # converted?
                    if random.random() < P_CONVERT:
                        campaign_events_rows.append(
                            {
                                "id": campaign_event_id,
                                "customer_id": cust_id,
                                "campaign_id": cid,
                                "event_type": "converted",
                                "event_date": event_date.strftime("%d/%m/%Y"),
                            }
                        )
                        campaign_event_id += 1

                        # create matching conversion_event row
                        revenue = random.uniform(REVENUE_MIN, REVENUE_MAX)
                        conversion_events_rows.append(
                            {
                                "id": conversion_event_id,
                                "customer_id": cust_id,
                                "campaign_id": cid,
                                "revenue": round(revenue, 2),
                                # column name chosen to match analytics_service.py
                                "conversion_date": event_date.strftime("%d/%m/%Y"),
                            }
                        )
                        conversion_event_id += 1

    # Write campaign_event_data.csv
    campaign_events_df = pd.DataFrame(campaign_events_rows)
    campaign_events_df.to_csv(CAMPAIGN_EVENT_CSV, index=False)
    print(f"Wrote {len(campaign_events_df)} rows to {CAMPAIGN_EVENT_CSV.name}")

    # Write conversion_event_data.csv
    conversion_events_df = pd.DataFrame(conversion_events_rows)
    conversion_events_df.to_csv(CONVERSION_EVENT_CSV, index=False)
    print(f"Wrote {len(conversion_events_df)} rows to {CONVERSION_EVENT_CSV.name}")


if __name__ == "__main__":
    main()
