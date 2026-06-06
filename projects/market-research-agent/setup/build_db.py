"""
build_db.py — load the 7 CSV tables in data/ into a single SQLite file.

The codelab provisions BigQuery; our governed/cost-minimized design uses a single
committed SQLite file (market_research.db) so the agent runs locally or on Cloud Run
with no warehouse and no per-query cost. Stdlib only.
"""
import csv, os, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
DB   = os.path.join(HERE, "..", "market_research.db")

# table_name -> (csv_file, [(column, sql_type), ...])
SCHEMA = {
    "demographics": ("demographics.csv", [
        ("zip_code","TEXT"),("city","TEXT"),("neighborhood","TEXT"),
        ("total_population","INTEGER"),("median_age","REAL"),
        ("bachelors_degree_pct","REAL"),("foot_traffic_index","REAL"),
        ("chinese_population_pct","REAL")]),
    "foot_traffic": ("foot_traffic.csv", [
        ("zip_code","TEXT"),("time_of_day","TEXT"),("foot_traffic_score","REAL")]),
    "competitor_prices": ("competitor_prices.csv", [
        ("store_name","TEXT"),("product_type","TEXT"),("price","REAL"),
        ("region","TEXT"),("is_organic","TEXT")]),
    "sales_history_weekly": ("sales_history_weekly.csv", [
        ("week_start_date","TEXT"),("store_location","TEXT"),("product_type","TEXT"),
        ("quantity_sold","INTEGER"),("total_revenue","REAL")]),
    "competitors": ("competitors.csv", [
        ("competitor_id","INTEGER"),("name","TEXT"),("business_type","TEXT"),
        ("zip_code","TEXT"),("lat","REAL"),("lng","REAL"),
        ("rating","REAL"),("review_count","INTEGER")]),
    "competitor_reviews": ("competitor_reviews.csv", [
        ("review_id","INTEGER"),("competitor_id","INTEGER"),("rating","INTEGER"),
        ("review_text","TEXT"),("theme","TEXT")]),
    "suppliers": ("suppliers.csv", [
        ("supplier_id","INTEGER"),("name","TEXT"),("zip_code","TEXT"),
        ("lat","REAL"),("lng","REAL")]),
}

def main():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    for table, (fname, cols) in SCHEMA.items():
        coldef = ", ".join(f'"{c}" {t}' for c, t in cols)
        cur.execute(f'CREATE TABLE "{table}" ({coldef})')
        path = os.path.join(DATA, fname)
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.reader(f); next(r)  # skip header
            placeholders = ",".join("?" for _ in cols)
            cur.executemany(f'INSERT INTO "{table}" VALUES ({placeholders})', list(r))
        n = cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        print(f"  {table:22s} {n:4d} rows")
    con.commit(); con.close()
    print("\nSQLite database built at:", os.path.normpath(DB))

if __name__ == "__main__":
    main()
