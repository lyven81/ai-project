"""Custom data-reading tool for the Researcher agent.

Reads the bookshelf sales dataset (xlsx) and computes the metrics the
Portfolio Analyst will reason over. The tool returns structured JSON so the
Forensic Judge can validate it deterministically.
"""

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


def resolve_dataset_path(explicit: str | None = None) -> str:
    """Find the dataset file using a priority chain:

    1. explicit argument
    2. BOOKSHELF_DATASET_PATH env var
    3. /app/dataset/dataset.xlsx (Cloud Run bundled location)
    4. <project-root>/dataset/dataset.xlsx (local dev — walk up from this file)
    5. <project-root>/dataset/dataset-sample-150.csv (fallback CSV)

    Returns the first path that exists. Raises FileNotFoundError otherwise.
    """
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("BOOKSHELF_DATASET_PATH")
    if env:
        candidates.append(Path(env))
    candidates.append(Path("/app/dataset/dataset.xlsx"))

    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "dataset").exists():
            candidates.append(parent / "dataset" / "dataset.xlsx")
            candidates.append(parent / "dataset" / "dataset-sample-150.csv")
            break

    for c in candidates:
        if c.exists():
            return str(c)

    raise FileNotFoundError(
        f"No dataset found. Tried: {[str(c) for c in candidates]}"
    )


def analyse_sales_data(dataset_path: str | None = None) -> dict[str, Any]:
    """Read a sales dataset and return per-SKU + per-category + seasonal metrics.

    The dataset must match the Bookshelf schema (17 columns including OrderNo,
    OrderQuantity, ItemCost, ItemPrice, OrderDate, ProductCategory, Product,
    Brand, SalesChannel, etc.).

    Returns a dict with keys:
        - sku_metrics: list of dicts, one per SKU
        - category_metrics: list of dicts, one per ProductCategory
        - subcategory_metrics: list of dicts, one per ProductSubcategory
        - seasonal_indices: dict mapping subcategory -> 12-month revenue index
        - channel_breakdown: dict mapping (category, channel) -> revenue
        - data_quality: dict of completeness + impossibility checks
        - meta: shape, date range, totals
    """
    try:
        resolved = resolve_dataset_path(dataset_path)
    except FileNotFoundError as e:
        return {"error": str(e)}
    path = Path(resolved)

    if path.suffix == ".xlsx":
        try:
            df = pd.read_excel(path, sheet_name="Sales")
        except (ValueError, KeyError):
            df = pd.read_excel(path, sheet_name=0)
    else:
        df = pd.read_csv(path)
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df["Revenue"] = df["OrderQuantity"] * df["ItemPrice"]
    df["Profit"] = (df["ItemPrice"] - df["ItemCost"]) * df["OrderQuantity"]
    df["Month"] = df["OrderDate"].dt.month
    df["YearMonth"] = df["OrderDate"].dt.to_period("M").astype(str)

    months_span = max(1, ((df["OrderDate"].max() - df["OrderDate"].min()).days // 30) or 1)

    # ------------------------------------------------------------------ per-SKU
    # Group by Product only — using more columns as keys would drop rows with
    # missing Brand/Language. We pull category/subcategory/brand/language as
    # the most-common value per SKU below.
    sku_agg = df.groupby("Product", dropna=False).agg(
        revenue=("Revenue", "sum"),
        profit=("Profit", "sum"),
        units_sold=("OrderQuantity", "sum"),
        item_price_avg=("ItemPrice", "mean"),
        item_cost_avg=("ItemCost", "mean"),
        order_count=("OrderNo", "nunique"),
    ).reset_index()

    # Pull the dominant category/subcategory/brand/language per SKU
    def _mode(series):
        m = series.dropna().mode()
        return m.iloc[0] if not m.empty else None

    descriptors = df.groupby("Product").agg(
        ProductCategory=("ProductCategory", _mode),
        ProductSubcategory=("ProductSubcategory", _mode),
        Brand=("Brand", _mode),
        Language=("Language", _mode),
    ).reset_index()
    sku_agg = sku_agg.merge(descriptors, on="Product", how="left")
    sku_agg["margin_pct"] = (sku_agg["profit"] / sku_agg["revenue"]).fillna(0).round(3)
    sku_agg["velocity_units_per_month"] = (sku_agg["units_sold"] / months_span).round(2)

    last_sale = df.groupby("Product")["OrderDate"].max().reset_index()
    last_sale.columns = ["Product", "_last_sale_dt"]
    sku_agg = sku_agg.merge(last_sale, on="Product", how="left")
    data_max_date = df["OrderDate"].max()
    sku_agg["days_since_last_sale"] = (data_max_date - sku_agg["_last_sale_dt"]).dt.days.astype(int)
    sku_agg["last_sale_date"] = sku_agg["_last_sale_dt"].dt.strftime("%Y-%m-%d")

    def _aging_class(days: int) -> str:
        if days <= 30:
            return "fresh"
        if days <= 90:
            return "slowing"
        if days <= 180:
            return "stale"
        return "stuck"

    sku_agg["aging_class"] = sku_agg["days_since_last_sale"].apply(_aging_class)
    sku_agg = sku_agg.drop(columns=["_last_sale_dt"])

    sku_agg = sku_agg.sort_values("revenue", ascending=False).reset_index(drop=True)
    sku_agg["pareto_rank"] = sku_agg.index + 1
    total_rev = sku_agg["revenue"].sum()
    sku_agg["revenue_share_pct"] = (sku_agg["revenue"] / total_rev * 100).round(2)
    sku_agg["cumulative_share_pct"] = sku_agg["revenue_share_pct"].cumsum().round(2)

    # Top channel + top city per SKU (compact - just label + share)
    sku_channel = df.groupby(["Product", "SalesChannel"])["Revenue"].sum().reset_index()
    top_channel = sku_channel.sort_values("Revenue", ascending=False).groupby("Product").head(1)
    top_channel = top_channel.rename(columns={"SalesChannel": "top_channel", "Revenue": "_tcr"})[["Product", "top_channel"]]
    sku_agg = sku_agg.merge(top_channel, on="Product", how="left")

    # Round numeric columns for compactness
    for col in ["revenue", "profit", "item_price_avg", "item_cost_avg"]:
        sku_agg[col] = sku_agg[col].round(2)

    sku_metrics = sku_agg.to_dict(orient="records")

    # -------------------------------------------------------------- per-Category
    cat_grouped = df.groupby("ProductCategory")
    cat_agg = cat_grouped.agg(
        revenue=("Revenue", "sum"),
        profit=("Profit", "sum"),
        units_sold=("OrderQuantity", "sum"),
        order_count=("OrderNo", "nunique"),
        sku_count=("Product", "nunique"),
    ).reset_index()
    cat_agg["margin_pct"] = (cat_agg["profit"] / cat_agg["revenue"]).fillna(0).round(3)
    cat_agg["revenue_share_pct"] = (cat_agg["revenue"] / total_rev * 100).round(2)
    for col in ["revenue", "profit"]:
        cat_agg[col] = cat_agg[col].round(2)
    category_metrics = cat_agg.to_dict(orient="records")

    # --------------------------------------------------------- per-Subcategory
    sub_agg = df.groupby(["ProductCategory", "ProductSubcategory"]).agg(
        revenue=("Revenue", "sum"),
        units_sold=("OrderQuantity", "sum"),
        sku_count=("Product", "nunique"),
    ).reset_index()
    sub_agg["revenue"] = sub_agg["revenue"].round(2)
    subcategory_metrics = sub_agg.sort_values("revenue", ascending=False).to_dict(orient="records")

    # --------------------------------------------------- seasonal indices (per subcat)
    sub_month = df.groupby(["ProductSubcategory", "Month"])["Revenue"].sum().reset_index()
    seasonal_indices = {}
    for subcat, grp in sub_month.groupby("ProductSubcategory"):
        monthly = {int(row["Month"]): round(row["Revenue"], 2) for _, row in grp.iterrows()}
        # Fill missing months with 0
        full_year = {m: monthly.get(m, 0.0) for m in range(1, 13)}
        avg = sum(full_year.values()) / 12 or 1.0
        index = {m: round(v / avg, 2) for m, v in full_year.items()}
        seasonal_indices[subcat] = index

    # ---------------------------------------------------- channel breakdown
    channel_rev = df.groupby(["ProductCategory", "SalesChannel"])["Revenue"].sum().reset_index()
    channel_breakdown = []
    for cat, grp in channel_rev.groupby("ProductCategory"):
        cat_total = grp["Revenue"].sum() or 1.0
        for _, row in grp.iterrows():
            channel_breakdown.append({
                "category": cat,
                "channel": row["SalesChannel"],
                "revenue": round(row["Revenue"], 2),
                "share_pct": round(row["Revenue"] / cat_total * 100, 1),
            })

    # ------------------------------------------------------- data quality
    data_quality = {
        "total_rows": int(len(df)),
        "missing_customer_city": int(df["CustomerCity"].isna().sum()),
        "missing_brand": int(df["Brand"].isna().sum()),
        "zero_quantity_rows": int((df["OrderQuantity"] == 0).sum()),
        "negative_price_rows": int((df["ItemPrice"] < 0).sum()),
        "duplicate_order_lines": int(df.duplicated(subset=["OrderNo", "Product"]).sum()),
    }

    # ------------------------------------------------------------------ meta
    meta = {
        "row_count": int(len(df)),
        "unique_skus": int(df["Product"].nunique()),
        "unique_orders": int(df["OrderNo"].nunique()),
        "date_min": df["OrderDate"].min().strftime("%Y-%m-%d"),
        "date_max": df["OrderDate"].max().strftime("%Y-%m-%d"),
        "months_span": int(months_span),
        "total_revenue": round(total_rev, 2),
        "total_profit": round(df["Profit"].sum(), 2),
    }

    return {
        "meta": meta,
        "sku_metrics": sku_metrics,
        "category_metrics": category_metrics,
        "subcategory_metrics": subcategory_metrics,
        "seasonal_indices": seasonal_indices,
        "channel_breakdown": channel_breakdown,
        "data_quality": data_quality,
    }


def analyse_sales_data_summary(dataset_path: str | None = None, top_n: int = 30) -> str:
    """Return the analysis as a JSON string, with the SKU list trimmed to top_n + bottom_n + aging slice.

    Sending all 385 SKUs would blow the LLM context. We keep:
      - top_n by revenue (Pareto winners)
      - bottom_n by revenue (dead-stock candidates)
      - all SKUs with aging_class in {"slowing", "stale", "stuck"} (aging signal)
    Deduplicated by Product name.
    """
    full = analyse_sales_data(dataset_path)
    if "error" in full:
        return json.dumps(full)

    skus = full["sku_metrics"]
    if len(skus) > top_n * 2:
        kept: list[dict] = []
        seen: set[str] = set()
        for s in skus[:top_n] + skus[-top_n:]:
            if s["Product"] not in seen:
                kept.append(s)
                seen.add(s["Product"])
        for s in skus:
            if s.get("aging_class") in ("slowing", "stale", "stuck") and s["Product"] not in seen:
                kept.append(s)
                seen.add(s["Product"])
        full["sku_metrics"] = kept
        full["meta"]["sku_list_trimmed"] = True
        full["meta"]["sku_list_kept"] = len(kept)
    else:
        full["meta"]["sku_list_trimmed"] = False

    return json.dumps(full, ensure_ascii=False)
