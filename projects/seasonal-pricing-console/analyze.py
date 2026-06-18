#!/usr/bin/env python3
"""
Kinta Stays - ANALYTICAL BRAIN (Step 2) + RECOVERY CHECK (Step 3).

Step 2: estimate price elasticity per ROOM TYPE x SEASON BLIND to the truth, via a
        log-log demand regression with LISTING FIXED EFFECTS + a weekend control
        (the identification: within-listing monthly price changes, net of listing,
        season and weekend = the exogenous treatment). 95% CIs included. Then derive
        the profit-maximizing nightly rate per listing per season.
Step 3: prove the estimate recovers the baked-in true elasticity (from the eval file)
        and beats a naive no-controls estimate.

Reads  : data/calendar_deployed.csv (blind), data/calendar_eval.csv (truth, Step 3 only)
Writes : data/results.json
Run    : python analyze.py
"""
import numpy as np, pandas as pd, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE,"data")
dep = pd.read_csv(os.path.join(D,"calendar_deployed.csv"))
ev  = pd.read_csv(os.path.join(D,"calendar_eval.csv"))
SEASONS = ["peak","shoulder","trough"]; TYPES = ["Studio","1BR","2BR","3BR"]

def wls(X, y, w):
    W = np.sqrt(w); Xw, yw = X*W[:,None], y*W
    beta,_,_,_ = np.linalg.lstsq(Xw, yw, rcond=None)
    resid = yw - Xw@beta; dof = max(len(y)-X.shape[1],1)
    cov = float(resid@resid)/dof*np.linalg.inv(Xw.T@Xw)
    return beta, cov

def estimate(sub, controls=True):
    """Elasticity = coef on ln(price). controls=True adds listing fixed effects + weekend."""
    g = (sub.groupby(["listing_id","is_weekend","nightly_price"])
            .agg(occ=("booked","mean"), n=("booked","size")).reset_index())
    g = g[g.occ > 0]
    if len(g) < 6 or g.nightly_price.nunique() < 3: return None
    y = np.log(g.occ.values); w = g.n.values.astype(float); lp = np.log(g.nightly_price.values)
    if controls:
        lids = sorted(g.listing_id.unique())
        FE = np.column_stack([(g.listing_id.values==l).astype(float) for l in lids])  # listing intercepts
        X = np.column_stack([FE, lp, g.is_weekend.values.astype(float)]); ei = FE.shape[1]
    else:
        X = np.column_stack([np.ones(len(g)), lp]); ei = 1                            # naive: no controls
    beta, cov = wls(X, y, w); e, se = float(beta[ei]), float(np.sqrt(cov[ei,ei]))
    return dict(elasticity=round(e,3), se=round(se,3),
                ci_low=round(e-1.96*se,3), ci_high=round(e+1.96*se,3))

def optimal_price(sub, e, base):
    """Profit-max rate from the constant-elasticity curve anchored at the listing-season's
    current avg price/occupancy, net of variable cost per booked night. The search is bounded
    to the prices ACTUALLY OBSERVED that season (no extrapolation beyond the data's support),
    which keeps recommendations realistic and genuinely season-specific."""
    P0 = float(sub.nightly_price.mean()); occ0 = float(sub.booked.mean())
    bk = sub[sub.booked==1]; varc = float(bk.variable_cost.mean()) if len(bk) else float(sub.cleaning_fee.mean())
    e = min(e, -0.05)
    lo, hi = float(sub.nightly_price.min()), float(sub.nightly_price.max())
    grid = np.arange(lo, hi+1, 1.0)
    occP = np.clip(occ0*(grid/P0)**e, 0.02, 0.98); profit = occP*(grid-varc)
    k = int(np.argmax(profit)); cur = occ0*(P0-varc)
    return dict(current_avg_price=round(P0,0), current_occ=round(occ0,3),
                optimal_price=round(float(grid[k]),0), optimal_occ=round(float(occP[k]),3),
                current_profit_per_night=round(cur,2), optimal_profit_per_night=round(float(profit[k]),2),
                uplift_pct=round(float((profit[k]-cur)/cur*100),1) if cur>0 else None)

# ----------------------------------------------------- STEP 2: elasticity by type x season
el_ts, ts_rows = {}, []
for ty in TYPES:
    for s in SEASONS:
        sub = dep[(dep.property_type==ty)&(dep.season==s)]
        est = estimate(sub, True); nv = estimate(sub, False)
        truth = float(ev[(ev.property_type==ty)&(ev.season==s)].true_elasticity.mean())
        el_ts[(ty,s)] = est["elasticity"]
        ts_rows.append(dict(property_type=ty, season=s, **est,
                            naive=nv["elasticity"], truth=round(truth,3),
                            abs_err=round(abs(est["elasticity"]-truth),3),
                            naive_abs_err=round(abs(nv["elasticity"]-truth),3),
                            truth_in_ci=bool(est["ci_low"]<=truth<=est["ci_high"])))
ts = pd.DataFrame(ts_rows)

# ----------------------------------------------------- optimal price per listing x season
base_rate = (dep[(dep.season=="shoulder")&(dep.is_weekend==0)]
             .groupby("listing_id").nightly_price.median().to_dict())
meta_l = dep[["listing_id","listing_title","property_type"]].drop_duplicates()
ls_rows = []
for _,r in meta_l.iterrows():
    for s in SEASONS:
        sub = dep[(dep.listing_id==r.listing_id)&(dep.season==s)]
        opt = optimal_price(sub, el_ts[(r.property_type,s)], base_rate[r.listing_id])
        ls_rows.append(dict(listing_id=r.listing_id, listing_title=r.listing_title,
                            property_type=r.property_type, season=s,
                            elasticity=el_ts[(r.property_type,s)], **opt))
ls = pd.DataFrame(ls_rows)

# ----------------------------------------------------- STEP 3: recovery check
recovery = dict(
    mean_abs_error=round(float(ts.abs_err.mean()),3),
    naive_mean_abs_error=round(float(ts.naive_abs_err.mean()),3),
    truth_in_ci_rate=round(float(ts.truth_in_ci.mean()),3),
    by_season={s:dict(est_mean=round(float(ts[ts.season==s].elasticity.mean()),3),
                      truth_mean=round(float(ts[ts.season==s].truth.mean()),3)) for s in SEASONS},
    n_cells=len(ts))

# ----------------------------------------------------- portfolio summary
cur_rev = float(dep.revenue.sum())
cell_rev = dep.groupby(["listing_id","season"]).revenue.sum().rename("cell_rev").reset_index()
ls = ls.merge(cell_rev, on=["listing_id","season"], how="left")
ls["uplift_rm"] = ls.cell_rev*ls.uplift_pct.fillna(0)/100
portfolio = dict(listings=int(dep.listing_id.nunique()), nights=int(len(dep)), days=int(dep.date.nunique()),
    observed_revenue=round(cur_rev,0), overall_occupancy=round(float(dep.booked.mean()),3),
    projected_uplift_rm=round(float(ls.uplift_rm.sum()),0),
    projected_uplift_pct=round(float(ls.uplift_rm.sum()/cur_rev*100),1))

# ----------------------------------------------------- seasonal trend (peak/slow periods)
dep["month"] = pd.to_datetime(dep.date).dt.month
MN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
by_month = [dict(month=MN[m-1], occupancy=round(float(g.booked.mean()),3),
                 avg_price=round(float(g.nightly_price.mean()),0),
                 revenue=round(float(g.revenue.sum()),0))
            for m,g in [(m, dep[dep.month==m]) for m in range(1,13)]]
by_season_t = [dict(season=s, occupancy=round(float(g.booked.mean()),3),
                    avg_price=round(float(g.nightly_price.mean()),0),
                    revenue=round(float(g.revenue.sum()),0), nights=int(len(g)))
               for s,g in [(s, dep[dep.season==s]) for s in SEASONS]]
seasonal = dict(by_month=by_month, by_season=by_season_t,
    peak_month=max(by_month,key=lambda x:x["occupancy"])["month"],
    slow_month=min(by_month,key=lambda x:x["occupancy"])["month"])

out = dict(meta=dict(project="Kinta Stays - Ipoh seasonal price-elasticity", grain="listing-night",
        listings=portfolio["listings"], period=f"{dep.date.min()}..{dep.date.max()}"),
    portfolio=portfolio, recovery=recovery, seasonal=seasonal,
    elasticity_by_type_season=json.loads(ts.round(3).to_json(orient="records")),
    by_listing_season=json.loads(ls.round(3).to_json(orient="records")))
json.dump(out, open(os.path.join(D,"results.json"),"w"), indent=1)

# ----------------------------------------------------- verify
print("STEP 2 - ELASTICITY BY TYPE x SEASON (estimate vs truth)")
print(ts[["property_type","season","elasticity","ci_low","ci_high","truth","naive"]].to_string(index=False))
print(f"\nSTEP 3 - RECOVERY CHECK over {recovery['n_cells']} type-season cells")
print(f"  mean abs error (controlled): {recovery['mean_abs_error']}  "
      f"vs NAIVE (no controls): {recovery['naive_mean_abs_error']}")
print(f"  truth inside 95% CI: {recovery['truth_in_ci_rate']*100:.0f}% of cells")
for s in SEASONS:
    b=recovery['by_season'][s]; print(f"  {s:<9} est {b['est_mean']:>7}  truth {b['truth_mean']:>7}")
print(f"\nPORTFOLIO: observed revenue RM{portfolio['observed_revenue']:,.0f} | "
      f"occupancy {portfolio['overall_occupancy']:.0%} | projected uplift "
      f"RM{portfolio['projected_uplift_rm']:,.0f} ({portfolio['projected_uplift_pct']}%)")
print("\nOPTIMAL PRICE sample:")
print(ls[["listing_id","season","current_avg_price","optimal_price","uplift_pct"]].head(6).to_string(index=False))
print("WROTE data/results.json")
