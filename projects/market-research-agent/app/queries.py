"""
queries.py — the 10 approved, parameterized queries (the governance layer).

This is the heart of the design: the agent NEVER writes SQL. It may only call one of
these 10 named tools with whitelisted parameters. Each SQL string is fixed; only bound
parameters (?) vary. 6 are pure local SQL (~0 cost); 4 read the cached-Maps tables
(free per call, Maps billed only on the scheduled refresh). No live Maps call here.

Run standalone to smoke-test every query against market_research.db:
    python app/queries.py
"""
import os, sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "market_research.db")

# default parameters for the tong shui / Klang Valley pack
BUSINESS = "tong shui"
SS2, KEPONG = "47300", "52100"

def _conn():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def _rows(sql, params=()):
    con = _conn()
    try:
        return [dict(r) for r in con.execute(sql, params).fetchall()]
    finally:
        con.close()

# ---------- Q1  Where: highest foot traffic by daypart  (SQL) ----------
def q1_top_foot_traffic(limit=5):
    sql = """
        SELECT d.neighborhood, ft.time_of_day, ft.foot_traffic_score
        FROM foot_traffic ft
        JOIN demographics d ON d.zip_code = ft.zip_code
        ORDER BY ft.foot_traffic_score DESC
        LIMIT ?"""
    return _rows(sql, (limit,))

# ---------- Q2  Who: resident-profile fit score  (SQL) ----------
def q2_resident_fit(limit=5):
    # proxy blend: population scale + Chinese share + youthfulness (no income column)
    sql = """
        SELECT neighborhood, total_population, median_age,
               chinese_population_pct,
               ROUND(
                 (total_population * 1.0 / (SELECT MAX(total_population) FROM demographics)) * 40
               + (chinese_population_pct / 100.0) * 40
               + ((40 - ABS(median_age - 32)) / 40.0) * 20, 1) AS fit_score
        FROM demographics
        ORDER BY fit_score DESC
        LIMIT ?"""
    return _rows(sql, (limit,))

# ---------- Q3  Where+Competition: high traffic, few competitors  (cached) ----------
def q3_opportunity_gap(business_type=BUSINESS, min_evening_traffic=50, limit=5):
    sql = """
        SELECT d.neighborhood, d.zip_code,
               ft.foot_traffic_score AS evening_traffic,
               COUNT(c.competitor_id) AS shop_count,
               ROUND(ft.foot_traffic_score * 1.0 / (COUNT(c.competitor_id) + 1), 1) AS opportunity_ratio
        FROM demographics d
        JOIN foot_traffic ft
          ON ft.zip_code = d.zip_code AND ft.time_of_day = 'evening'
        LEFT JOIN competitors c
          ON c.zip_code = d.zip_code AND c.business_type = ?
        GROUP BY d.zip_code
        HAVING evening_traffic >= ?
        ORDER BY opportunity_ratio DESC
        LIMIT ?"""
    return _rows(sql, (business_type, min_evening_traffic, limit))

# ---------- Q4  Competition: saturation in one area  (cached) ----------
def q4_saturation(zip_code=SS2, business_type=BUSINESS):
    sql = """
        SELECT COUNT(*) AS shop_count, ROUND(AVG(rating), 2) AS avg_rating
        FROM competitors
        WHERE zip_code = ? AND business_type = ?"""
    return _rows(sql, (zip_code, business_type))

# ---------- Q5  Price: competitor price range for a bowl  (SQL) ----------
def q5_price_range():
    sql = """
        SELECT ROUND(MIN(price),2) AS low,
               ROUND(AVG(price),2) AS avg,
               ROUND(MAX(price),2) AS high,
               COUNT(*) AS n
        FROM competitor_prices"""
    return _rows(sql)

# ---------- Q6  Price: unoccupied price band  (SQL + light post-processing) ----------
def q6_price_gap():
    # fixed query returns occupancy per RM1 band; python flags the sparsest interior band
    bands = _rows("""
        SELECT CAST(price AS INTEGER) AS band, COUNT(*) AS n
        FROM competitor_prices
        GROUP BY band ORDER BY band""")
    if not bands:
        return {"gap_low": None, "gap_high": None, "bands": []}
    lo, hi = bands[0]["band"], bands[-1]["band"]
    occ = {b["band"]: b["n"] for b in bands}
    sparsest, sparse_n = None, None
    for b in range(lo + 1, hi):  # interior bands only
        n = occ.get(b, 0)
        if sparse_n is None or n < sparse_n:
            sparse_n, sparsest = n, b
    return {"gap_low": sparsest + 0.5, "gap_high": sparsest + 1.5,
            "gap_count": sparse_n, "bands": bands}

# ---------- Q7  Economics: revenue forecast next quarter  (SQL + projection) ----------
def q7_revenue_forecast(weeks_ahead=13):
    weekly = _rows("""
        SELECT week_start_date, ROUND(SUM(total_revenue),2) AS weekly_rev
        FROM sales_history_weekly
        GROUP BY week_start_date ORDER BY week_start_date""")
    if len(weekly) < 4:
        return {"projection": None, "weekly": weekly}
    y = [w["weekly_rev"] for w in weekly]
    n = len(y); xs = list(range(n))
    mx, my = sum(xs)/n, sum(y)/n
    denom = sum((x-mx)**2 for x in xs) or 1
    slope = sum((xs[i]-mx)*(y[i]-my) for i in range(n)) / denom
    intercept = my - slope*mx
    proj = sum(intercept + slope*(n+k) for k in range(weeks_ahead))
    return {"projection": round(proj, 2), "weeks_ahead": weeks_ahead,
            "recent_weekly_avg": round(my, 2), "slope_per_week": round(slope, 2)}

# ---------- Q8  Demand: bestseller + growth/decline  (SQL) ----------
def q8_product_trend(midpoint="2025-10-06"):
    sql = """
        SELECT product_type,
               SUM(quantity_sold) AS total_qty,
               ROUND(SUM(total_revenue),2) AS total_rev,
               SUM(CASE WHEN week_start_date >= ? THEN quantity_sold ELSE 0 END) AS recent_qty,
               SUM(CASE WHEN week_start_date <  ? THEN quantity_sold ELSE 0 END) AS older_qty
        FROM sales_history_weekly
        GROUP BY product_type
        ORDER BY total_rev DESC"""
    rows = _rows(sql, (midpoint, midpoint))
    for r in rows:
        older = r["older_qty"] or 1
        r["growth_pct"] = round((r["recent_qty"] - older) / older * 100, 1)
    return rows

# ---------- Q9  Differentiation: top competitor complaints  (cached) ----------
def q9_top_complaints(max_rating=3, limit=3):
    sql = """
        SELECT theme, COUNT(*) AS mentions
        FROM competitor_reviews
        WHERE rating <= ?
        GROUP BY theme ORDER BY mentions DESC
        LIMIT ?"""
    return _rows(sql, (max_rating, limit))

# ---------- Q10 Go/No-go: launch synthesis for one area  (multi, cached) ----------
def q10_launch_decision(zip_code=KEPONG, business_type=BUSINESS):
    area = _rows("SELECT neighborhood, chinese_population_pct, total_population "
                 "FROM demographics WHERE zip_code = ?", (zip_code,))
    evening = _rows("SELECT foot_traffic_score FROM foot_traffic "
                    "WHERE zip_code = ? AND time_of_day = 'evening'", (zip_code,))
    sat = q4_saturation(zip_code, business_type)
    return {
        "area": area[0] if area else None,
        "evening_traffic": evening[0]["foot_traffic_score"] if evening else None,
        "saturation": sat[0] if sat else None,
        "price_gap": q6_price_gap(),
        "top_product": q8_product_trend()[0],
        "top_complaint": (q9_top_complaints(limit=1) or [None])[0],
    }

# registry: id -> (callable, title, source, cost)
REGISTRY = {
    1:  (q1_top_foot_traffic, "Highest foot traffic by daypart", "foot_traffic", "sql"),
    2:  (q2_resident_fit,     "Resident profile fit",           "demographics", "sql"),
    3:  (q3_opportunity_gap,  "High traffic, few competitors",  "foot_traffic + competitors", "cached"),
    4:  (q4_saturation,       "Saturation in an area",          "competitors", "cached"),
    5:  (q5_price_range,      "Competitor price range",         "competitor_prices", "sql"),
    6:  (q6_price_gap,        "Unoccupied price band",          "competitor_prices", "sql"),
    7:  (q7_revenue_forecast, "Revenue forecast",               "sales_history_weekly", "sql"),
    8:  (q8_product_trend,    "Bestseller and trend",           "sales_history_weekly", "sql"),
    9:  (q9_top_complaints,   "Top competitor complaints",      "competitor_reviews", "cached"),
    10: (q10_launch_decision, "Launch go / no-go",              "multiple", "multi"),
}

if __name__ == "__main__":
    import json
    for qid, (fn, title, src, cost) in REGISTRY.items():
        print(f"\n=== Q{qid} [{cost}] {title}  ({src}) ===")
        print(json.dumps(fn(), indent=2, ensure_ascii=False)[:600])
