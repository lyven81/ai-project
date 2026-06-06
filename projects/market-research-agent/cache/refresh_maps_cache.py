"""
refresh_maps_cache.py — fill the 3 cached-Maps tables from Google Maps Places.

This is the ONLY place Google Maps is ever billed. It runs on a schedule (Cloud
Scheduler / cron), not per user question. After it writes the CSVs, rebuild the DB.

It populates:
  competitors.csv         (Places Text Search per area + business keyword)
  competitor_reviews.csv  (Place Details reviews; theme tagged)
  suppliers.csv           (Places Text Search for supplier keywords)

Cost controls baked in:
  - field masking (X-Goog-FieldMask) so we pay only for fields we use
  - one scheduled run, results cached; user queries never hit this
  - limit on results per area

Requires:  pip install requests   and   MAPS_API_KEY in the environment (.env)
Run:       python cache/refresh_maps_cache.py            (live)
           python cache/refresh_maps_cache.py --dry-run  (prints plan, no API calls)
"""
import csv, os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
API_KEY = os.getenv("MAPS_API_KEY", "")

# areas to search (zip -> (display name, lat, lng)); keep in sync with the data pack
AREAS = {
    "47300": ("SS2 Petaling Jaya", 3.1180, 101.6230),
    "56000": ("Cheras", 3.0830, 101.7430),
    "52100": ("Kepong", 3.2150, 101.6360),
    "53000": ("Setapak", 3.2010, 101.7000),
    "55100": ("Pudu", 3.1340, 101.7110),
    "58100": ("Old Klang Road", 3.0940, 101.6790),
    "59100": ("Bangsar", 3.1290, 101.6710),
    "40000": ("Shah Alam Seksyen 13", 3.0720, 101.5180),
}
BUSINESS_KEYWORD = "tong shui dessert"
SUPPLIER_KEYWORDS = ["wholesale dessert ingredients", "pasar borong"]
MAX_PER_AREA = 20

PLACES_SEARCH = "https://places.googleapis.com/v1/places:searchText"
COMPLAINT_HINTS = {  # very light keyword tagging; swap for a cheap-model pass if wanted
    "too sweet / inconsistent": ["sweet", "inconsistent", "different"],
    "slow service": ["slow", "wait", "queue"],
    "parking / seating": ["parking", "seat", "cramped", "crowded"],
    "portion size": ["portion", "small", "little"],
}

def tag_theme(text):
    t = text.lower()
    for theme, hints in COMPLAINT_HINTS.items():
        if any(h in t for h in hints):
            return theme
    return "general"

def search_places(query, lat, lng):
    import requests
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        # field mask = pay only for what we use
        "X-Goog-FieldMask": ("places.id,places.displayName,places.location,"
                             "places.rating,places.userRatingCount,places.reviews"),
    }
    body = {"textQuery": query,
            "locationBias": {"circle": {"center": {"latitude": lat, "longitude": lng},
                                         "radius": 2500.0}},
            "maxResultCount": MAX_PER_AREA}
    r = requests.post(PLACES_SEARCH, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    return r.json().get("places", [])

def write_csv(name, header, rows):
    with open(os.path.join(DATA, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f"  wrote {name} ({len(rows)} rows)")

def main(dry_run=False):
    if dry_run:
        print("DRY RUN — would call Places Text Search for:")
        for z, (nm, *_ ) in AREAS.items():
            print(f"  [{z}] '{BUSINESS_KEYWORD}' near {nm}")
        print("  suppliers:", SUPPLIER_KEYWORDS)
        print("No API calls made. Set MAPS_API_KEY and drop --dry-run to refresh.")
        return
    if not API_KEY:
        sys.exit("MAPS_API_KEY not set. Add it to .env or the environment.")

    comp_rows, rev_rows, sup_rows = [], [], []
    cid = rid = 1
    for z, (nm, lat, lng) in AREAS.items():
        for p in search_places(BUSINESS_KEYWORD, lat, lng):
            loc = p.get("location", {})
            comp_rows.append([cid, p.get("displayName", {}).get("text", ""), "tong shui", z,
                              loc.get("latitude"), loc.get("longitude"),
                              p.get("rating"), p.get("userRatingCount")])
            for rv in (p.get("reviews") or []):
                txt = (rv.get("text", {}) or {}).get("text", "")
                rev_rows.append([rid, cid, rv.get("rating"), txt.replace("\n", " "),
                                 tag_theme(txt)])
                rid += 1
            cid += 1
    sid = 1
    for kw in SUPPLIER_KEYWORDS:
        for z, (nm, lat, lng) in AREAS.items():
            for p in search_places(kw, lat, lng)[:2]:
                loc = p.get("location", {})
                sup_rows.append([sid, p.get("displayName", {}).get("text", ""), z,
                                 loc.get("latitude"), loc.get("longitude")])
                sid += 1

    write_csv("competitors.csv",
              ["competitor_id","name","business_type","zip_code","lat","lng","rating","review_count"], comp_rows)
    write_csv("competitor_reviews.csv",
              ["review_id","competitor_id","rating","review_text","theme"], rev_rows)
    write_csv("suppliers.csv", ["supplier_id","name","zip_code","lat","lng"], sup_rows)
    print("\nCache refreshed. Now rebuild the DB:  python setup/build_db.py")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    main(ap.parse_args().dry_run)
