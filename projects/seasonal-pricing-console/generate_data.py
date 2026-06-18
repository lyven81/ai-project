#!/usr/bin/env python3
"""
Kinta Stays - Ipoh Airbnb seasonal price-elasticity: DATA LAYER (Step 1, the roots).

Builds on the Voucher Analyzer generator pattern: a synthetic dataset with a
KNOWN ground truth baked in. Here the truth is a per-listing, per-season price
elasticity, and occupancy genuinely RESPONDS to the nightly price (the mechanism
the voucher generator lacked).

Grain: one row per listing per night, 2 calendar years (2 full seasonal cycles).
Emits:
  data/calendar_deployed.csv  - the queryable dataset, NO truth column
  data/calendar_eval.csv      - same rows + true_elasticity (for the recovery check only)
  data/listings.csv           - the 15-listing roster
  data/truth_elasticity.csv   - the baked-in elasticity per listing per season

Run:  python generate_data.py
"""
import numpy as np, pandas as pd, os
from datetime import date, timedelta

rng = np.random.default_rng(11)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data"); os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 1. ROSTER
# 15 Ipoh listings (from build-spec): id, title, type, base weekday off-peak rate,
# review count -> demand weight (review / busiest). Base rate is the elasticity reference price.
ROSTER = [
 ("KS01","Infinity Poolside View @ The Haven Lakeside Tambun","1BR",250,112),
 ("KS02","Sunset Hill View @ Sunway City Ipoh","1BR",210,68),
 ("KS03","Hot Spring Retreat @ Lost World Tambun","1BR",240,95),
 ("KS04","Comfy Apt @ Majestic Taman Jubilee","1BR",195,54),
 ("KS05","Spacious Family Stay @ Ipoh Garden","2BR",300,73),
 ("KS06","High Rise Mountain View @ Meru Raya","2BR",270,41),
 ("KS07","Luxury Apt @ Kinta Riverfront","2BR",330,58),
 ("KS08","Grand Family Retreat @ Tambun Lakeside","3BR",450,87),
 ("KS09","Premium City View @ Greentown Octagon","3BR",380,49),
 ("KS10","Heritage Studio @ Old Town Concubine Lane","Studio",185,64),
 ("KS11","Modern Studio Loft @ Greentown","Studio",165,38),
 ("KS12","Chic Studio @ The Horizon Bercham","Studio",150,22),
 ("KS13","Compact Studio @ Ipoh Garden East","Studio",160,29),
 ("KS14","Minimalist Studio @ Octagon Greentown","Studio",175,33),
 ("KS15","Snug Studio @ Station 18 Kinta City","Studio",150,17),
]
maxrev = max(r[4] for r in ROSTER)
TYPE_CAP   = {"Studio":2,"1BR":3,"2BR":4,"3BR":6}
TYPE_CLEAN = {"Studio":40,"1BR":50,"2BR":70,"3BR":90}
TYPE_MIN   = {"Studio":1,"1BR":1,"2BR":2,"3BR":2}

# ---------------------------------------------------------------- 2. SEASONS + TRUTH
# Ipoh tourism: peak Dec (year-end), Feb (CNY), May; trough Nov + Mar; else shoulder.
def season_of(d):
    if d.month in (12,2,5): return "peak"
    if d.month in (11,3):   return "trough"
    return "shoulder"

# Price the HOST sets (multipliers on base): up in peak, down in trough, weekend premium.
PRICE_SEASON = {"peak":1.30,"shoulder":1.00,"trough":0.85}
PRICE_WEEKEND = 1.25                       # Fri/Sat
# DEMAND (independent of price): higher in peak, lower in trough, weekend bump.
DEMAND_SEASON = {"peak":1.32,"shoulder":1.00,"trough":0.76}
DEMAND_WEEKEND = 1.18

# Baked-in TRUE elasticity: negative; bigger magnitude = more price-sensitive.
# Studios/budget most elastic; 3BR/premium least. Peak demand is LESS elastic, trough MORE
# (the season x price interaction the build must recover).
TYPE_ELAST = {"Studio":-1.60,"1BR":-1.25,"2BR":-1.05,"3BR":-0.85}
SEASON_ELAST_FACTOR = {"peak":0.80,"shoulder":1.00,"trough":1.20}

BASE_OCC = 0.62                            # reference booking prob at reference price
START, END = date(2023,1,1), date(2025,12,31)   # 3 years = 3 seasonal cycles, tighter estimates
NDAYS = (END-START).days + 1

# per-listing true elasticity by season (+ small per-listing jitter so same-type listings differ)
truth = {}
for lid,_,typ,_,_ in ROSTER:
    jit = float(rng.uniform(-0.08,0.08))
    truth[lid] = {s: round(TYPE_ELAST[typ]*SEASON_ELAST_FACTOR[s]+jit, 3) for s in PRICE_SEASON}

# ---------------------------------------------------------------- 3. HOST PRICE ADJUSTMENTS
# Per-listing MONTHLY idiosyncratic price multiplier (+/-20%), INDEPENDENT of season/weekend/demand.
# Real hosts re-test prices month to month; this exogenous price variation is what identifies
# elasticity (it is the DiD price-change event: the listing's price moves while demand drivers do not).
ym_list = sorted({(START+timedelta(days=i)).year*100+(START+timedelta(days=i)).month
                  for i in range(NDAYS)})
adj = {lid: {ym: float(rng.uniform(0.80,1.20)) for ym in ym_list} for lid,_,_,_,_ in ROSTER}

# ---------------------------------------------------------------- 4. GENERATE ROWS
rows = []
for lid,title,typ,base,rev in ROSTER:
    dw = rev/maxrev                                   # demand weight 0..1
    dw_term = 0.70 + 0.50*dw                          # popularity multiplier ~0.78..1.20
    for i in range(NDAYS):
        d = START + timedelta(days=i)
        s = season_of(d); wknd = d.weekday() >= 4     # Fri=4, Sat=5 (Sun=6 -> not premium)
        price = base * PRICE_SEASON[s] * (PRICE_WEEKEND if wknd else 1.0) * adj[lid][d.year*100+d.month]
        price = round(price, 0)
        # occupancy responds to price via the baked-in elasticity (constant-elasticity demand)
        el = truth[lid][s]
        price_response = (price/base) ** el
        occ = (BASE_OCC * dw_term * DEMAND_SEASON[s]
               * (DEMAND_WEEKEND if wknd else 1.0) * price_response)
        occ = float(np.clip(occ * rng.uniform(0.98,1.02), 0.02, 0.98))   # small day-level noise
        booked = int(rng.random() < occ)
        clean = TYPE_CLEAN[typ]
        platform_fee = round(price*0.03, 2) if booked else 0.0           # host service fee ~3%
        revenue = price if booked else 0.0
        var_cost = round((clean + price*0.03 + {"Studio":12,"1BR":16,"2BR":22,"3BR":30}[typ]), 2) if booked else 0.0
        rows.append(dict(
            listing_id=lid, listing_title=title, property_type=typ,
            date=d.isoformat(), season=s, is_weekend=int(wknd),
            nightly_price=price, booked=booked, occupancy_prob=round(occ,3),
            min_nights=TYPE_MIN[typ], capacity=TYPE_CAP[typ],
            cleaning_fee=clean, platform_fee=platform_fee,
            revenue=revenue, variable_cost=var_cost,
            review_count=rev, demand_weight=round(dw,3),
            true_elasticity=el))
df = pd.DataFrame(rows)

# ---------------------------------------------------------------- 5. EMIT
deploy_cols = ["listing_id","listing_title","property_type","date","season","is_weekend",
    "nightly_price","booked","min_nights","capacity","cleaning_fee","platform_fee",
    "revenue","variable_cost","review_count","demand_weight"]      # NO true_elasticity / occupancy_prob
df[deploy_cols].to_csv(os.path.join(OUT,"calendar_deployed.csv"), index=False)
df.to_csv(os.path.join(OUT,"calendar_eval.csv"), index=False)

pd.DataFrame([dict(listing_id=l,title=t,property_type=ty,base_rate=b,review_count=r,
    demand_weight=round(r/maxrev,3)) for l,t,ty,b,r in ROSTER]
    ).to_csv(os.path.join(OUT,"listings.csv"), index=False)

tr = [dict(listing_id=l, property_type=dict((x[0],x[2]) for x in ROSTER)[l],
    **{f"elasticity_{s}":truth[l][s] for s in PRICE_SEASON}) for l in truth]
pd.DataFrame(tr).to_csv(os.path.join(OUT,"truth_elasticity.csv"), index=False)

# ---------------------------------------------------------------- 6. VERIFY
print(f"ROWS {len(df)} | listings {df.listing_id.nunique()} | days {NDAYS} "
      f"({START} -> {END})")
print(f"overall occupancy {df.booked.mean():.3f} | avg price RM{df.nightly_price.mean():.0f} "
      f"| total revenue RM{df.revenue.sum():,.0f}")
print("\nBy season (price up in peak, demand up too, occupancy stays firm):")
g = df.groupby("season").agg(avg_price=("nightly_price","mean"),
    occupancy=("booked","mean"), nights=("booked","size"))
print(g.round(2).to_string())
print("\nWeekend vs weekday:")
print(df.groupby("is_weekend").agg(avg_price=("nightly_price","mean"),
    occupancy=("booked","mean")).round(3).to_string())
print("\nSanity - does occupancy fall as price rises within a listing+season?")
chk = df[(df.listing_id=="KS10")&(df.season=="shoulder")]
lo = chk[chk.nightly_price<=chk.nightly_price.median()].booked.mean()
hi = chk[chk.nightly_price> chk.nightly_price.median()].booked.mean()
print(f"  KS10 shoulder: occ at LOW price {lo:.3f}  vs HIGH price {hi:.3f}  "
      f"(low should exceed high) | true elasticity {truth['KS10']['shoulder']}")
print("\nBaked-in elasticity (head):")
print(pd.DataFrame(tr).head(6).to_string(index=False))
print("\nWROTE: data/calendar_deployed.csv, calendar_eval.csv, listings.csv, truth_elasticity.csv")
