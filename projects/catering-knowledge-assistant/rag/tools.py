"""
Governed database tools.

Record questions ("how many meals do I have left", "what is tomorrow's
delivery list") are arithmetic over structured data. Vector retrieval answers
them badly, because similarity search cannot count, cannot compare dates and
cannot resolve a per-customer balance.

Every tool here is a fixed, parameterised query. The model chooses which tool
to call and supplies arguments; it never writes SQL, never sees the schema and
cannot list tables or dump records. That boundary is what makes the database
safe to expose to a chat interface.
"""

import sqlite3
from datetime import date, datetime, timedelta

from .config import DB_PATH

# The simulation is evaluated as of this date, matching build_database.py.
SIM_TODAY = date(2026, 9, 1)
ROTATION_ANCHOR = date(2026, 8, 3)


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _parse_date(s):
    if isinstance(s, date):
        return s
    s = (s or "").strip().lower()
    if s in ("", "today"):
        return SIM_TODAY
    if s == "tomorrow":
        return SIM_TODAY + timedelta(days=1)
    if s == "yesterday":
        return SIM_TODAY - timedelta(days=1)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Could not read the date '{s}'")


def _find_customer(cur, who):
    who = (who or "").strip()
    row = cur.execute(
        "SELECT * FROM customers WHERE UPPER(customer_id)=UPPER(?)", (who,)
    ).fetchone()
    if row:
        return row
    rows = cur.execute(
        "SELECT * FROM customers WHERE name LIKE ?", (f"%{who}%",)
    ).fetchall()
    if len(rows) == 1:
        return rows[0]
    if len(rows) > 1:
        names = ", ".join(f"{r['name']} ({r['customer_id']})" for r in rows[:6])
        raise LookupError(f"More than one customer matches '{who}': {names}")
    raise LookupError(f"No customer found matching '{who}'")


# ---------------------------------------------------------------- tools ----

def get_customer_summary(customer: str) -> dict:
    """Plan, service and area for one customer."""
    with _conn() as c:
        r = _find_customer(c.cursor(), customer)
        return {"tool": "get_customer_summary", "customer_id": r["customer_id"],
                "name": r["name"], "area": r["area"], "plan_type": r["plan_type"],
                "service": r["service"], "joined_date": r["joined_date"],
                "status": r["status"]}


def get_meals_remaining(customer: str) -> dict:
    """Meals delivered and remaining for a monthly subscriber."""
    with _conn() as c:
        cur = c.cursor()
        r = _find_customer(cur, customer)
        if r["plan_type"] != "monthly":
            n = cur.execute(
                "SELECT COUNT(*) FROM orders WHERE customer_id=?",
                (r["customer_id"],)).fetchone()[0]
            return {"tool": "get_meals_remaining", "name": r["name"],
                    "plan_type": "daily", "meals_ordered_to_date": n,
                    "note": "Daily plan customers have no meal balance. "
                            "They pay per meal ordered."}
        s = cur.execute(
            "SELECT * FROM subscriptions WHERE customer_id=?",
            (r["customer_id"],)).fetchone()
        return {"tool": "get_meals_remaining", "name": r["name"],
                "plan_type": "monthly", "service": s["service"],
                "start_date": s["start_date"],
                "meals_purchased": s["meals_purchased"],
                "meals_delivered": s["meals_delivered"],
                "meals_remaining": s["meals_remaining"],
                "cycle_end_date": s["cycle_end_date"],
                "status": s["status"], "as_of": SIM_TODAY.isoformat()}


def get_cycle_end_date(customer: str) -> dict:
    """Cycle end date for a monthly subscriber, with holiday extensions applied."""
    with _conn() as c:
        cur = c.cursor()
        r = _find_customer(cur, customer)
        s = cur.execute(
            "SELECT * FROM subscriptions WHERE customer_id=?",
            (r["customer_id"],)).fetchone()
        if not s:
            return {"tool": "get_cycle_end_date", "name": r["name"],
                    "note": "This customer is on the daily plan and has no cycle."}
        hol = cur.execute(
            "SELECT holiday_date, holiday_name FROM holidays "
            "WHERE holiday_date BETWEEN ? AND ?",
            (s["start_date"], s["cycle_end_date"])).fetchall()
        return {"tool": "get_cycle_end_date", "name": r["name"],
                "start_date": s["start_date"],
                "cycle_end_date": s["cycle_end_date"],
                "service_days": s["service_days"],
                "holidays_in_cycle": s["holidays_in_cycle"],
                "holidays": [dict(h) for h in hol],
                "explanation": "The cycle is extended by one service day for "
                               "each public holiday inside it."}


def get_delivery_list(order_date: str = "today", service: str = "all") -> dict:
    """Meal counts to prepare for a given date, broken down by dish."""
    d = _parse_date(order_date)
    with _conn() as c:
        cur = c.cursor()
        hol = cur.execute(
            "SELECT holiday_name FROM holidays WHERE holiday_date=?",
            (d.isoformat(),)).fetchone()
        if hol:
            return {"tool": "get_delivery_list", "date": d.isoformat(),
                    "closed": True, "reason": hol["holiday_name"],
                    "total_meals": 0}
        if d.weekday() >= 5:
            return {"tool": "get_delivery_list", "date": d.isoformat(),
                    "closed": True, "reason": "Weekend, no service",
                    "total_meals": 0}
        sql = ("SELECT service, dish_en, dish_zh, COUNT(*) n FROM orders "
               "WHERE order_date=?")
        args = [d.isoformat()]
        if service in ("lunch", "dinner"):
            sql += " AND service=?"
            args.append(service)
        sql += " GROUP BY service, dish_en ORDER BY service"
        rows = cur.execute(sql, args).fetchall()
        return {"tool": "get_delivery_list", "date": d.isoformat(),
                "weekday": d.strftime("%A"), "closed": False,
                "breakdown": [dict(r) for r in rows],
                "total_meals": sum(r["n"] for r in rows)}


def get_menu_for_date(order_date: str = "today", service: str = "all") -> dict:
    """The dish served on any date, resolved through the 4-week rotation."""
    d = _parse_date(order_date)
    if d.weekday() >= 5:
        return {"tool": "get_menu_for_date", "date": d.isoformat(),
                "closed": True, "reason": "Weekend, no service"}
    with _conn() as c:
        cur = c.cursor()
        hol = cur.execute(
            "SELECT holiday_name FROM holidays WHERE holiday_date=?",
            (d.isoformat(),)).fetchone()
        if hol:
            return {"tool": "get_menu_for_date", "date": d.isoformat(),
                    "closed": True, "reason": hol["holiday_name"]}
        rot = ((d - ROTATION_ANCHOR).days // 7) % 4 + 1
        sql = ("SELECT service, dish_zh, dish_en, protein, price_daily, "
               "price_monthly, is_premium FROM menu_rotation "
               "WHERE rotation_week=? AND weekday_num=?")
        args = [rot, d.weekday() + 1]
        if service in ("lunch", "dinner"):
            sql += " AND service=?"
            args.append(service)
        rows = cur.execute(sql, args).fetchall()
        return {"tool": "get_menu_for_date", "date": d.isoformat(),
                "weekday": d.strftime("%A"), "rotation_week": rot,
                "closed": False, "meals": [dict(r) for r in rows]}


def get_dishes_by_protein(protein: str) -> dict:
    """Every meal in the rotation with a given protein."""
    p = (protein or "").strip().lower()
    alias = {"seafood": "fish", "vegetarian": "tofu", "veg": "tofu",
             "beef": "beef", "poultry": "chicken"}
    p = alias.get(p, p)
    with _conn() as c:
        rows = c.execute(
            "SELECT rotation_week, weekday_name, service, dish_zh, dish_en, "
            "price_daily FROM menu_rotation WHERE LOWER(protein) LIKE ? "
            "ORDER BY rotation_week, weekday_num, service", (f"%{p}%",)
        ).fetchall()
        return {"tool": "get_dishes_by_protein", "protein": p,
                "count": len(rows), "dishes": [dict(r) for r in rows],
                "note": "" if rows else
                        f"There is no {p} dish anywhere in the 4-week rotation."}


TOOLS = {
    "get_customer_summary": get_customer_summary,
    "get_meals_remaining": get_meals_remaining,
    "get_cycle_end_date": get_cycle_end_date,
    "get_delivery_list": get_delivery_list,
    "get_menu_for_date": get_menu_for_date,
    "get_dishes_by_protein": get_dishes_by_protein,
}

TOOL_SPECS = [
    {"name": "get_customer_summary",
     "description": "Look up one customer's plan, service, area and status.",
     "args": {"customer": "customer name or customer id"}},
    {"name": "get_meals_remaining",
     "description": "How many meals a monthly subscriber has left, and how many "
                    "were delivered.",
     "args": {"customer": "customer name or customer id"}},
    {"name": "get_cycle_end_date",
     "description": "When a monthly subscriber's cycle ends, including public "
                    "holiday extensions.",
     "args": {"customer": "customer name or customer id"}},
    {"name": "get_delivery_list",
     "description": "How many meals to cook and deliver on a date, by dish. "
                    "Staff facing.",
     "args": {"order_date": "a date, or today or tomorrow",
              "service": "lunch, dinner or all"}},
    {"name": "get_menu_for_date",
     "description": "Which dish is served on a specific date, resolved through "
                    "the 4-week rotation.",
     "args": {"order_date": "a date, or today or tomorrow",
              "service": "lunch, dinner or all"}},
    {"name": "get_dishes_by_protein",
     "description": "List every dish in the rotation with a given protein, for "
                    "example chicken, pork, fish, beef or tofu.",
     "args": {"protein": "chicken, pork, fish, beef or tofu"}},
]


def call_tool(name, args):
    if name not in TOOLS:
        raise KeyError(f"Unknown tool '{name}'")
    return TOOLS[name](**args)


if __name__ == "__main__":
    import json
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    with _conn() as c:
        who = c.execute(
            "SELECT name FROM customers WHERE plan_type='monthly' LIMIT 1"
        ).fetchone()["name"]
    for label, out in [
        ("meals remaining", get_meals_remaining(who)),
        ("cycle end date", get_cycle_end_date(who)),
        ("delivery list, 27 Aug", get_delivery_list("2026-08-27")),
        ("menu on 1 Sep (rotation)", get_menu_for_date("2026-09-01")),
        ("delivery list on Merdeka", get_delivery_list("2026-08-31")),
        ("beef dishes", get_dishes_by_protein("beef")),
    ]:
        print(f"--- {label} ---")
        print(json.dumps(out, ensure_ascii=False, indent=2)[:600])
        print()
