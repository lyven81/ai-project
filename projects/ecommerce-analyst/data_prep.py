"""
Data prep for Ecommerce Analyst demo.
- Reads the raw Cash Cows dataset
- Remaps `region` from generic zones to Malaysian states
- Drops `payment_method` column
- Saves full cleaned dataset + random 150-row sample for demo
"""
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "dataset.csv"
FULL_OUT = HERE / "data" / "dataset-clean.csv"
SAMPLE_OUT = HERE / "data" / "sample-150.csv"

MALAYSIAN_STATES = [
    "Selangor", "Kuala Lumpur", "Johor", "Penang", "Perak",
    "Sarawak", "Sabah", "Kedah", "Pahang", "Negeri Sembilan",
    "Melaka", "Terengganu", "Kelantan", "Perlis", "Putrajaya", "Labuan"
]

STATE_WEIGHTS = [0.22, 0.18, 0.12, 0.10, 0.07,
                 0.06, 0.05, 0.04, 0.03, 0.03,
                 0.03, 0.02, 0.02, 0.01, 0.01, 0.01]

STATE_DELIVERY_MEAN = {
    "Selangor": 1.2, "Kuala Lumpur": 1.1, "Putrajaya": 1.3,
    "Negeri Sembilan": 2.2, "Melaka": 2.4, "Johor": 2.6,
    "Perak": 2.8, "Penang": 2.5,
    "Kedah": 3.5, "Pahang": 3.8,
    "Perlis": 4.5, "Terengganu": 4.8, "Kelantan": 5.0,
    "Sabah": 6.2, "Sarawak": 6.4, "Labuan": 6.8
}

def main():
    df = pd.read_csv(RAW)
    print(f"Raw rows: {len(df):,}")
    print(f"Raw columns: {list(df.columns)}")

    if "payment_method" in df.columns:
        df = df.drop(columns=["payment_method"])
        print("Dropped payment_method")

    if "region" in df.columns:
        rng = np.random.default_rng(seed=42)
        df["region"] = rng.choice(MALAYSIAN_STATES, size=len(df), p=STATE_WEIGHTS)
        print(f"Remapped region to {len(MALAYSIAN_STATES)} Malaysian states")

    if "delivery_time_days" in df.columns:
        rng = np.random.default_rng(seed=7)
        means = df["region"].map(STATE_DELIVERY_MEAN).values
        noise = rng.normal(0, 0.6, size=len(df))
        df["delivery_time_days"] = np.clip(np.round(means + noise), 1, 9).astype(int)
        print(f"Regenerated delivery_time_days with Malaysian logistics spread "
              f"(min={df['delivery_time_days'].min()}, max={df['delivery_time_days'].max()}, "
              f"mean={df['delivery_time_days'].mean():.2f})")

    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", dayfirst=True, errors="coerce")
    df = df.dropna(subset=["order_date"])
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
    print(f"Rows after date cleanup: {len(df):,}")

    (HERE / "data").mkdir(exist_ok=True)
    df.to_csv(FULL_OUT, index=False)
    print(f"Saved full cleaned: {FULL_OUT} ({len(df):,} rows)")

    sample = df.sample(n=150, random_state=42).reset_index(drop=True)
    sample.to_csv(SAMPLE_OUT, index=False)
    print(f"Saved 150-row sample: {SAMPLE_OUT}")

    print("\n=== Sample preview ===")
    print(sample.head(3).to_string())
    print(f"\nStates in sample: {sample['region'].nunique()}")
    print(f"Categories: {sample['category'].unique()}")
    print(f"Date range: {sample['order_date'].min()} → {sample['order_date'].max()}")

if __name__ == "__main__":
    main()
