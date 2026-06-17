# Builds voucher-data.js: the redemption rows (voucher_id != 'none') with only the
# observable columns the 4 governed live-SQL tracks need. Loaded into sql.js in-browser.
# was_incremental is NOT in the source CSV, so it cannot leak here.
import csv, json
COLS = ["voucher_id","campaign_tier","customer_type","discount_amount_rm","effective_discount_pct"]
rows = []
with open("voucher_orders.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["voucher_id"] and r["voucher_id"] != "none":
            rows.append([
                r["voucher_id"], r["campaign_tier"], r["customer_type"],
                round(float(r["discount_amount_rm"]), 2),
                round(float(r["effective_discount_pct"]), 4),
            ])
with open("voucher-data.js", "w", encoding="utf-8") as f:
    f.write("// Voucher redemption records (governed, read-only) for the live sql.js tracks.\n")
    f.write("// Columns: " + ", ".join(COLS) + ". No was_incremental column exists.\n")
    f.write("const VOUCHER_COLS=" + json.dumps(COLS) + ";\n")
    f.write("const VOUCHER_ROWS=" + json.dumps(rows, separators=(",",":")) + ";\n")
print("redemption rows:", len(rows))
