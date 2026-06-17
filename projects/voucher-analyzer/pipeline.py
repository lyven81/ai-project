#!/usr/bin/env python3
"""
Voucher Profit Planner — build pipeline (data -> brain -> eval).
Phase 1 (seeds): generate dataset with VOLUME-IDENTIFIABLE incrementality.
Phase 2 (trunk): the analytical brain — estimate incrementality (blind to truth),
                 contribution margins, scorecard, category x voucher, recommendations.
Phase 3 (proof): recovery check — estimate vs the baked-in was_incremental truth.
Emits: voucher_orders.csv (deployed, no truth), voucher_orders_eval.csv (with truth), voucher_issuance.csv, results.json
"""
import numpy as np, pandas as pd, json
from datetime import datetime, timedelta
rng = np.random.default_rng(7)

# ---------- realism anchors from the uploaded file ----------
src = pd.read_csv("/mnt/user-data/uploads/dataset.csv")
CATS=["Grocery","Toys","Beauty","Fashion","Sports","Home","Electronics"]
price_pool={c:src.loc[src.category==c,"price"].values for c in CATS}
age_pool=src["customer_age"].values
gender_p=src["customer_gender"].value_counts(normalize=True)
region_p=src["region"].value_counts(normalize=True)
cat_share=src["category"].value_counts(normalize=True).reindex(CATS).fillna(.1); cat_share/=cat_share.sum()

def price(cat,min_p=None):
    pool=price_pool[cat]
    if min_p is not None:
        e=pool[pool>=min_p]
        return float(round(rng.choice(e),2)) if len(e)>=20 else float(round(max(min_p,rng.choice(pool))*rng.uniform(1,1.4),2))
    return float(round(rng.choice(pool),2))

CAT={ "Grocery":dict(cogs=.90,fee=.06,acos=.05,incr=.20),"Toys":dict(cogs=.80,fee=.06,acos=.06,incr=.34),
 "Beauty":dict(cogs=.74,fee=.07,acos=.08,incr=.38),"Fashion":dict(cogs=.64,fee=.07,acos=.07,incr=.42),
 "Sports":dict(cogs=.52,fee=.06,acos=.05,incr=.48),"Home":dict(cogs=.48,fee=.05,acos=.05,incr=.50),
 "Electronics":dict(cogs=.44,fee=.05,acos=.06,incr=.55)}
VOUCHERS={"F1":dict(mech="fixed",thr=50,val=5,redeem=.78),"F2":dict(mech="fixed",thr=150,val=10,redeem=.62),
 "F3":dict(mech="fixed",thr=250,val=20,redeem=.40),"P1":dict(mech="percentage",thr=100,val=.05,redeem=.70),
 "P2":dict(mech="percentage",thr=200,val=.10,redeem=.55),"P3":dict(mech="percentage",thr=300,val=.20,redeem=.85),
 "N1":dict(mech="new_product",thr=0,val=.05,redeem=.50)}
ISSUED=1000
START=datetime(2023,9,12); END=datetime(2025,9,11)
ALLDAYS=(END-START).days

# campaign windows
def months(a,b):
    y,m=a.year,a.month
    while (y,m)<=(b.year,b.month):
        yield y,m
        m=m%12+1; y+=(m==1)
monthly=[]; mega=[]
for y,m in months(START,END):
    s,e=datetime(y,m,13),datetime(y,m,17)
    if s>=START and e<=END: monthly.append((f"{y}-{m:02d}-MONTHLY","monthly",s,e))
    if m==11:
        s,e=datetime(y,11,8),datetime(y,11,12)
        if s>=START and e<=END: mega.append((f"{y}-11-11","11.11",s,e))
    if m==12:
        s,e=datetime(y,12,9),datetime(y,12,13)
        if s>=START and e<=END: mega.append((f"{y}-12-12","12.12",s,e))
windows=monthly+mega
win_days=set()
for _,_,s,e in windows:
    for d in range((e-s).days+1): win_days.add((s+timedelta(days=d)).date())
def rdate(s,e): return s+timedelta(days=int(rng.integers(0,(e-s).days+1)))

# customers + products
cust=[f"C{100000+i}" for i in range(8000)]
c_age={c:int(rng.choice(age_pool)) for c in cust}
c_gen={c:rng.choice(gender_p.index,p=gender_p.values) for c in cust}
c_reg={c:rng.choice(region_p.index,p=region_p.values) for c in cust}
prods=[f"P{200000+i}" for i in range(3500)]
p_cat={p:rng.choice(CATS,p=cat_share.values) for p in prods}
p_new={p:(rng.random()<.08) for p in prods}
p_launch={p:(rdate(START+timedelta(days=120),END-timedelta(days=120)) if p_new[p] else START) for p in prods}
prod_by={c:[p for p in prods if p_cat[p]==c] for c in CATS}
new_by={c:[p for p in prod_by[c] if p_new[p]] for c in CATS}

rows=[]
def stack(cat,gross,net):
    e=CAT[cat]; cogs=round(gross*e["cogs"]*rng.uniform(.97,1.03),2)
    fee=round(net*e["fee"],2); ad=round(net*e["acos"],2)
    return cogs,fee,ad,round(net-cogs-fee-ad,2)
def emit(d,cu,pr,cat,pz,qty,vid,mech,thr,disc,eff,cid,tier,inc,ret):
    gross=round(pz*qty,2); net=round(gross-disc,2); cogs,fee,ad,cm=stack(cat,gross,net)
    rows.append(dict(order_date=d,customer_id=cu,product_id=pr,category=cat,is_new_product=p_new.get(pr,False),
        product_launch_date=p_launch.get(pr,START).date(),price=pz,quantity=qty,gross_amount=gross,
        voucher_id=vid,voucher_mechanic=mech,voucher_threshold=thr,discount_amount_rm=round(disc,2),
        effective_discount_pct=round(eff,4),net_amount=net,campaign_id=cid,campaign_tier=tier,
        was_incremental=inc,cogs=cogs,platform_fee=fee,ad_cost_allocated=ad,contribution_margin=cm,returned=ret))

# ---- (A) ORGANIC baseline demand across ALL days (exists regardless of vouchers) ----
N_ORGANIC=26000
for _ in range(N_ORGANIC):
    cat=rng.choice(CATS,p=cat_share.values); pr=rng.choice(prod_by[cat]); pz=price(cat)
    qty=int(rng.choice([1,2,3,4,5],p=[.72,.15,.07,.04,.02])); d=rdate(START,END)
    ret="Yes" if rng.random()<.055 else "No"
    in_win=d.date() in win_days
    # SUBSIDISED: a baseline order that falls in a campaign window may attach a qualifying voucher
    vid="none";mech="none";thr=0;disc=0.0;eff=0.0;cid="none";tier="none"
    if in_win:
        # find the window
        w=[w for w in windows if w[2].date()<=d.date()<=w[3].date()][0]
        cid,tier=w[0],w[1]
        # eligible vouchers for this price (exclude N1 unless new product)
        elig=[k for k,v in VOUCHERS.items() if v["mech"]!="new_product" and pz>=v["thr"]]
        if p_new[pr]: elig.append("N1")
        if elig and rng.random()<0.55:           # in-window baseline buyers who grab a voucher = subsidy
            vid=rng.choice(elig); v=VOUCHERS[vid]; mech=v["mech"]; thr=v["thr"]
            disc=min(v["val"],round(pz*.9,2)) if mech=="fixed" else round(pz*v["val"],2)
            eff=disc/(pz*qty)
        else:
            cid="none";tier="none"
    emit(d,rng.choice(cust),pr,cat,pz,qty,vid,mech,thr,disc,eff,cid,tier,False,ret)

# ---- (B) INCREMENTAL orders: EXTRA window volume the voucher CAUSED (always true) ----
# category chosen weighted by share*incr so high-incr categories get more incrementals
# => the TRUE per-category incremental share rises Grocery->Electronics, and volume-lift recovers it
incr_w=np.array([cat_share[c]*CAT[c]["incr"] for c in CATS]); incr_w/=incr_w.sum()
for vid,v in VOUCHERS.items():
    n_incr=int(round(v["redeem"]*ISSUED*0.28))
    for _ in range(n_incr):
        wi=rng.choice(len(windows),p=(np.array([1.]*len(monthly)+[6.]*len(mega))/(len(monthly)+6*len(mega))))
        cid,tier,ws,we=windows[wi]; d=rdate(ws,we); cat=rng.choice(CATS,p=incr_w)
        if v["mech"]=="new_product":
            pool=[p for p in new_by[cat] if p_launch[p]<=d] or prod_by[cat]; pr=rng.choice(pool); pz=price(cat)
            disc=round(pz*v["val"],2)
        else:
            pr=rng.choice(prod_by[cat]); pz=price(cat,min_p=v["thr"])
            disc=min(v["val"],round(pz*.9,2)) if v["mech"]=="fixed" else round(pz*v["val"],2)
        qty=int(rng.choice([1,2,3],p=[.82,.13,.05])); eff=disc/(pz*qty)
        ret="Yes" if rng.random()<.05 else "No"
        emit(d,rng.choice(cust),pr,cat,pz,qty,vid,v["mech"],v["thr"],disc,eff,cid,tier,True,ret)

df=pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
df.insert(0,"order_id",[f"O{1000000+i}" for i in range(len(df))])
fs=df.groupby("customer_id")["order_date"].transform("min")
df["customer_type"]=np.where(df["order_date"]==fs,"new","returning")
df["customer_age"]=df.customer_id.map(c_age); df["customer_gender"]=df.customer_id.map(c_gen); df["region"]=df.customer_id.map(c_reg)
df["order_date"]=pd.to_datetime(df.order_date).dt.strftime("%Y-%m-%d")
cols=["order_id","order_date","customer_id","customer_type","customer_age","customer_gender","region",
 "product_id","category","is_new_product","product_launch_date","price","quantity","gross_amount",
 "voucher_id","voucher_mechanic","voucher_threshold","discount_amount_rm","effective_discount_pct",
 "net_amount","campaign_id","campaign_tier","was_incremental","cogs","platform_fee","ad_cost_allocated",
 "contribution_margin","returned"]
df=df[cols]
# DEPLOYED dataset: per-order truth column WITHHELD — the assistant must never see was_incremental.
df.drop(columns=["was_incremental"]).to_csv("/mnt/user-data/outputs/voucher_orders.csv",index=False)
# EVAL copy WITH the truth — for reproducing/auditing the recovery check only. Not deployed, not queried.
df.to_csv("/mnt/user-data/outputs/voucher_orders_eval.csv",index=False)

# ============================================================
# PHASE 2 — THE ANALYTICAL BRAIN  (estimate blind to was_incremental)
# ============================================================
df["d"]=pd.to_datetime(df.order_date)
_wd=set(win_days)
df["in_window"]=df["d"].dt.date.isin(_wd)
v=df[df.voucher_id!="none"].copy()

# --- incrementality ESTIMATE via baseline-counterfactual (DiD-style) per category ---
nonwin_days = ALLDAYS - len(win_days)
est_share={}
for c in CATS:
    base_rate = ((df.category==c)&(~df.in_window)&(df.voucher_id=="none")).sum()/max(nonwin_days,1)
    # actual orders in windows vs expected baseline
    win_orders=((df.category==c)&(df.in_window)).sum()
    exp_base=base_rate*len(win_days)
    incr_vol=max(0.0, win_orders-exp_base)
    redemptions=((v.category==c)).sum()
    est_share[c]=float(np.clip(incr_vol/max(redemptions,1),0,1))
true_share={c:float(v[v.category==c]["was_incremental"].mean()) for c in CATS}

# --- voucher scorecard (uses est_share by category composition) ---
def voucher_block(sub):
    redeemed=len(sub); disc=float(sub.discount_amount_rm.sum())
    s=float(np.average([est_share[c] for c in sub.category],weights=None)) if redeemed else 0
    inc_cm=float((sub.contribution_margin*[est_share[c] for c in sub.category]).sum())
    sub_loss=float((sub.discount_amount_rm*[1-est_share[c] for c in sub.category]).sum())
    net=inc_cm-sub_loss
    return dict(redeemed=redeemed,discount_cost=round(disc,2),est_incremental_share=round(s,3),
        incremental_contribution=round(inc_cm,2),subsidy_loss=round(sub_loss,2),
        net_pnl=round(net,2),roi=round(net/disc,3) if disc else 0,
        verdict=("scale" if net>0.15*disc else "keep" if net>0 else "kill"))
scorecard={}
for vid in VOUCHERS:
    sub=v[v.voucher_id==vid]
    blk=voucher_block(sub); blk.update(issued=ISSUED,redemption_rate=round(len(sub)/ISSUED,3),
        mechanic=VOUCHERS[vid]["mech"],
        value=(f"RM{VOUCHERS[vid]['val']}" if VOUCHERS[vid]['mech']=='fixed' else f"{int(VOUCHERS[vid]['val']*100)}%"),
        threshold=VOUCHERS[vid]["thr"], eff_disc=round(float(sub.effective_discount_pct.mean()),3))
    scorecard[vid]=blk

# --- category x voucher net P&L matrix ---
matrix={}
for c in CATS:
    matrix[c]={}
    for vid in VOUCHERS:
        sub=v[(v.category==c)&(v.voucher_id==vid)]
        if len(sub)==0: matrix[c][vid]=None; continue
        inc_cm=float(sub.contribution_margin.sum()*est_share[c])
        sub_loss=float(sub.discount_amount_rm.sum()*(1-est_share[c]))
        matrix[c][vid]=round(inc_cm-sub_loss,2)

# --- fixed vs % at overlapping value bands ---
bands=[(100,150),(150,200),(200,250),(250,300),(300,99999)]
fxpct=[]
for lo,hi in bands:
    seg=v[(v.price>=lo)&(v.price<hi)]
    fx=seg[seg.voucher_mechanic=="fixed"]; pc=seg[seg.voucher_mechanic=="percentage"]
    def net_per(s):
        if len(s)==0: return None
        return round(float(s.contribution_margin.mean()),2)
    fxpct.append(dict(band=f"RM{lo}-{hi if hi<99999 else '+'}",
        fixed_net_cm=net_per(fx),pct_net_cm=net_per(pc),
        fixed_eff=round(float(fx.effective_discount_pct.mean()),3) if len(fx) else None,
        pct_eff=round(float(pc.effective_discount_pct.mean()),3) if len(pc) else None))

# --- effective discount distribution per voucher (regressivity of fixed) ---
effdist={vid:dict(mean=round(float(v[v.voucher_id==vid].effective_discount_pct.mean()),3),
    min=round(float(v[v.voucher_id==vid].effective_discount_pct.min()),3),
    max=round(float(v[v.voucher_id==vid].effective_discount_pct.max()),3)) for vid in VOUCHERS}

# --- recommendations: per category recommended voucher set + flat->targeted flags ---
recs={}
for c in CATS:
    keep=[vid for vid in VOUCHERS if matrix[c][vid] and matrix[c][vid]>0]
    drop=[vid for vid in VOUCHERS if matrix[c][vid] and matrix[c][vid]<=0]
    recs[c]=dict(use=keep,avoid=drop)
flat_to_targeted=[vid for vid in VOUCHERS
    if scorecard[vid]["net_pnl"]>0 and any(matrix[c][vid] and matrix[c][vid]<0 for c in CATS)]

# --- new product (N1) ---
n1=v[v.voucher_id=="N1"]
new_block=dict(est_incremental_share=round(est_share_avg:=float(np.mean([est_share[c] for c in n1.category])),3) if len(n1) else 0,
    net_pnl=scorecard["N1"]["net_pnl"], verdict=scorecard["N1"]["verdict"],
    note="5% flat reads as trial spend; compare against a small fixed voucher in a follow-up build.")

# overview kpis
total_disc=float(v.discount_amount_rm.sum())
total_inc_cm=sum(scorecard[k]["incremental_contribution"] for k in scorecard)
total_sub=sum(scorecard[k]["subsidy_loss"] for k in scorecard)
overview=dict(promo_spend=round(total_disc,0),real_incremental_margin=round(total_inc_cm-total_sub,0),
    subsidy_share=round(total_sub/total_disc,3),
    best=max(scorecard,key=lambda k:scorecard[k]["net_pnl"]),
    worst=min(scorecard,key=lambda k:scorecard[k]["net_pnl"]),
    orders=len(df),redemptions=len(v))

# ============================================================
# PHASE 3 — RECOVERY CHECK (estimate vs baked-in truth)
# ============================================================
import numpy as _np
mae=float(_np.mean([abs(est_share[c]-true_share[c]) for c in CATS]))
order_est=[est_share[c] for c in CATS]; order_true=[true_share[c] for c in CATS]
rank_ok=list(_np.argsort(order_est))==list(_np.argsort(order_true))
recovery=dict(by_category={c:dict(estimate=round(est_share[c],3),truth=round(true_share[c],3)) for c in CATS},
    mean_abs_error=round(mae,3),ranking_recovered=bool(rank_ok),
    naive_share=1.0, true_overall=round(float(v.was_incremental.mean()),3),
    est_overall=round(float(_np.mean([est_share[c] for c in v.category])),3))

# issuance companion (truth split, for reference)
iss=[]
for vid in VOUCHERS:
    sub=v[v.voucher_id==vid]
    iss.append(dict(voucher_id=vid,mechanic=VOUCHERS[vid]["mech"],
        value=scorecard[vid]["value"],threshold=VOUCHERS[vid]["thr"],issued=ISSUED,redeemed=len(sub),
        redemption_rate=round(len(sub)/ISSUED,3),
        true_incremental=int(sub.was_incremental.sum()),true_subsidised=int((~sub.was_incremental).sum()),
        total_discount_rm=round(float(sub.discount_amount_rm.sum()),2)))
pd.DataFrame(iss).to_csv("/mnt/user-data/outputs/voucher_issuance.csv",index=False)

# --- LIFT BY CATEGORY (observable baseline-counterfactual; recovery vs hidden truth) ---
_wdates=set(df.loc[df.voucher_id!="none","d"].dt.date)
_tot=(df.d.max()-df.d.min()).days+1; _nwin=len(_wdates); _nnon=_tot-_nwin
lift_by_category={}
for c in CATS:
    sub=df[df.category==c]; sa=sub["d"].dt.date.isin(_wdates)
    out_o=int((~sa).sum()); in_o=int(sa.sum())
    ro=out_o/_nnon; ri=in_o/_nwin; exp=ro*_nwin; incr=in_o-exp
    lp=(ri-ro)/ro if ro>0 else 0
    red=int((sub.voucher_id!="none").sum()); ish=incr/red if red>0 else 0
    tr=float(sub.loc[sub.voucher_id!="none","was_incremental"].mean())
    lift_by_category[c]=dict(rate_out=round(ro,2),rate_in=round(ri,2),lift_pct=round(lp,3),
        incremental_orders=int(round(incr)),redemptions=red,
        incremental_share=round(float(ish),3),truth=round(tr,3))

results=dict(meta=dict(generated=str(datetime.now().date()),orders=len(df),redemptions=len(v),
    categories=CATS,vouchers=list(VOUCHERS)),
    overview=overview,scorecard=scorecard,matrix=matrix,fixed_vs_pct=fxpct,
    effective_discount=effdist,recommendations=dict(per_category=recs,flat_to_targeted=flat_to_targeted),
    new_product=new_block,recovery=recovery,lift_by_category=lift_by_category,
    margin_gradient={c:round(float(df[(df.category==c)&(df.voucher_id=='none')].contribution_margin.mean()),2) for c in CATS})
json.dump(results,open("/mnt/user-data/outputs/results.json","w"),indent=1)

# ---------------- VERIFICATION ----------------
print("ORDERS",len(df),"| REDEMPTIONS",len(v),"| cols",len(cols))
print("\nSCORECARD (vid: redeemed | est_inc_share | net_pnl | roi | verdict)")
for k,b in scorecard.items():
    print(f"  {k}: {b['redeemed']:>4} | {b['est_incremental_share']:.2f} | {b['net_pnl']:>10.0f} | {b['roi']:>6.2f} | {b['verdict']}")
print("\nRECOVERY CHECK (incrementality share by category)")
for c in CATS: print(f"  {c:<12} est {recovery['by_category'][c]['estimate']:.2f}  truth {recovery['by_category'][c]['truth']:.2f}")
print(f"  mean abs error: {recovery['mean_abs_error']:.3f} | ranking recovered: {recovery['ranking_recovered']}")
print(f"  overall: est {recovery['est_overall']:.2f} vs truth {recovery['true_overall']:.2f} | naive would say 1.00")
print("\nMARGIN GRADIENT (no-voucher):",{c:results['margin_gradient'][c] for c in CATS})
print("\nflat->targeted flags:",flat_to_targeted)
print("\nLIFT BY CATEGORY (does the voucher increase orders?)")
for c in CATS:
    L=lift_by_category[c]
    print(f"  {c:<12} lift {L['lift_pct']*100:>5.0f}%  +{L['incremental_orders']:>4} orders  | est_share {L['incremental_share']:.2f} vs truth {L['truth']:.2f}")
print("results.json written.")
