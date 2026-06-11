"""
Lead Source Intelligence — Synthetic Dataset Generator
Project: Property Rental Lead Source Analytics (Pau Analytics portfolio build)
Window: 1 Dec 2025 – 31 May 2026 (6 months)
Seed fixed for reproducibility. All planted insights documented in README.md.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(2026)

START = datetime(2025, 12, 1)
END = datetime(2026, 5, 31, 23, 59)

# ---------------------------------------------------------------
# 1. LISTINGS (10) — fictionalized agent: "Adeline Khoo (PEA 9183), Klang Valley Homes Realty"
# ---------------------------------------------------------------
listings = [
    # id, name, area, segment, config, sqf, rent, gender_rule, listed, status, signed_date, signed_source, base_weekly_enq
    ("L01", "Arte Mont Kiara", "Mont Kiara, KL", "whole_unit", "1R1B + powder", 494, 1749, "any", "2025-12-01", "signed", "2026-02-18", "propertyguru", 6.0),
    ("L02", "Nexus Residence (Room)", "Taman Pertama, Cheras", "room", "Private room, shared bath", 120, 899, "any", "2025-12-01", "signed", "2026-04-21", "meta_ads", 9.0),
    ("L03", "J.Dupion Residence (Female Room)", "Taman Tenaga, Cheras", "room", "Medium room, shared bath", 110, 799, "female", "2025-12-08", "active", None, None, 8.5),
    ("L04", "28 Boulevard Studio", "Pandan Perdana, Ampang", "studio", "Studio, 1 car park", 450, 1599, "any", "2025-12-15", "active", None, None, 5.5),
    ("L05", "Nexus Residence (Whole Unit)", "Taman Pertama, Cheras", "whole_unit", "3R2B, 2 car parks", 850, 2999, "any", "2026-01-05", "signed", "2026-05-12", "propertyguru", 4.0),
    ("L06", "J.Dupion Residence (Master Room)", "Taman Tenaga, Cheras", "room", "Master room, attached bath", 160, 1200, "any", "2025-12-08", "signed", "2026-03-09", "referral", 7.0),
    ("L07", "Lavile Kuala Lumpur", "Maluri, Cheras", "whole_unit", "2R2B", 650, 1800, "any", "2025-12-10", "signed", "2026-01-02", "google_ads", 8.0),
    ("L08", "M Vertica (Room)", "Maluri, Cheras", "room", "Medium room, shared bath", 115, 850, "any", "2026-01-12", "signed", "2026-04-06", "referral", 8.0),
    ("L09", "Sunway Velocity Two", "Maluri, Cheras", "whole_unit", "3R2B premium", 950, 3400, "any", "2026-02-01", "active", None, None, 6.5),  # STALE
    ("L10", "Razak City Residences Studio", "Sungai Besi, KL", "studio", "Studio, furnished", 480, 1350, "any", "2025-12-20", "signed", "2026-03-26", "google_ads", 6.0),
]
listings_df = pd.DataFrame(listings, columns=[
    "listing_id","property_name","area","segment","configuration","size_sqf",
    "asking_rent_myr","gender_rule","listed_date","status","signed_date","signed_source","_base_w"])

# ---------------------------------------------------------------
# 2. SOURCE BEHAVIOR PROFILES (planted insights live here)
# ---------------------------------------------------------------
# share = relative enquiry volume weight; q = qualified rate; resp = responded rate;
# view = P(viewing booked | qualified & responded); show = P(attended | booked)
SOURCES = {
    "mudah":        dict(share=0.38, q=0.15, view=0.30, show=0.55, methods=[("portal_chat",0.7),("phone_call",0.2),("whatsapp",0.1)]),
    "propertyguru": dict(share=0.27, q=0.42, view=0.55, show=0.75, methods=[("portal_chat",0.6),("whatsapp",0.3),("phone_call",0.1)]),
    "meta_ads":     dict(share=0.16, q=0.35, view=0.45, show=0.65, methods=[("lead_form",0.5),("whatsapp",0.4),("phone_call",0.1)]),
    "google_ads":   dict(share=0.11, q=0.55, view=0.68, show=0.80, methods=[("whatsapp",0.45),("phone_call",0.35),("lead_form",0.2)]),
    "referral":     dict(share=0.08, q=0.75, view=0.80, show=0.90, methods=[("whatsapp",0.85),("phone_call",0.15)]),
}

# Channel x segment interaction (insight #6): multiplier on volume
SEG_MULT = {
    ("meta_ads","room"): 1.6, ("meta_ads","studio"): 1.1, ("meta_ads","whole_unit"): 0.5,
    ("google_ads","whole_unit"): 1.7, ("google_ads","studio"): 1.3, ("google_ads","room"): 0.5,
    ("mudah","room"): 1.5, ("mudah","studio"): 1.0, ("mudah","whole_unit"): 0.6,
    ("propertyguru","whole_unit"): 1.4, ("propertyguru","studio"): 1.1, ("propertyguru","room"): 0.8,
    ("referral","room"): 1.2, ("referral","studio"): 1.0, ("referral","whole_unit"): 0.9,
}

CAMPAIGNS = {
    "google_ads": {"whole_unit": "G-Search WholeUnits Cheras/KL", "studio": "G-Search Studios MRT", "room": "G-Search Rooms MRT"},
    "meta_ads":   {"room": "Meta Rooms YoungPro", "studio": "Meta Studio Budget", "whole_unit": "Meta Rooms YoungPro"},
}

OUTCOME_NOTES = ["no_reply","lowball","requirement_mismatch","budget_mismatch","no_show","lost_to_other","unanswered","still_open","viewing_pipeline","tenancy_signed"]

def weekly_intensity(listing, week_start):
    """Enquiries/week for a listing, applying lifecycle + stale + signed cutoff."""
    lid = listing.listing_id
    listed = pd.Timestamp(listing.listed_date)
    if week_start < listed - timedelta(days=6):
        return 0.0
    age_w = max(0, (week_start - listed).days / 7)
    base = listing._base_w
    # New-listing bump then settle
    lifecycle = 1.35 if age_w < 2 else (1.0 if age_w < 10 else 0.85)
    # STALE L09: collapse after week 2
    if lid == "L09":
        lifecycle = 1.5 if age_w < 2 else max(0.25, 1.5 - 0.45*age_w)
    # STAR L07: hot until signed
    if lid == "L07":
        lifecycle *= 1.3
    # Signed: taper to ~0 after signed date
    if listing.status == "signed":
        sd = pd.Timestamp(listing.signed_date)
        if week_start > sd:
            return 0.15  # stragglers before listing removed
    # Mild seasonality: Jan-Feb intake bump
    m = week_start.month
    season = 1.2 if m in (1, 2) else (0.9 if m == 12 else 1.0)
    return base * lifecycle * season

def pick(dist):
    items, w = zip(*dist)
    w = np.array(w); w = w / w.sum()
    return rng.choice(items, p=w)

def random_dt(week_start):
    """Datetime within week; ~20% land after-hours (Mon-Fri 20:00-23:00) or weekend."""
    after_hours = rng.random() < 0.20
    if after_hours:
        if rng.random() < 0.5:  # weekday evening
            day = int(rng.integers(0, 5)); hour = int(rng.integers(20, 23))
        else:                   # weekend
            day = int(rng.integers(5, 7)); hour = int(rng.integers(10, 22))
    else:
        day = int(rng.integers(0, 5)); hour = int(rng.choice(range(9, 20)))
    minute = int(rng.integers(0, 60))
    return week_start + timedelta(days=day, hours=hour, minutes=minute)

def is_after_hours(dt):
    return dt.weekday() >= 5 or dt.hour >= 20 or dt.hour < 9

# ---------------------------------------------------------------
# 3. GENERATE ENQUIRIES
# ---------------------------------------------------------------
rows = []
eid = 0
weeks = pd.date_range(START, END, freq="W-MON")

for _, L in listings_df.iterrows():
    for wk in weeks:
        lam = weekly_intensity(L, wk)
        if lam <= 0:
            continue
        n = rng.poisson(lam)
        for _ in range(n):
            # choose source weighted by share * segment multiplier
            weights = {s: p["share"] * SEG_MULT.get((s, L.segment), 1.0) for s, p in SOURCES.items()}
            ws = np.array(list(weights.values())); ws = ws / ws.sum()
            src = rng.choice(list(weights.keys()), p=ws)
            P = SOURCES[src]
            dt = random_dt(wk.to_pydatetime())
            if dt < pd.Timestamp(L.listed_date) or dt > END:
                continue
            ah = is_after_hours(dt)
            method = pick(P["methods"])
            campaign = CAMPAIGNS.get(src, {}).get(L.segment, None)

            # requirement mismatch: planted female-room problem on L03 via mudah
            req_mismatch = False
            if L.listing_id == "L03" and src == "mudah" and rng.random() < 0.28:
                req_mismatch = True
            elif rng.random() < 0.06:
                req_mismatch = True

            # qualification drawn at target rate; move-in days made consistent with it
            qualified = (not req_mismatch) and (rng.random() < P["q"])
            if qualified:
                move_in = int(np.clip(rng.normal(18, 7), 3, 30))
            else:
                if rng.random() < 0.6:
                    move_in = max(31, int(rng.normal(48, 14)))   # beyond 30-day window
                else:
                    move_in = max(3, int(rng.normal(24, 10)))    # in-window but failed for other reasons

            # response behaviour: after-hours unanswered 3x (insight #5)
            unanswered_p = 0.21 if ah else 0.07
            responded = rng.random() > unanswered_p
            resp_min = None
            if responded:
                base_resp = rng.lognormal(mean=3.4, sigma=0.9)  # ~30 min median
                resp_min = round(base_resp * (3.0 if ah else 1.0), 1)

            viewing_booked = bool(responded and qualified and rng.random() < P["view"])
            viewing_attended = bool(viewing_booked and rng.random() < P["show"])

            # outcome
            if not responded:
                outcome = "unanswered"
            elif req_mismatch:
                outcome = "requirement_mismatch"
            elif viewing_attended:
                outcome = rng.choice(["lost_to_other","still_open","viewing_pipeline"], p=[0.45,0.30,0.25])
            elif viewing_booked:
                outcome = "no_show"
            elif qualified:
                outcome = rng.choice(["no_reply","still_open","budget_mismatch"], p=[0.5,0.3,0.2])
            else:
                outcome = rng.choice(["no_reply","lowball","budget_mismatch","requirement_mismatch"], p=[0.45,0.25,0.15,0.15])

            rows.append(dict(
                enquiry_id=f"E{eid:05d}", listing_id=L.listing_id, datetime=dt,
                source=src, contact_method=method, campaign=campaign,
                move_in_days=move_in, qualified=qualified, responded=responded,
                first_response_min=resp_min, after_hours=ah,
                viewing_booked=viewing_booked, viewing_attended=viewing_attended,
                outcome=outcome))
            eid += 1

enq = pd.DataFrame(rows).sort_values("datetime").reset_index(drop=True)
enq["enquiry_id"] = [f"E{i:05d}" for i in range(len(enq))]

# Plant the 7 tenancies: convert one attended-viewing enquiry per signing
signings = [
    ("L07","google_ads","2026-01-02"), ("L10","google_ads","2026-03-26"),
    ("L01","propertyguru","2026-02-18"), ("L05","propertyguru","2026-05-12"),
    ("L06","referral","2026-03-09"), ("L08","referral","2026-04-06"),
    ("L02","meta_ads","2026-04-21"),
]
for lid, src, sd in signings:
    sd_ts = pd.Timestamp(sd)
    cand = enq[(enq.listing_id==lid) & (enq.source==src) & (enq.datetime < sd_ts) & (enq.datetime > sd_ts - timedelta(days=35))]
    if len(cand)==0:  # force-create one
        dt = sd_ts - timedelta(days=int(rng.integers(10,21)), hours=int(rng.integers(1,9)))
        new = dict(enquiry_id=f"E{len(enq):05d}", listing_id=lid, datetime=dt, source=src,
                   contact_method="whatsapp", campaign=CAMPAIGNS.get(src,{}).get(listings_df.set_index('listing_id').loc[lid,'segment']),
                   move_in_days=int(rng.integers(7,25)), qualified=True, responded=True,
                   first_response_min=12.0, after_hours=False, viewing_booked=True,
                   viewing_attended=True, outcome="tenancy_signed")
        enq = pd.concat([enq, pd.DataFrame([new])], ignore_index=True)
    else:
        idx = cand.index[-1]
        enq.loc[idx, ["qualified","responded","viewing_booked","viewing_attended","outcome"]] = [True,True,True,True,"tenancy_signed"]
        if pd.isna(enq.loc[idx,"first_response_min"]): enq.loc[idx,"first_response_min"]=15.0

enq = enq.sort_values("datetime").reset_index(drop=True)
enq["enquiry_id"] = [f"E{i:05d}" for i in range(len(enq))]
enq["date"] = enq["datetime"].dt.date
enq["month"] = enq["datetime"].dt.to_period("M").astype(str)

# ---------------------------------------------------------------
# 4. AD SPEND (campaign-level) & PLATFORM COSTS (portfolio-level)
# ---------------------------------------------------------------
months = pd.period_range("2025-12","2026-05",freq="M").astype(str)
ad_rows=[]
for m in months:
    # Google RM600/mo split across 3 campaigns; Meta RM400/mo across 2
    g = np.array([0.45,0.30,0.25]) * 600 * rng.uniform(0.92,1.08)
    ad_rows += [dict(month=m, source="google_ads", campaign="G-Search WholeUnits Cheras/KL", spend_myr=round(g[0],2), target_segment="whole_unit"),
                dict(month=m, source="google_ads", campaign="G-Search Studios MRT", spend_myr=round(g[1],2), target_segment="studio"),
                dict(month=m, source="google_ads", campaign="G-Search Rooms MRT", spend_myr=round(g[2],2), target_segment="room")]
    me = np.array([0.65,0.35]) * 400 * rng.uniform(0.92,1.08)
    ad_rows += [dict(month=m, source="meta_ads", campaign="Meta Rooms YoungPro", spend_myr=round(me[0],2), target_segment="room"),
                dict(month=m, source="meta_ads", campaign="Meta Studio Budget", spend_myr=round(me[1],2), target_segment="studio")]
ad_spend = pd.DataFrame(ad_rows)

platform_costs = pd.DataFrame([dict(month=m, source=s, cost_myr=c)
    for m in months for s,c in [("propertyguru",450.0),("mudah",60.0)]])

# ---------------------------------------------------------------
# 5. SAVE + VALIDATE
# ---------------------------------------------------------------
out = "/home/claude/dataset/"
import os; os.makedirs(out, exist_ok=True)
listings_out = listings_df.drop(columns=["_base_w"])
listings_out.to_csv(out+"listings.csv", index=False)
enq.drop(columns=["date"]).to_csv(out+"enquiries.csv", index=False)
ad_spend.to_csv(out+"ad_spend.csv", index=False)
platform_costs.to_csv(out+"platform_costs.csv", index=False)

# ---- validation report ----
print(f"Enquiries: {len(enq)}  | window {enq.datetime.min()} → {enq.datetime.max()}")
print("\n— Volume share by source —")
print((enq.source.value_counts(normalize=True)*100).round(1))
print("\n— Qualified rate by source —")
print((enq.groupby("source").qualified.mean()*100).round(1))
print("\n— Enquiry→viewing rate by source —")
print((enq.groupby("source").viewing_booked.mean()*100).round(1))
print("\n— Tenancies by source —")
print(enq[enq.outcome=="tenancy_signed"].source.value_counts())
total_cost = {"google_ads":3600,"meta_ads":2400,"propertyguru":2700,"mudah":360,"referral":0}
ten = enq[enq.outcome=="tenancy_signed"].source.value_counts()
print("\n— Cost per enquiry / per tenancy (RM) —")
for s,c in total_cost.items():
    n=(enq.source==s).sum(); t=ten.get(s,0)
    print(f"{s:13s} CPE {c/n:7.2f}   CPT {'∞' if t==0 else round(c/t)}")
print("\n— After-hours unanswered check —")
print(enq.groupby("after_hours").apply(lambda d:(d.outcome=="unanswered").mean()*100).round(1))
print("\n— L09 stale check: enquiries by week-of-life —")
l9=enq[enq.listing_id=="L09"].copy()
l9["wk"]=((l9.datetime-pd.Timestamp("2026-02-01")).dt.days//7)
print(l9.groupby("wk").size())
print("\n— Monthly enquiry volume —")
print(enq.groupby("month").size())
