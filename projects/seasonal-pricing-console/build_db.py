#!/usr/bin/env python3
"""
ai-agent-mcp-build Step 1 + Step 4: build right-price-right-season.db from results.json
and self-test the 9 governed fixed queries. Writes the DB next to the assistant page.
Run: python build_db.py
"""
import json, os, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE,"data","results.json")))
DB = r"C:\Users\Lenovo\data-analyst-portfolio\agentic_workflow\right-price-right-season.db"
os.makedirs(os.path.dirname(DB), exist_ok=True)
if os.path.exists(DB): os.remove(DB)

LS=R["by_listing_season"]; TS=R["elasticity_by_type_season"]; SEA=R["seasonal"]; P=R["portfolio"]; REC=R["recovery"]
MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MS={1:"shoulder",2:"peak",3:"trough",4:"shoulder",5:"peak",6:"shoulder",7:"shoulder",8:"shoulder",9:"shoulder",10:"shoulder",11:"trough",12:"peak"}
SDISP={"peak":"Peak","shoulder":"Shoulder","trough":"Value"}

con=sqlite3.connect(DB); c=con.cursor()
c.execute("""CREATE TABLE by_month(month TEXT, month_num INT, season TEXT, occupancy REAL, avg_price REAL, revenue REAL)""")
for i,x in enumerate(SEA["by_month"],1):
    c.execute("INSERT INTO by_month VALUES(?,?,?,?,?,?)",(x["month"],i,SDISP[MS[i]],round(x["occupancy"]*100,1),x["avg_price"],x["revenue"]))

c.execute("""CREATE TABLE season_summary(season TEXT, occupancy REAL, avg_price REAL, revenue REAL, uplift_rm REAL)""")
for s in ["peak","shoulder","trough"]:
    row=next(z for z in SEA["by_season"] if z["season"]==s)
    up=round(sum(r["uplift_rm"] for r in LS if r["season"]==s))
    c.execute("INSERT INTO season_summary VALUES(?,?,?,?,?)",(SDISP[s],round(row["occupancy"]*100,1),row["avg_price"],row["revenue"],up))

c.execute("""CREATE TABLE elasticity(property_type TEXT, season TEXT, elasticity REAL, lost_per_10 REAL)""")
for r in TS:
    c.execute("INSERT INTO elasticity VALUES(?,?,?,?)",(r["property_type"],SDISP[r["season"]],r["elasticity"],round(abs(r["elasticity"])*10,1)))

c.execute("""CREATE TABLE listing_season(listing_id TEXT, listing_title TEXT, property_type TEXT, season TEXT,
    current_price REAL, optimal_price REAL, current_occ REAL, optimal_occ REAL, uplift_rm REAL, uplift_pct REAL, move TEXT)""")
for r in LS:
    move="Raise" if r["optimal_price"]>r["current_avg_price"] else ("Cut" if r["optimal_price"]<r["current_avg_price"] else "Hold")
    c.execute("INSERT INTO listing_season VALUES(?,?,?,?,?,?,?,?,?,?,?)",(
        r["listing_id"],r["listing_title"],r["property_type"],SDISP[r["season"]],
        round(r["current_avg_price"]),round(r["optimal_price"]),round(r["current_occ"]*100,1),
        round(r["optimal_occ"]*100,1),round(r["uplift_rm"]),r["uplift_pct"],move))

c.execute("""CREATE TABLE price_sheet(listing_id TEXT, listing_title TEXT, property_type TEXT, month TEXT, month_num INT, season TEXT, suggested_rate REAL)""")
opt={(r["listing_id"],r["season"]):round(r["optimal_price"]) for r in LS}
meta=[(r["listing_id"],r["listing_title"],r["property_type"]) for r in LS if r["season"]=="peak"]
inv={"peak":"peak","shoulder":"shoulder","trough":"trough"}
for lid,title,typ in meta:
    for m in range(1,13):
        s=MS[m]
        c.execute("INSERT INTO price_sheet VALUES(?,?,?,?,?,?,?)",(lid,title,typ,MN[m-1],m,SDISP[s],opt[(lid,s)]))

c.execute("""CREATE TABLE portfolio(metric TEXT, value TEXT)""")
for k,v in [("observed_revenue",round(P["observed_revenue"])),("occupancy_pct",round(P["overall_occupancy"]*100,1)),
    ("uplift_rm",round(P["projected_uplift_rm"])),("uplift_pct",P["projected_uplift_pct"]),("listings",P["listings"]),
    ("raise_count",sum(1 for r in LS if r["optimal_price"]>r["current_avg_price"])),
    ("cut_count",sum(1 for r in LS if r["optimal_price"]<r["current_avg_price"])),
    ("busiest_month",SEA["peak_month"]),("slowest_month",SEA["slow_month"]),
    ("method_error",REC["mean_abs_error"]),("naive_error",REC["naive_mean_abs_error"]),
    ("truth_in_ci_pct",round(REC["truth_in_ci_rate"]*100)),
    ("accuracy_ratio",round(REC["naive_mean_abs_error"]/REC["mean_abs_error"],1))]:
    c.execute("INSERT INTO portfolio VALUES(?,?)",(k,str(v)))
con.commit()

# ---- Step 4: self-test the 9 fixed queries ----
SQL = {
 "season_calendar":("SELECT month, season, occupancy, avg_price FROM by_month ORDER BY month_num", {}),
 "current_state":("SELECT season, current_price, current_occ FROM listing_season WHERE listing_id=:lid ORDER BY CASE season WHEN 'Peak' THEN 1 WHEN 'Shoulder' THEN 2 ELSE 3 END", {"lid":"KS10"}),
 "sensitivity_all":("SELECT property_type, ROUND(AVG(lost_per_10),1) lost FROM elasticity GROUP BY property_type ORDER BY lost DESC", {}),
 "most_sensitive":("SELECT property_type, ROUND(AVG(lost_per_10),1) lost FROM elasticity GROUP BY property_type ORDER BY lost DESC LIMIT 1", {}),
 "opportunity_by_season":("SELECT season, uplift_rm FROM season_summary ORDER BY uplift_rm DESC", {}),
 "optimal_by_type_season":("SELECT property_type, season, ROUND(AVG(optimal_price)) rate FROM listing_season GROUP BY property_type, season ORDER BY property_type, CASE season WHEN 'Peak' THEN 1 WHEN 'Shoulder' THEN 2 ELSE 3 END", {}),
 "raise_cut":("SELECT move, COUNT(*) n FROM listing_season GROUP BY move ORDER BY n DESC", {}),
 "current_vs_suggested":("SELECT season, current_price, optimal_price, uplift_pct FROM listing_season WHERE listing_id=:lid ORDER BY CASE season WHEN 'Peak' THEN 1 WHEN 'Shoulder' THEN 2 ELSE 3 END", {"lid":"KS05"}),
 "price_sheet_all":("SELECT listing_title, month, suggested_rate FROM price_sheet ORDER BY listing_id, month_num", {}),
}
print("DB:", DB, "\nSELF-TEST (rows returned per tool):")
ok=True
for name,(q,params) in SQL.items():
    try:
        rows=c.execute(q,params).fetchall()
        print(f"  {name:<24} {len(rows):>4} rows  e.g. {rows[0] if rows else 'NONE'}")
        if not rows: ok=False
    except Exception as e:
        print(f"  {name:<24} ERROR {e}"); ok=False
con.close()
print("ALL TOOLS RETURN ROWS" if ok else "SOME TOOLS FAILED")
