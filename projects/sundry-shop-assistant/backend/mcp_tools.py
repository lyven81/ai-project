"""
MCP-style tools over the sundry shop sales dataset.

Each tool queries dataset.csv (March 2024 POS data, 150 rows) and returns
a JSON-serializable dict. Gemini Live API calls these via function-calling.

To swap this for a real MCP server later:
  - Keep the same tool names and return shapes
  - Replace pandas queries with MCP client calls
  - The tool_bridge.py schema declarations don't change
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_DATASET_PATH = Path(__file__).parent.parent / "dataset.csv"
_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    """Lazy-load and cache the dataset with cleaned types."""
    global _df
    if _df is None:
        df = pd.read_csv(_DATASET_PATH)
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df["Total Sales"] = pd.to_numeric(df["Total Sales"], errors="coerce")
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
        df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
        _df = df.dropna(subset=["Total Sales"])
        logger.info(f"Loaded dataset: {len(_df)} rows, date range "
                    f"{_df['Date'].min().date()} to {_df['Date'].max().date()}")
    return _df


# ---------- 1. Sales Performance ----------

def get_total_sales() -> dict:
    """Total revenue, transaction count, and average basket over the whole dataset."""
    df = _load()
    return {
        "total_revenue_rm": round(float(df["Total Sales"].sum()), 2),
        "total_transactions": int(len(df)),
        "avg_basket_rm": round(float(df["Total Sales"].mean()), 2),
        "date_range": f"{df['Date'].min().strftime('%d %b %Y')} — {df['Date'].max().strftime('%d %b %Y')}",
    }


def get_top_day() -> dict:
    """Identify the single best-selling day in the dataset."""
    df = _load()
    daily = df.groupby(df["Date"].dt.date)["Total Sales"].agg(["sum", "count"])
    top = daily.sort_values("sum", ascending=False).head(1)
    top_date = top.index[0]
    return {
        "top_day": str(top_date),
        "revenue_rm": round(float(top["sum"].iloc[0]), 2),
        "transactions": int(top["count"].iloc[0]),
    }


def get_weekly_summary() -> dict:
    """Weekly revenue breakdown across the dataset."""
    df = _load()
    df = df.copy()
    df["week"] = df["Date"].dt.isocalendar().week
    weekly = df.groupby("week")["Total Sales"].agg(["sum", "count"]).reset_index()
    return {
        "weeks": [
            {
                "week_number": int(row["week"]),
                "revenue_rm": round(float(row["sum"]), 2),
                "transactions": int(row["count"]),
            }
            for _, row in weekly.iterrows()
        ]
    }


# ---------- 2. Product Category ----------

def get_sales_by_category() -> dict:
    """Revenue and transaction count by product category, ranked best to worst."""
    df = _load()
    grouped = df.groupby("Product Category")["Total Sales"].agg(["sum", "count", "mean"])
    grouped = grouped.sort_values("sum", ascending=False)
    return {
        "categories": [
            {
                "category": cat,
                "revenue_rm": round(float(row["sum"]), 2),
                "transactions": int(row["count"]),
                "avg_basket_rm": round(float(row["mean"]), 2),
            }
            for cat, row in grouped.iterrows()
        ]
    }


def get_slowest_category() -> dict:
    """The three worst-performing product categories by revenue."""
    df = _load()
    grouped = df.groupby("Product Category")["Total Sales"].sum().sort_values()
    return {
        "slowest": [
            {"category": cat, "revenue_rm": round(float(rev), 2)}
            for cat, rev in grouped.head(3).items()
        ]
    }


# ---------- 3. Customer Segmentation ----------

def compare_member_vs_visitor() -> dict:
    """Compare Member vs Visitor spend, transaction count, and average basket."""
    df = _load()
    grouped = df.groupby("Customer Type")["Total Sales"].agg(["sum", "mean", "count"])
    total_revenue = float(df["Total Sales"].sum())
    return {
        "segments": [
            {
                "customer_type": seg,
                "revenue_rm": round(float(row["sum"]), 2),
                "pct_of_total": round(100 * float(row["sum"]) / total_revenue, 1),
                "avg_basket_rm": round(float(row["mean"]), 2),
                "transactions": int(row["count"]),
            }
            for seg, row in grouped.iterrows()
        ]
    }


def compare_gender() -> dict:
    """Compare spend by Gender (excludes rows where gender is missing)."""
    df = _load()
    df_g = df[df["Gender"].notna() & (df["Gender"].str.strip() != "")]
    grouped = df_g.groupby("Gender")["Total Sales"].agg(["sum", "mean", "count"])
    return {
        "segments": [
            {
                "gender": g,
                "revenue_rm": round(float(row["sum"]), 2),
                "avg_basket_rm": round(float(row["mean"]), 2),
                "transactions": int(row["count"]),
            }
            for g, row in grouped.iterrows()
        ],
        "note": f"Excluded {len(df) - len(df_g)} rows with missing gender",
    }


# ---------- 4. Payment Behavior ----------

def get_payment_mix() -> dict:
    """Revenue and transaction share by payment method."""
    df = _load()
    df_p = df[df["Payment Method"].notna() & (df["Payment Method"].str.strip() != "")]
    grouped = df_p.groupby("Payment Method")["Total Sales"].agg(["sum", "count"])
    total = float(grouped["sum"].sum())
    return {
        "methods": [
            {
                "method": m,
                "revenue_rm": round(float(row["sum"]), 2),
                "pct_of_total": round(100 * float(row["sum"]) / total, 1),
                "transactions": int(row["count"]),
            }
            for m, row in grouped.iterrows()
        ],
        "note": f"Excluded {len(df) - len(df_p)} rows with missing payment method",
    }


def get_payment_by_customer_type() -> dict:
    """Cross-tab payment method preference by Member vs Visitor."""
    df = _load()
    df_p = df[df["Payment Method"].notna() & (df["Payment Method"].str.strip() != "")]
    cross = df_p.groupby(["Customer Type", "Payment Method"])["Total Sales"].count()
    result = {}
    for (ctype, method), count in cross.items():
        result.setdefault(ctype, []).append({"method": method, "transactions": int(count)})
    # Add percentages within each customer type
    for ctype, methods in result.items():
        total = sum(m["transactions"] for m in methods)
        for m in methods:
            m["pct_of_type"] = round(100 * m["transactions"] / total, 1)
    return {"by_customer_type": result}


# ---------- 5. Basket & Pricing ----------

def get_basket_stats() -> dict:
    """Average, max, and unit-level basket statistics for the dataset."""
    df = _load()
    return {
        "avg_basket_rm": round(float(df["Total Sales"].mean()), 2),
        "max_basket_rm": round(float(df["Total Sales"].max()), 2),
        "min_basket_rm": round(float(df["Total Sales"].min()), 2),
        "avg_quantity_per_transaction": round(float(df["Quantity"].mean()), 2),
        "avg_unit_price_rm": round(float(df["Unit Price"].mean()), 2),
    }


# Public mapping — what tool_bridge.py registers with Gemini
ALL_TOOLS = {
    "get_total_sales": get_total_sales,
    "get_top_day": get_top_day,
    "get_weekly_summary": get_weekly_summary,
    "get_sales_by_category": get_sales_by_category,
    "get_slowest_category": get_slowest_category,
    "compare_member_vs_visitor": compare_member_vs_visitor,
    "compare_gender": compare_gender,
    "get_payment_mix": get_payment_mix,
    "get_payment_by_customer_type": get_payment_by_customer_type,
    "get_basket_stats": get_basket_stats,
}
