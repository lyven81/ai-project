"""Precompute aggregated views from dataset.csv and emit data.js for the browser demo.

We don't ship all 6,074 raw rows to the browser (~1MB); we ship ~60KB of
pre-aggregated tables that the AI agent's MCP tools query in-browser.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "dataset.csv"
OUT = HERE / "data.js"

rows = []
with SRC.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        r["quantity"] = int(r["quantity"])
        r["unit_cost"] = float(r["unit_cost"])
        r["unit_price"] = float(r["unit_price"])
        r["cost"] = float(r["cost"])
        r["revenue"] = float(r["revenue"])
        rows.append(r)


def days_between(order, delivery):
    from datetime import date
    o = date.fromisoformat(order)
    d = date.fromisoformat(delivery)
    return (d - o).days


SLA = {
    "Supermarket": {True: 1, False: 1},
    "Minimarket": {True: 2, False: 3},
    "Convenience Store": {True: 2, False: 3},
    "Petrol Station": {True: 2, False: 3},
    "Sundry Shop": {True: 3, False: 4},
}
URBAN = {"Petaling", "Klang", "Hulu Langat", "Gombak"}


def classify_delivery(r):
    days = days_between(r["order_date"], r["delivery_date"])
    sla = SLA[r["channel"]][r["district"] in URBAN]
    if days <= sla:
        return "on_time"
    if days <= sla + 3:
        return "slightly_late"
    return "very_late"


# ---- Aggregates ----

by_sku = defaultdict(lambda: {"revenue": 0, "cost": 0, "quantity": 0, "lines": 0})
for r in rows:
    k = (r["sku_id"], r["product_name"], r["category"])
    by_sku[k]["revenue"] += r["revenue"]
    by_sku[k]["cost"] += r["cost"]
    by_sku[k]["quantity"] += r["quantity"]
    by_sku[k]["lines"] += 1

sku_table = [
    {"sku_id": k[0], "product": k[1], "category": k[2],
     "revenue": round(v["revenue"], 2),
     "cost": round(v["cost"], 2),
     "margin_rm": round(v["revenue"] - v["cost"], 2),
     "margin_pct": round((v["revenue"] - v["cost"]) / v["revenue"] * 100, 1),
     "quantity": v["quantity"],
     "lines": v["lines"]}
    for k, v in by_sku.items()
]

by_district = defaultdict(lambda: {"revenue": 0, "cost": 0, "quantity": 0, "orders": 0, "outlets": set(), "deliveries": defaultdict(int)})
for r in rows:
    k = r["district"]
    by_district[k]["revenue"] += r["revenue"]
    by_district[k]["cost"] += r["cost"]
    by_district[k]["quantity"] += r["quantity"]
    by_district[k]["orders"] += 1
    by_district[k]["outlets"].add(r["outlet_id"])
    by_district[k]["deliveries"][classify_delivery(r)] += 1

district_table = []
for d, v in by_district.items():
    total_d = sum(v["deliveries"].values())
    district_table.append({
        "district": d,
        "revenue": round(v["revenue"], 2),
        "cost": round(v["cost"], 2),
        "margin_rm": round(v["revenue"] - v["cost"], 2),
        "quantity": v["quantity"],
        "line_items": v["orders"],
        "outlets": len(v["outlets"]),
        "on_time_pct": round(v["deliveries"]["on_time"] / total_d * 100, 1),
        "slightly_late_pct": round(v["deliveries"]["slightly_late"] / total_d * 100, 1),
        "very_late_pct": round(v["deliveries"]["very_late"] / total_d * 100, 1),
    })

by_channel = defaultdict(lambda: {"revenue": 0, "cost": 0, "quantity": 0, "orders": 0, "outlets": set(), "deliveries": defaultdict(int)})
for r in rows:
    k = r["channel"]
    by_channel[k]["revenue"] += r["revenue"]
    by_channel[k]["cost"] += r["cost"]
    by_channel[k]["quantity"] += r["quantity"]
    by_channel[k]["orders"] += 1
    by_channel[k]["outlets"].add(r["outlet_id"])
    by_channel[k]["deliveries"][classify_delivery(r)] += 1

channel_table = []
for c, v in by_channel.items():
    total_d = sum(v["deliveries"].values())
    channel_table.append({
        "channel": c,
        "revenue": round(v["revenue"], 2),
        "cost": round(v["cost"], 2),
        "margin_rm": round(v["revenue"] - v["cost"], 2),
        "quantity": v["quantity"],
        "line_items": v["orders"],
        "outlets": len(v["outlets"]),
        "revenue_per_outlet": round(v["revenue"] / len(v["outlets"]), 2),
        "on_time_pct": round(v["deliveries"]["on_time"] / total_d * 100, 1),
        "slightly_late_pct": round(v["deliveries"]["slightly_late"] / total_d * 100, 1),
        "very_late_pct": round(v["deliveries"]["very_late"] / total_d * 100, 1),
    })

by_category = defaultdict(lambda: {"revenue": 0, "cost": 0, "quantity": 0, "lines": 0})
for r in rows:
    k = r["category"]
    by_category[k]["revenue"] += r["revenue"]
    by_category[k]["cost"] += r["cost"]
    by_category[k]["quantity"] += r["quantity"]
    by_category[k]["lines"] += 1

category_table = [
    {"category": k, "revenue": round(v["revenue"], 2),
     "cost": round(v["cost"], 2),
     "margin_rm": round(v["revenue"] - v["cost"], 2),
     "margin_pct": round((v["revenue"] - v["cost"]) / v["revenue"] * 100, 1),
     "quantity": v["quantity"],
     "lines": v["lines"]}
    for k, v in by_category.items()
]

by_reseller = defaultdict(lambda: {"revenue": 0, "quantity": 0, "orders": 0, "channel": "", "district": "", "name": "", "deliveries": defaultdict(int)})
for r in rows:
    k = r["outlet_id"]
    by_reseller[k]["revenue"] += r["revenue"]
    by_reseller[k]["quantity"] += r["quantity"]
    by_reseller[k]["orders"] += 1
    by_reseller[k]["channel"] = r["channel"]
    by_reseller[k]["district"] = r["district"]
    by_reseller[k]["name"] = r["outlet_name"]
    by_reseller[k]["deliveries"][classify_delivery(r)] += 1

reseller_table = []
for oid, v in by_reseller.items():
    total_d = sum(v["deliveries"].values())
    reseller_table.append({
        "outlet_id": oid,
        "outlet_name": v["name"],
        "channel": v["channel"],
        "district": v["district"],
        "revenue": round(v["revenue"], 2),
        "quantity": v["quantity"],
        "line_items": v["orders"],
        "on_time_pct": round(v["deliveries"]["on_time"] / total_d * 100, 1),
    })
reseller_table.sort(key=lambda x: x["revenue"], reverse=True)

# District × Channel cross-tab
matrix = defaultdict(lambda: defaultdict(float))
for r in rows:
    matrix[r["district"]][r["channel"]] += r["revenue"]
district_channel_matrix = {d: {c: round(v, 2) for c, v in cs.items()} for d, cs in matrix.items()}

# Category × Channel cross-tab
matrix2 = defaultdict(lambda: defaultdict(float))
for r in rows:
    matrix2[r["category"]][r["channel"]] += r["revenue"]
category_channel_matrix = {cat: {ch: round(v, 2) for ch, v in chs.items()} for cat, chs in matrix2.items()}

# Daily trend
daily = defaultdict(lambda: {"revenue": 0, "quantity": 0, "lines": 0})
for r in rows:
    daily[r["order_date"]]["revenue"] += r["revenue"]
    daily[r["order_date"]]["quantity"] += r["quantity"]
    daily[r["order_date"]]["lines"] += 1
daily_trend = [
    {"date": d, "revenue": round(v["revenue"], 2), "quantity": v["quantity"], "lines": v["lines"]}
    for d, v in sorted(daily.items())
]

# Campaign window: 15-31 Dec vs 1-14 Dec
first_half = sum(r["revenue"] for r in rows if r["order_date"] <= "2025-12-14")
campaign = sum(r["revenue"] for r in rows if r["order_date"] >= "2025-12-15")
total = first_half + campaign
campaign_compare = {
    "first_half_revenue": round(first_half, 2),
    "first_half_lines": sum(1 for r in rows if r["order_date"] <= "2025-12-14"),
    "campaign_revenue": round(campaign, 2),
    "campaign_lines": sum(1 for r in rows if r["order_date"] >= "2025-12-15"),
    "campaign_share_pct": round(campaign / total * 100, 1),
    "first_half_share_pct": round(first_half / total * 100, 1),
    "uplift_pct": round((campaign / 17 - first_half / 14) / (first_half / 14) * 100, 1),  # daily average uplift
}

# At-risk accounts: below channel average revenue
channel_avg = {c["channel"]: c["revenue"] / c["outlets"] for c in channel_table}
at_risk = [
    {**r, "channel_avg": round(channel_avg[r["channel"]], 2),
     "gap_pct": round((r["revenue"] - channel_avg[r["channel"]]) / channel_avg[r["channel"]] * 100, 1)}
    for r in reseller_table
    if r["revenue"] < channel_avg[r["channel"]] * 0.5  # below 50% of channel avg
]
at_risk.sort(key=lambda x: x["revenue"])

# Top 150-row sample for data preview
sample_150 = rows[:150]

data = {
    "meta": {
        "total_rows": len(rows),
        "total_revenue": round(sum(r["revenue"] for r in rows), 2),
        "total_cost": round(sum(r["cost"] for r in rows), 2),
        "total_margin_rm": round(sum(r["revenue"] - r["cost"] for r in rows), 2),
        "total_outlets": len({r["outlet_id"] for r in rows}),
        "total_skus": len({r["sku_id"] for r in rows}),
        "period": "2025-12-01 to 2025-12-31",
    },
    "sku": sorted(sku_table, key=lambda x: x["revenue"], reverse=True),
    "district": sorted(district_table, key=lambda x: x["revenue"], reverse=True),
    "channel": sorted(channel_table, key=lambda x: x["revenue"], reverse=True),
    "category": sorted(category_table, key=lambda x: x["revenue"], reverse=True),
    "reseller": reseller_table,
    "district_channel_matrix": district_channel_matrix,
    "category_channel_matrix": category_channel_matrix,
    "daily_trend": daily_trend,
    "campaign_compare": campaign_compare,
    "at_risk_accounts": at_risk,
    "sample_150": sample_150,
}

content = "// Auto-generated by precompute.py — do not edit by hand\n"
content += "window.HOOTIM_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n"
OUT.write_text(content, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")
print(f"Total rows: {data['meta']['total_rows']}")
print(f"Total revenue: RM {data['meta']['total_revenue']:,.0f}")
print(f"Campaign (15-31 Dec) share: {data['campaign_compare']['campaign_share_pct']}%")
print(f"Daily uplift: {data['campaign_compare']['uplift_pct']}%")
