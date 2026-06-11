"""
Owner Report Generator — Lead Source Intelligence
=================================================
Reads the four committed CSVs, aggregates any listing x month, and renders a
branded, plain-language one-page owner report from owner_report_template.html.j2.

P4 of the build. One data model, two audiences: this is the landlord-facing
audience. Only the "Both" rows of the KPI dictionary appear here, translated to
plain language. No cost figures are shown to the owner (those are the agency's).

Run:  python generate_owner_reports.py
Output: owner-reports/out/<listing_id>-<month>-<skin>.html

Cloneability proof: a new owner is one new row in listings.csv; a new agency is
one new skin in the template. Nothing in this script is listing-specific.
"""

import calendar
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

AGENT_NAME, AGENT_PEA = "Adeline Khoo", "PEA 9183"

SOURCE_LABEL = {
    "propertyguru": "PropertyGuru",
    "mudah": "Mudah.my",
    "google_ads": "Google Ads",
    "meta_ads": "Meta Ads",
    "referral": "WhatsApp referral",
}
# How each channel is described in the plain-language "what we did" line.
SOURCE_ACTION = {
    "propertyguru": "Kept your listing featured on PropertyGuru",
    "mudah": "Maintained the free Mudah.my listing",
    "google_ads": "Ran targeted Google search ads for your unit",
    "meta_ads": "Ran Meta (Facebook/Instagram) ads for your unit",
    "referral": "Worked our tenant referral network",
}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def load():
    enq = pd.read_csv(ROOT / "enquiries.csv", parse_dates=["datetime"])
    lst = pd.read_csv(ROOT / "listings.csv", parse_dates=["listed_date", "signed_date"])
    return enq, lst


def month_label(month):  # "2026-03" -> ("March 2026", "March")
    y, m = map(int, month.split("-"))
    name = calendar.month_name[m]
    return f"{name} {y}", name


def listing_row(lst, listing_id):
    return lst[lst.listing_id == listing_id].iloc[0]


def comparable_anchor(lst, enq, row):
    """Find a signed listing of the same segment with a lower rent — the honest
    'a similar unit nearby at RM X' anchor. Returns (name, rent) or None."""
    cand = lst[
        (lst.segment == row.segment)
        & (lst.listing_id != row.listing_id)
        & (lst.status == "signed")
        & (lst.asking_rent_myr < row.asking_rent_myr)
    ].copy()
    if cand.empty:
        return None
    cand = cand.sort_values("asking_rent_myr", ascending=False)  # closest below
    c = cand.iloc[0]
    return c.property_name, int(c.asking_rent_myr)


# ---------------------------------------------------------------------------
# Per listing x month figures
# ---------------------------------------------------------------------------
def figures(enq, lst, listing_id, month):
    row = listing_row(lst, listing_id)
    m = enq[(enq.listing_id == listing_id) & (enq.month == month)]
    cumulative = len(enq[(enq.listing_id == listing_id) & (enq.month <= month)])

    # previous month volume for the trend sentence
    months_sorted = sorted(enq[enq.listing_id == listing_id].month.unique())
    prev_vol = None
    if month in months_sorted:
        i = months_sorted.index(month)
        if i > 0:
            prev_vol = len(enq[(enq.listing_id == listing_id) & (enq.month == months_sorted[i - 1])])

    signed_this_month = (
        pd.notna(row.signed_date) and row.signed_date.strftime("%Y-%m") == month
    )

    # velocity: avg enquiries/week first 2 weeks of life vs the report month
    listed = row.listed_date
    early = enq[
        (enq.listing_id == listing_id)
        & (enq.datetime < listed + timedelta(days=14))
    ]
    early_weekly = len(early) / 2 if len(early) else 0
    # report-month weekly rate
    y, mo = map(int, month.split("-"))
    days_in_month = calendar.monthrange(y, mo)[1]
    month_weekly = len(m) / (days_in_month / 7)
    velocity_drop = (
        (early_weekly - month_weekly) / early_weekly if early_weekly > 0 else 0
    )
    weeks_on_market = max(0, (date(y, mo, days_in_month) - listed.date()).days // 7)

    return dict(
        row=row,
        new_enq=len(m),
        serious=int(m.qualified.sum()),
        viewings=int(m.viewing_attended.sum()),
        cumulative=cumulative,
        prev_vol=prev_vol,
        signed_this_month=signed_this_month,
        sources=m.source.value_counts().to_dict(),
        velocity_drop=velocity_drop,
        weeks_on_market=weeks_on_market,
        is_active=(row.status == "active"),
    )


# ---------------------------------------------------------------------------
# Narrative
# ---------------------------------------------------------------------------
def n_word(n):
    return {0: "no", 1: "one", 2: "two", 3: "three"}.get(n, str(n))


def trend_phrase(new_enq, prev_vol):
    if prev_vol is None or prev_vol == 0:
        return "This is the first full month of marketing activity"
    if new_enq >= prev_vol * 1.15:
        return "Interest has picked up compared with last month"
    if new_enq <= prev_vol * 0.85:
        return "Interest has been steady but slower than last month"
    return "Interest has held steady compared with last month"


def what_this_means(f, anchor):
    s = f["serious"]
    parts = [
        f"Your unit attracted {f['new_enq']} {'enquiry' if f['new_enq']==1 else 'enquiries'} "
        f"this month, with {n_word(s)} from genuinely suitable {'tenant' if s==1 else 'tenants'} "
        f"and {n_word(f['viewings'])} {'viewing' if f['viewings']==1 else 'viewings'} completed."
    ]
    trend = trend_phrase(f["new_enq"], f["prev_vol"])
    if f["is_active"] and f["velocity_drop"] >= 0.5 and anchor:
        name, rent = anchor
        parts.append(
            f"{trend}, and slower than a comparable unit nearby asking RM{rent:,}. "
            "In plain terms: people are looking, but the price is making some of them hesitate."
        )
    elif f["signed_this_month"]:
        parts.append(f"{trend}, and this is the month your unit was successfully tenanted.")
    else:
        parts.append(f"{trend}.")
    return " ".join(parts)


def did_items(f):
    items = []
    for src, cnt in sorted(f["sources"].items(), key=lambda x: -x[1]):
        action = SOURCE_ACTION.get(src, f"Promoted your unit via {SOURCE_LABEL.get(src, src)}")
        items.append(
            f"{action}, which produced {cnt} of this month's "
            f"{'enquiry' if cnt==1 else 'enquiries'}"
        )
    items.append("Followed up every serious prospect within the hour and arranged viewings where ready")
    items.append(f"Reviewed pricing against comparable units in the {f['row'].area.split(',')[0]} area")
    return items


def recommendation(f, anchor):
    rent = int(f["row"].asking_rent_myr)
    if f["signed_this_month"]:
        return (
            "Your property is now tenanted. No further action needed.",
            "Congratulations: we secured a suitable tenant this month. We will hand over the "
            "signed tenancy details and deposit confirmation, and we are glad to help with the "
            "next unit whenever you are ready.",
        )
    if f["is_active"] and f["velocity_drop"] >= 0.5 and f["weeks_on_market"] >= 6:
        low = round(rent * 0.88 / 50) * 50
        high = round(rent * 0.913 / 50) * 50
        anchor_txt = ""
        if anchor:
            name, arent = anchor
            anchor_txt = (
                f" Enquiries fell after the first fortnight while a similar unit at RM{arent:,} "
                "kept receiving steady interest and has since been rented."
            )
        return (
            f"Consider adjusting the asking rent to RM{low:,} to RM{high:,}.",
            f"The market has had several weeks to respond to RM{rent:,}.{anchor_txt} "
            "Each additional empty month costs you more than the monthly difference would over a "
            "full tenancy. Alternatively, we can keep the price and sweeten the offer with a "
            "flexible move-in date or included parking. We are happy to discuss both options this week.",
        )
    if f["new_enq"] >= 4 and f["viewings"] >= 1:
        return (
            "Stay the course; interest is converting to viewings.",
            "Your unit is attracting suitable prospects and viewings are happening. We will keep "
            "the current channels running and focus on converting the active viewings into an offer.",
        )
    return (
        "Refresh the listing to lift enquiry volume.",
        "Enquiry volume is on the quieter side this month. We will refresh the listing photos and "
        "headline, and re-feature it on the portals to bring more suitable prospects through.",
    )


def next_month(f):
    if f["signed_this_month"]:
        return (
            "With your unit tenanted, no further marketing is scheduled. We will be in touch at "
            "renewal time, or sooner if you have another property to list."
        )
    if f["is_active"] and f["velocity_drop"] >= 0.5:
        return (
            "With your go-ahead on the price adjustment, we will refresh the listing photos, "
            "relaunch it as \"newly reduced\", and expect enquiry volume to recover within two weeks. "
            "We will report the results in next month's update."
        )
    return (
        "We will keep the current channels running, follow up every prospect quickly, and report "
        "the results in next month's update."
    )


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def prepared_date(month):
    y, m = map(int, month.split("-"))
    nm = date(y, m, 28) + timedelta(days=7)  # roll into next month
    nm = date(nm.year, nm.month, 2)          # report prepared on the 2nd
    return f"{nm.day} {calendar.month_name[nm.month]} {nm.year}"  # cross-platform, no leading zero


def render(enq, lst, listing_id, month, skin):
    env = Environment(loader=FileSystemLoader(str(HERE)), autoescape=False)
    tpl = env.get_template("owner_report_template.html.j2")
    f = figures(enq, lst, listing_id, month)
    row = f["row"]
    anchor = comparable_anchor(lst, enq, row)
    label, short = month_label(month)
    rec_title, rec_body = recommendation(f, anchor)

    html = tpl.render(
        skin=skin,
        property_name=row.property_name,
        subtitle=f"{row.configuration} · {int(row.size_sqf)} sqf · asking RM{int(row.asking_rent_myr):,}/month · Marketing report for {label}",
        month_label=label,
        month_short=short,
        stats=[
            {"v": f["new_enq"], "l": "New enquiries"},
            {"v": f["serious"], "l": "Serious prospects"},
            {"v": f["viewings"], "l": "Viewings held"},
            {"v": f["cumulative"], "l": "Total enquiries since listing"},
        ],
        what_this_means=what_this_means(f, anchor),
        did_items=did_items(f),
        rec_title=rec_title,
        rec_body=rec_body,
        next_month=next_month(f),
        agent_name=AGENT_NAME,
        agent_pea=AGENT_PEA,
        prepared_date=prepared_date(month),
    )
    path = OUT / f"{listing_id}-{month}-{skin}.html"
    path.write_text(html, encoding="utf-8")
    return path, f


if __name__ == "__main__":
    enq, lst = load()
    # Two demonstrations, two agency skins:
    #   L09 Sunway Velocity Two, March 2026  — the reprice story (Klang Valley Homes)
    #   L07 Lavile KL, December 2025         — the success story (Harbour & Co)
    jobs = [("L09", "2026-03", "kvh"), ("L07", "2025-12", "harbour")]
    for lid, month, skin in jobs:
        path, f = render(enq, lst, lid, month, skin)
        print(f"[{skin}] {lid} {month}: {f['new_enq']} enq / {f['serious']} serious / "
              f"{f['viewings']} viewings / {f['cumulative']} cumulative  ->  {path.name}")
