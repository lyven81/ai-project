"""
generate_data.py — builds the Klang Valley tong shui data pack (7 CSV tables).

Mirrors the codelab's data/ folder, adapted to our no-ADK governed design:
  4 data tables  : demographics, foot_traffic, competitor_prices, sales_history_weekly
  3 cached tables: competitors, competitor_reviews, suppliers  (normally filled from
                   Google Maps by cache/refresh_maps_cache.py; seeded here so the demo
                   runs offline at zero cost)

Deterministic (seeded) so the build is reproducible. Stdlib only.
"""
import csv, os, random
from datetime import date, timedelta

random.seed(42)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)

def write_csv(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {name:28s} {len(rows):4d} rows")

# ---- area master (Klang Valley, Chinese-dense supper districts) ----
# zip, city, neighborhood, population, median_age, degree_pct, chinese_pct, evening_ft, shop_count, lat, lng
AREAS = [
    ("47300", "Petaling Jaya", "SS2",            38000, 34.0, 52.0, 64.0, 95, 17, 3.1180, 101.6230),
    ("56000", "Kuala Lumpur",  "Cheras",         61000, 33.0, 41.0, 72.0, 88, 12, 3.0830, 101.7430),
    ("52100", "Kuala Lumpur",  "Kepong",         54000, 35.0, 39.0, 78.0, 80,  4, 3.2150, 101.6360),
    ("53000", "Kuala Lumpur",  "Setapak",        47000, 32.0, 43.0, 58.0, 72,  8, 3.2010, 101.7000),
    ("55100", "Kuala Lumpur",  "Pudu",           33000, 38.0, 37.0, 68.0, 68,  9, 3.1340, 101.7110),
    ("58100", "Kuala Lumpur",  "Old Klang Road", 42000, 36.0, 45.0, 66.0, 64,  7, 3.0940, 101.6790),
    ("59100", "Kuala Lumpur",  "Bangsar",        28000, 39.0, 71.0, 40.0, 60, 10, 3.1290, 101.6710),
    ("40000", "Shah Alam",     "Seksyen 13",     51000, 31.0, 48.0, 30.0, 55,  6, 3.0720, 101.5180),
]

# ---- 1. demographics (with optional chinese_population_pct for tong shui) ----
demo_rows = []
for z, city, hood, pop, age, deg, cn, ev, *_ in AREAS:
    ft_index = round(ev * 0.85 + random.uniform(-3, 3), 1)
    demo_rows.append([z, city, hood, pop, age, deg, ft_index, cn])
write_csv("demographics.csv",
          ["zip_code","city","neighborhood","total_population","median_age",
           "bachelors_degree_pct","foot_traffic_index","chinese_population_pct"],
          demo_rows)

# ---- 2. foot_traffic (evening peak for tong shui) ----
ft_rows = []
for z, *_rest in AREAS:
    ev = _rest[6]  # evening_ft
    morning   = round(ev * random.uniform(0.34, 0.44), 1)
    afternoon = round(ev * random.uniform(0.58, 0.70), 1)
    evening   = round(ev + random.uniform(-1.5, 1.5), 1)
    ft_rows += [[z, "morning", morning], [z, "afternoon", afternoon], [z, "evening", evening]]
write_csv("foot_traffic.csv", ["zip_code","time_of_day","foot_traffic_score"], ft_rows)

# ---- 3. competitor_prices (region-level; cluster ~RM5.50, gap RM6.50-7.50) ----
PRODUCTS = ["cheng tng","tau fu fa","bubur cha cha","red bean soup","green bean soup",
            "black glutinous rice","leng chee kang","mango pomelo sago","sea coconut",
            "ginger sweet potato soup"]
STORES = ["Sweet Bowl Dessert","Ah Mei Tong Sui","Madam Tang Dessert","Cheng Tng Corner",
          "Old Town Sweet Soup","Nyonya Dessert House","Honey Dew Tong Sui","Sago Story",
          "Bean & Bowl","Night Market Desserts","Heritage Tong Sui","Cooling House"]
def gap_price():
    # mostly RM3.50-6.00, some premium RM8.00-9.00; avoid the RM6.50-7.50 gap band
    if random.random() < 0.75:
        return round(random.uniform(3.5, 6.0), 2)
    return round(random.uniform(8.0, 9.0), 2)
price_rows = []
for store in STORES:
    for prod in random.sample(PRODUCTS, random.randint(5, 8)):
        price_rows.append([store, prod, gap_price(), "Klang Valley", "False"])
write_csv("competitor_prices.csv",
          ["store_name","product_type","price","region","is_organic"], price_rows)

# ---- 4. sales_history_weekly (26 wks, upward trend; sago grows, green bean declines) ----
# per-product weekly growth slope (small). Default ~+0.2%/wk; specific products overridden.
GROWTH = {p: 0.002 for p in PRODUCTS}
GROWTH.update({"mango pomelo sago": 0.012, "tau fu fa": 0.005, "red bean soup": 0.000,
               "green bean soup": -0.004, "cheng tng": 0.003})
BASE_QTY = {"mango pomelo sago": 140, "tau fu fa": 120, "red bean soup": 110,
            "green bean soup": 95, "cheng tng": 105}
OWN_PRICE = {"cheng tng":5.5,"tau fu fa":5.0,"bubur cha cha":6.0,"red bean soup":4.5,
             "green bean soup":4.5,"black glutinous rice":5.5,"leng chee kang":6.0,
             "mango pomelo sago":7.5,"sea coconut":5.0,"ginger sweet potato soup":4.5}
sales_rows = []
start = date(2025, 7, 7)  # a Monday
for store in ["SS2 Flagship","Kepong Branch"]:
    for w in range(26):
        wk = (start + timedelta(weeks=w)).isoformat()
        for prod in PRODUCTS:
            base = BASE_QTY.get(prod, 70)
            g = GROWTH.get(prod, 0.001)
            seasonal = 1.0 + 0.06 * (1 if "soup" not in prod else -0.5)  # mild
            qty = int(base * (1 + g) ** w * seasonal * random.uniform(0.9, 1.1))
            if store == "Kepong Branch":
                qty = int(qty * 0.7)
            rev = round(qty * OWN_PRICE[prod], 2)
            sales_rows.append([wk, store, prod, qty, rev])
write_csv("sales_history_weekly.csv",
          ["week_start_date","store_location","product_type","quantity_sold","total_revenue"],
          sales_rows)

# ---- 5. competitors (cached Maps Places result) ----
comp_rows, comp_id = [], 1
NAME_POOL = STORES + ["Tong Sui Master","Sweet Memory","Dessert Lane","Bowl of Comfort",
                      "Grandma's Sweet Soup","Cool Dessert Co","Sugar & Spice Tong Sui"]
comp_index = {}  # zip -> list of competitor_ids (for reviews)
for z, city, hood, pop, age, deg, cn, ev, count, lat, lng in AREAS:
    ids = []
    for _ in range(count):
        nm = random.choice(NAME_POOL) + f" ({hood})"
        rating = round(random.uniform(3.7, 4.7), 1)
        reviews = random.randint(35, 620)
        jlat = round(lat + random.uniform(-0.012, 0.012), 6)
        jlng = round(lng + random.uniform(-0.012, 0.012), 6)
        comp_rows.append([comp_id, nm, "tong shui", z, jlat, jlng, rating, reviews])
        ids.append((comp_id, rating)); comp_id += 1
    comp_index[z] = ids
write_csv("competitors.csv",
          ["competitor_id","name","business_type","zip_code","lat","lng","rating","review_count"],
          comp_rows)

# ---- 6. competitor_reviews (cached; themes tagged, weighted to top complaints) ----
NEG_THEMES = [("too sweet / inconsistent", 0.42), ("slow service", 0.30),
              ("parking / seating", 0.16), ("portion size", 0.12)]
POS_THEMES = [("great taste", 0.4), ("good value", 0.35), ("fresh ingredients", 0.25)]
NEG_TEXT = {
    "too sweet / inconsistent": "Too sweet for me, and it tasted different from last time.",
    "slow service": "Waited almost 20 minutes during the supper crowd.",
    "parking / seating": "No parking nearby and seating is very cramped.",
    "portion size": "Portion felt small for the price.",
}
POS_TEXT = {
    "great taste": "Best mango pomelo sago in the area, came back twice.",
    "good value": "Generous bowl and reasonable price.",
    "fresh ingredients": "Ingredients taste fresh, not from a can.",
}
def weighted(themes):
    r, acc = random.random(), 0.0
    for t, w in themes:
        acc += w
        if r <= acc: return t
    return themes[-1][0]
rev_rows, rev_id = [], 1
for z, ids in comp_index.items():
    for cid, crating in ids:
        for _ in range(random.randint(2, 6)):
            if random.random() < 0.55:  # skew to negative so complaints are findable
                theme = weighted(NEG_THEMES); rating = random.randint(2, 3); text = NEG_TEXT[theme]
            else:
                theme = weighted(POS_THEMES); rating = random.randint(4, 5); text = POS_TEXT[theme]
            rev_rows.append([rev_id, cid, rating, text, theme]); rev_id += 1
write_csv("competitor_reviews.csv",
          ["review_id","competitor_id","rating","review_text","theme"], rev_rows)

# ---- 7. suppliers (cached Maps Places result) ----
sup_rows = [
    [1, "Pasar Borong Selangor (wholesale)", "52100", 3.2080, 101.6300],
    [2, "Dessert Ingredient Wholesaler KL",  "55100", 3.1360, 101.7090],
    [3, "Sago & Bean Supply Co",             "58100", 3.0960, 101.6770],
    [4, "Coconut & Gula Melaka Trader",      "56000", 3.0850, 101.7400],
]
write_csv("suppliers.csv", ["supplier_id","name","zip_code","lat","lng"], sup_rows)

print("\nData pack generated in:", os.path.normpath(DATA))
