"""
Fire Claim Examiner: claim record parser.

Turns a neutral claim lodgement record (.txt) into a structured claim object.

The records carry no verdict and no hint by design, so this parser extracts
facts only. Every field it produces is something an examiner would read off the
file: dates, sums insured, endorsements held, items claimed. Nothing here
decides anything.
"""

import re
from datetime import date, datetime
from pathlib import Path

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}

DATE_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})")
MONEY_RE = re.compile(r"RM\s?([\d,]+(?:\.\d{2})?)")
CODE_RE = re.compile(r"\b(FP\d{3}[A-Z]?(?:\.\d+)?|FC\d{3}[A-Z]?|FW\d{3}[A-Z]?)\b")


def _date(text: str):
    m = DATE_RE.search(text or "")
    if not m:
        return None
    day, mon, year = m.group(1), m.group(2).lower(), m.group(3)
    if mon not in MONTHS:
        return None
    return date(int(year), MONTHS[mon], int(day))


def _field(text: str, label: str):
    m = re.search(rf"^{re.escape(label)}\s*:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else None


def _section(text: str, header: str):
    m = re.search(rf"^=+\n{re.escape(header)}.*?\n=+\n(.*?)(?=\n=====|\Z)",
                  text, re.M | re.S)
    return m.group(1) if m else ""


def parse(path) -> dict:
    text = Path(path).read_text(encoding="utf-8")

    period = _field(text, "Policy Period") or ""
    dates = DATE_RE.findall(period)
    period_from = period_to = None
    if len(dates) >= 2:
        period_from = _date(f"{dates[0][0]} {dates[0][1]} {dates[0][2]}")
        period_to = _date(f"{dates[1][0]} {dates[1][1]} {dates[1][2]}")

    # sums insured, per Schedule item
    sums, values = {}, {}
    for m in re.finditer(r"^Item (\d+)\s+(.+?)\s{2,}RM\s*([\d,]+(?:\.\d{2})?)\s*$",
                         _section(text, "SUMS INSURED"), re.M):
        sums[int(m.group(1))] = {
            "label": m.group(2).strip(),
            "sum_insured": float(m.group(3).replace(",", "")),
        }

    # assessed values, when a valuation report is in evidence
    circ = _section(text, "CIRCUMSTANCE OF LOSS")
    val = re.search(r"valuation report dated ([^,]+?),.*?as follows:(.*?)(?:\n\n|\Z)",
                    circ, re.S | re.I)
    if val:
        blob = val.group(2)
        for label, key in (("building", 1), ("contents", 2), ("stock", 3)):
            m = re.search(rf"{label}[^.]*?RM\s*([\d,]+(?:\.\d{{2}})?)", blob, re.I)
            if m:
                values[key] = float(m.group(1).replace(",", ""))

    # endorsements held, read from the endorsement block only
    endorsements = []
    for line in _section(text, "ENDORSEMENTS ON POLICY").splitlines():
        if line.strip().startswith("Schedule Excess"):
            continue
        found = CODE_RE.findall(line)
        if found:
            endorsements.append({"code": found[0], "title": line.split(found[0], 1)[1].strip()})

    items = _parse_items(_section(text, "ITEMS CLAIMED"))

    claim = {
        "claim_no": _field(text, "Claim Number"),
        "policy_no": _field(text, "Policy Number"),
        "policy_period": {"from": period_from, "to": period_to, "raw": period},
        "insured": _field(text, "Insured (Policyholder)"),
        "claimant": _field(text, "Claimant"),
        "risk_address": _field(text, "Risk Address"),
        "storeys": _parse_storeys(_field(text, "Storeys")),
        "date_of_loss": _date(_field(text, "Date of Loss") or ""),
        "date_notified": _date(_field(text, "Date Insurer Notified") or ""),
        "written_claim_received": _date(_field(text, "Written Claim Received") or ""),
        "peril_reported": _field(text, "Peril as Reported"),
        "schedule_excess": _field(text, "Schedule Excess"),
        "sums_insured": sums,
        "assessed_values": values,
        "endorsements": endorsements,
        "endorsement_codes": [e["code"] for e in endorsements],
        "items": items,
        "total_claimed": round(sum(i["claimed"] for i in items), 2),
        "circumstance": circ.strip(),
        "observations": _section(text, "FILE OBSERVATIONS").strip(),
        "source_file": Path(path).name,
    }
    claim["days_to_written_claim"] = (
        (claim["written_claim_received"] - claim["date_of_loss"]).days
        if claim["written_claim_received"] and claim["date_of_loss"] else None
    )
    return claim


def _parse_storeys(raw):
    if not raw:
        return None
    m = re.search(r"(\d+)", raw)
    low = raw.lower()
    has_mezz = "mezzanine" in low and "no mezzanine" not in low
    return {"count": int(m.group(1)) if m else None,
            "mezzanine": has_mezz, "raw": raw}


def _parse_items(block: str):
    """Item lines carry a ref, a description that may wrap over several lines,
    and an amount that may sit on any of them.

    Records are accumulated from one ref number to the next rather than matched
    line by line, because a description that wraps puts the amount on a
    continuation line. Two layouts appear across the records, with and without a
    Schedule Item column; both are handled, because the item-to-Schedule-item
    mapping is what the condition of average is applied against.
    """
    lines = [ln for ln in block.splitlines()
             if ln.strip() and not set(ln.strip()) <= {"-", "="}]

    # split into records: a new record starts at a line beginning with a ref
    records, current = [], None
    for ln in lines:
        if re.match(r"^\s*(Ref|Description)\b", ln.strip(), re.I):
            continue
        if re.match(r"^\s*TOTAL CLAIMED", ln, re.I):
            break
        start = re.match(r"^(\d+)\s{2,}(.*)$", ln)
        if start:
            if current:
                records.append(current)
            current = {"ref": int(start.group(1)), "lines": [start.group(2)]}
        elif current is not None:
            current["lines"].append(ln.strip())
    if current:
        records.append(current)

    items = []
    for rec in records:
        blob = " ".join(rec["lines"])
        amounts = re.findall(r"([\d,]+\.\d{2})", blob)
        if not amounts:
            continue
        claimed = float(amounts[-1].replace(",", ""))

        sched = re.search(r"\bItem (\d+)\b", blob)
        desc = blob
        if sched:
            desc = desc.replace(sched.group(0), " ")
        desc = desc.replace(amounts[-1], " ")
        desc = re.sub(r"\s+", " ", desc).strip(" ,.-")

        items.append({
            "ref": rec["ref"],
            "desc": desc,
            "schedule_item": int(sched.group(1)) if sched else None,
            "claimed": claimed,
        })
    return items


def parse_all(folder) -> list:
    out = [parse(p) for p in sorted(Path(folder).glob("CLM-*.txt"))]
    return out


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    for c in parse_all(root / "claim case"):
        ok = abs(c["total_claimed"] - sum(i["claimed"] for i in c["items"])) < 0.01
        print(f"{c['claim_no']}  {c['peril_reported']:22} "
              f"loss {c['date_of_loss']}  period {c['policy_period']['from']} to "
              f"{c['policy_period']['to']}  items {len(c['items']):2}  "
              f"claimed {c['total_claimed']:>10,.2f}  "
              f"endorsements {','.join(c['endorsement_codes'])}")
