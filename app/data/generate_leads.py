
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]  
DATA_DIR = BASE_DIR / "data"                     


def main():
    customers = pd.read_csv(DATA_DIR / "customer_data.csv")
    campaigns = pd.read_csv(DATA_DIR / "campaign_data.csv")
    conversions = pd.read_csv(DATA_DIR / "conversion_event_data.csv")

    SEG_CONV_PROB = {
        "High CLV Customers": 0.20,
        "New Signups (Last 30 Days)": 0.12,
        "Inactive > 90 Days": 0.07,
        "Churn Risk": 0.05,
    }
    DEFAULT_P = 0.10

    rows = []
    lead_id = 1

    for _, camp in campaigns.iterrows():
        cid = int(camp["id"])
        seg = str(camp.get("segment", ""))

        p = SEG_CONV_PROB.get(seg, DEFAULT_P)

        conv_count = int((conversions["campaign_id"] == cid).sum())

        if conv_count == 0:
            leads_count = int(np.random.randint(20, 80))
        else:
            leads_count = max(conv_count, int(round(conv_count / p)))

        seg_customers = customers[customers["segment"] == seg]
        if seg_customers.empty:
            seg_customers = customers

        customer_ids = np.random.choice(
            seg_customers["id"].values,
            size=leads_count,
            replace=True,
        )

        converted_flags = np.array(
            [1] * conv_count + [0] * max(leads_count - conv_count, 0)
        )
        np.random.shuffle(converted_flags)

        for cust_id, is_conv in zip(customer_ids, converted_flags):
            rows.append(
                {
                    "id": lead_id,
                    "customer_id": int(cust_id),
                    "campaign_id": cid,
                    "is_converted": int(is_conv),
                    "created_at": camp.get("start_date", ""),
                }
            )
            lead_id += 1

    df = pd.DataFrame(rows)
    out_path = DATA_DIR / "lead_data.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} lead rows to {out_path}")


if __name__ == "__main__":
    main()
