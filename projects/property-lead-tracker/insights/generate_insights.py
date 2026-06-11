"""
Insights Layer — Lead Source Intelligence
=========================================
P5 of the build. Threshold rules run over the monthly aggregates and emit
draft recommendation sentences in the voice of the dashboard's panel notes.
The agent reads, edits, and sends them; the rules guarantee nothing important
is missed and that the written note never contradicts the dashboard.

Run:  python generate_insights.py                 # sample month 2026-02
      python generate_insights.py --month 2026-05 # any month
      python generate_insights.py --all            # every month
      python generate_insights.py --polish         # optional Anthropic polish (needs ANTHROPIC_API_KEY)

Output: insights/<month>-notes.md

Each rule returns (severity, sentence). Severity drives ordering and the tag:
  flag  = something is leaking money / needs a decision now
  watch = worth keeping an eye on
  win   = a positive pattern worth reinforcing
"""

import argparse
import calendar
import os
from datetime import timedelta
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SOURCE_LABEL = {
    "propertyguru": "PropertyGuru", "mudah": "Mudah.my", "google_ads": "Google Ads",
    "meta_ads": "Meta Ads", "referral": "WhatsApp referral",
}
TAG = {"flag": "🚩 FLAG", "watch": "👀 WATCH", "win": "✅ WIN"}
ORDER = {"flag": 0, "watch": 1, "win": 2}


# ---------------------------------------------------------------------------
def load():
    enq = pd.read_csv(ROOT / "enquiries.csv", parse_dates=["datetime"])
    lst = pd.read_csv(ROOT / "listings.csv", parse_dates=["listed_date", "signed_date"])
    return enq, lst


def month_label(month):
    y, m = map(int, month.split("-"))
    return f"{calendar.month_name[m]} {y}"


def prev_month(month):
    y, m = map(int, month.split("-"))
    return f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"


def pct(x):
    return f"{round(100*x)}%"


# ---------------------------------------------------------------------------
# Rules  — each yields zero or more (severity, sentence)
# ---------------------------------------------------------------------------
def rule_volume_trend(enq, month):
    cur = len(enq[enq.month == month])
    pm = prev_month(month)
    prev = len(enq[enq.month == pm])
    if prev == 0:
        return
    change = (cur - prev) / prev
    if change <= -0.20:
        yield ("watch",
               f"Total enquiry volume fell {pct(-change)} month-on-month, from {prev} in "
               f"{month_label(pm)} to {cur} in {month_label(month)}. As listings sign, the pipeline "
               "thins; recommend onboarding 3 to 4 new listings before it shows in revenue.")
    elif change >= 0.20:
        yield ("win",
               f"Total enquiry volume rose {pct(change)} month-on-month, from {prev} to {cur}. "
               "Intake is healthy; keep the current channel mix running.")


def rule_after_hours(enq, month):
    m = enq[enq.month == month]
    ah = m[m.after_hours]
    if len(ah) == 0:
        return
    ah_unans = (ah.outcome == "unanswered").mean()
    office_unans = (m[~m.after_hours].outcome == "unanswered").mean() if len(m[~m.after_hours]) else 0
    if ah_unans > 0.15:
        yield ("flag",
               f"{len(ah)} enquiries arrived after 8pm or at weekends this month, and {pct(ah_unans)} "
               f"of them went unanswered, against {pct(office_unans)} in office hours. A WhatsApp "
               "auto-acknowledgement with three qualifying questions would hold these leads overnight "
               "at zero cost; recovering half the leak is worth real money in paid leads alone.")


def rule_source_quality(enq, month):
    m = enq[enq.month == month]
    total = len(m)
    by = m.groupby("source")
    for src, g in by:
        share = len(g) / total
        q = g.qualified.mean()
        viewings = int(g.viewing_booked.sum())
        label = SOURCE_LABEL.get(src, src)
        # Volume trap: big share, weak quality, no viewings
        if share >= 0.25 and q < 0.20 and viewings <= 1:
            yield ("flag",
                   f"{label} produced {len(g)} enquiries this month ({pct(share)} of all volume) but "
                   f"only {pct(q)} were qualified and it generated {viewings} viewing(s). Treat it as "
                   "free background noise, never paid boosts; the volume is not converting.")
        # Quality channel worth reinforcing
        if q >= 0.55 and len(g) >= 8:
            extra = (" Formalize a referral ask at every signing to grow this channel."
                     if src == "referral" else
                     " It is the cleanest paid channel; protect its budget.")
            yield ("win",
                   f"{label} was small but high quality this month: {len(g)} enquiries at a "
                   f"{pct(q)} qualified rate.{extra}")


def rule_stale_listings(enq, lst, month):
    y, mo = map(int, month.split("-"))
    last_day = calendar.monthrange(y, mo)[1]
    month_end = pd.Timestamp(y, mo, last_day)
    for _, row in lst[lst.status == "active"].iterrows():
        early = enq[(enq.listing_id == row.listing_id) &
                    (enq.datetime < row.listed_date + timedelta(days=14))]
        early_weekly = len(early) / 2 if len(early) else 0
        m = enq[(enq.listing_id == row.listing_id) & (enq.month == month)]
        if early_weekly == 0 or len(m) == 0:
            continue
        month_weekly = len(m) / (last_day / 7)
        drop = (early_weekly - month_weekly) / early_weekly
        weeks_on = max(0, (month_end.date() - row.listed_date.date()).days // 7)
        if drop >= 0.5 and weeks_on >= 6:
            # comparable anchor: cheaper signed unit, same segment
            comp = lst[(lst.segment == row.segment) & (lst.status == "signed") &
                       (lst.asking_rent_myr < row.asking_rent_myr)].sort_values(
                       "asking_rent_myr", ascending=False)
            anchor = ""
            if not comp.empty:
                c = comp.iloc[0]
                anchor = (f" A comparable unit asking RM{int(c.asking_rent_myr):,} kept moving and "
                          "has since signed.")
            yield ("flag",
                   f"{row.property_name} (RM{int(row.asking_rent_myr):,}) has gone stale: enquiry "
                   f"velocity is down {pct(drop)} from its opening fortnight after {weeks_on} weeks "
                   f"on market.{anchor} Recommend a price review toward "
                   f"RM{round(row.asking_rent_myr*0.88/50)*50:,} to "
                   f"RM{round(row.asking_rent_myr*0.913/50)*50:,}, not more ad spend.")


def rule_mismatch(enq, lst, month):
    # planted: J.Dupion female room getting male enquiries via Mudah
    fem = lst[lst.gender_rule == "female"]
    for _, row in fem.iterrows():
        m = enq[(enq.listing_id == row.listing_id) & (enq.month == month) &
                (enq.source == "mudah")]
        if len(m) == 0:
            continue
        mismatch = (m.outcome == "requirement_mismatch").mean()
        if mismatch >= 0.20:
            yield ("watch",
                   f"{row.property_name} is a female-only room, but {pct(mismatch)} of its Mudah.my "
                   "enquiries this month were requirement mismatches (mostly male applicants). Fix the "
                   "listing copy and the Mudah category to filter at the source and stop wasting replies.")


def rule_signings(enq, lst, month):
    signed = lst[lst.signed_date.notna() & (lst.signed_date.dt.strftime("%Y-%m") == month)]
    for _, row in signed.iterrows():
        yield ("win",
               f"{row.property_name} signed this month via {SOURCE_LABEL.get(row.signed_source, row.signed_source)}. "
               "Capture a tenant referral at handover; referrals are the zero-cost channel.")


RULES_ENQ = [rule_volume_trend, rule_after_hours, rule_source_quality]
RULES_ENQ_LST = [rule_stale_listings, rule_mismatch, rule_signings]


def collect(enq, lst, month):
    out = []
    for r in RULES_ENQ:
        out += list(r(enq, month))
    for r in RULES_ENQ_LST:
        out += list(r(enq, lst, month))
    out.sort(key=lambda x: ORDER[x[0]])
    return out


# ---------------------------------------------------------------------------
def maybe_polish(sentences):
    """Optional: pass the draft notes through Claude for a final copy edit.
    Falls back to the deterministic drafts when no API key is present, so the
    pipeline always produces output."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return sentences, False
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        joined = "\n".join(f"- {s}" for _, s in sentences)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            messages=[{"role": "user", "content":
                "Lightly copy-edit these property-marketing insight notes for an agent to send. "
                "Keep every number and recommendation. Plain, calm, direct. Never use em-dashes. "
                "Return the same number of bullet points, same order:\n\n" + joined}],
        )
        text = msg.content[0].text.strip()
        polished = [ln.lstrip("- ").strip() for ln in text.splitlines() if ln.strip().startswith("-")]
        if len(polished) == len(sentences):
            return [(sev, polished[i]) for i, (sev, _) in enumerate(sentences)], True
    except Exception as e:
        print(f"  (polish skipped: {e})")
    return sentences, False


def write_notes(enq, lst, month, polish=False):
    items = collect(enq, lst, month)
    if polish:
        items, used = maybe_polish(items)
    label = month_label(month)
    total = len(enq[enq.month == month])
    lines = [
        f"# Monthly insight notes — {label}",
        "",
        f"*Auto-drafted from the lead data ({total} enquiries this month). "
        "Threshold-rule drafts for the agent to review and send. Flags first.*",
        "",
    ]
    for sev, sentence in items:
        lines.append(f"- **{TAG[sev]}** — {sentence}")
    lines.append("")
    path = HERE / f"{month}-notes.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path, len(items)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default="2026-02")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--polish", action="store_true")
    args = ap.parse_args()

    enq, lst = load()
    months = sorted(enq.month.unique()) if args.all else [args.month]
    for mth in months:
        path, n = write_notes(enq, lst, mth, polish=args.polish)
        print(f"{mth}: {n} insight notes -> {path.name}")
