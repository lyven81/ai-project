"""
Build the Tasty Kitchen (好吃厨房) operational database for the RAG assistant.

Produces tasty_kitchen.db with five tables:
  menu_rotation   40 meal records, the repeating 4-week cycle
  holidays        public holiday closure dates
  customers       60 customers (20 monthly, 40 daily)
  subscriptions   20 monthly cycles with holiday extensions computed
  orders          every delivered meal line, monthly and daily

Deterministic: fixed seed, so the database rebuilds identically.
"""

import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260803
random.seed(SEED)

OUT = Path(__file__).parent / "tasty_kitchen.db"

# Rotation week 1 begins on this Monday. Any date maps back to a rotation week.
ROTATION_ANCHOR = date(2026, 8, 3)

# The simulation is evaluated as of this date.
AS_OF = date(2026, 9, 1)

HOLIDAYS = {
    date(2026, 8, 31): "Merdeka Day (Hari Kebangsaan)",
    date(2026, 9, 16): "Malaysia Day (Hari Malaysia)",
}

MEALS_PER_CYCLE = 20
MONTHLY_PRICE_PER_SERVICE = 300

# rotation_week -> weekday (0=Mon .. 4=Fri) -> service -> record
MENU = {
    1: {
        0: {"lunch": ("咖喱鸡", "Curry Chicken", "Chicken", 15, 0),
            "dinner": ("姜葱猪肉", "Ginger and Spring Onion Pork", "Pork", 15, 0)},
        1: {"lunch": ("豆酱肉片", "Bean Paste Pork Slices", "Pork", 15, 0),
            "dinner": ("冬菜肉饼", "Minced Pork with Preserved Vegetable Patty", "Pork", 15, 0)},
        2: {"lunch": ("啫啫鸡煲", "Sizzling Claypot Chicken", "Chicken", 18, 1),
            "dinner": ("姜葱多利鱼", "Ginger and Spring Onion Dory Fish", "Fish", 15, 0)},
        3: {"lunch": ("客家木耳鸡煲", "Hakka Style Chicken Claypot with Black Fungus", "Chicken", 18, 1),
            "dinner": ("瓦煲鸡", "Claypot Chicken", "Chicken", 18, 1)},
        4: {"lunch": ("酸甜猪肉片", "Sweet and Sour Pork Slices", "Pork", 15, 0),
            "dinner": ("豆豉猪肉片", "Sauteed Pork Slices with Black Bean", "Pork", 15, 0)},
    },
    2: {
        0: {"lunch": ("蒜苗猪肉", "Garlic Chives Pork", "Pork", 15, 0),
            "dinner": ("姜葱鸡丁", "Ginger and Spring Onion Chicken Dice", "Chicken", 15, 0)},
        1: {"lunch": ("豆腐焖鸡", "Braised Chicken with Tofu", "Chicken", 15, 0),
            "dinner": ("榨菜肉丝", "Shredded Pork with Pickled Mustard Green", "Pork", 15, 0)},
        2: {"lunch": ("沙姜鸡", "Sha Jiang Chicken", "Chicken", 18, 1),
            "dinner": ("娘惹巴丁鱼", "Nyonya Patin Fish", "Fish", 15, 0)},
        3: {"lunch": ("黄酒鸡煲", "Huang Jiu Chicken Claypot", "Chicken", 18, 1),
            "dinner": ("香菇滑鸡煲", "Mushroom Chicken Claypot", "Chicken", 18, 1)},
        4: {"lunch": ("豆角肉碎", "Minced Pork with Long Bean", "Pork", 15, 0),
            "dinner": ("酸甜鸡丁", "Sweet and Sour Chicken Dice", "Chicken", 15, 0)},
    },
    3: {
        0: {"lunch": ("南乳炸鸡", "Fried Chicken with Fermented Bean Curd", "Chicken", 15, 0),
            "dinner": ("宫保猪肉", "Kung Pao Pork", "Pork", 15, 0)},
        1: {"lunch": ("麻婆豆腐", "Mapo Tofu with Minced Pork", "Pork", 15, 0),
            "dinner": ("咸菜鸡", "Chicken with Pickled Mustard Green", "Chicken", 15, 0)},
        2: {"lunch": ("客家南乳焖花肉", "Hakka Braised Pork Belly with Fermented Bean Curd", "Pork", 18, 1),
            "dinner": ("潮州式蒸鱼片", "Teochew Style Steamed Fish Slices", "Fish", 15, 0)},
        3: {"lunch": ("亚三肉片", "A-Sam Style Stir-fried Pork Slices", "Pork", 18, 1),
            "dinner": ("沙姜鸡煲", "Claypot Chicken with Sand Ginger", "Chicken", 18, 1)},
        4: {"lunch": ("番茄肉片", "Pork Slices with Tomato Sauce", "Pork", 15, 0),
            "dinner": ("腐竹焖猪肉", "Braised Pork with Beancurd Stick", "Pork", 15, 0)},
    },
    4: {
        0: {"lunch": ("豆豉鸡", "Black Bean Chicken", "Chicken", 15, 0),
            "dinner": ("酒香肉片", "Wine Aroma Pork Slices", "Pork", 15, 0)},
        1: {"lunch": ("豆卜焖猪肉", "Braised Pork with Bean Curd Puff", "Pork", 15, 0),
            "dinner": ("宫保鸡丁", "Kung Pao Chicken Dice", "Chicken", 15, 0)},
        2: {"lunch": ("彩椒肉片", "Stir-fried Pork Slices with Capsicum", "Pork", 15, 0),
            "dinner": ("酿豆腐", "Stuffed Tofu", "Tofu", 18, 1)},
        3: {"lunch": ("咸鱼花腩煲", "Claypot Pork Belly with Salted Fish", "Pork", 18, 1),
            "dinner": ("卤猪肉", "Braised Pork (Lor Bak style)", "Pork", 18, 1)},
        4: {"lunch": ("蒜香肉片", "Garlic Pork Slices", "Pork", 15, 0),
            "dinner": ("干香猪肉片", "Dry-fried Pork Slices", "Pork", 15, 0)},
    },
}

ADDONS = [
    ("brown_rice", "Brown Rice Upgrade", 2),
    ("herbal_soup", "Herbal Pork Rib Soup", 13),
    ("dessert", "Today's Dessert", 5),
    ("tea", "Nourishing Tea", 13),
]

SURNAMES = ["Tan", "Lim", "Lee", "Wong", "Chan", "Ng", "Ooi", "Teoh", "Yap", "Goh",
            "Chong", "Loh", "Foo", "Khoo", "Sim", "Toh", "Chew", "Heng", "Kok", "Pang"]
INITIALS = ["A.L.", "B.K.", "C.H.", "E.M.", "H.Y.", "J.S.", "K.W.", "L.F.", "M.C.",
            "P.T.", "S.L.", "W.K.", "X.Y.", "Y.H.", "Z.M.", "C.K.", "J.L.", "S.M."]
AREAS = ["Shah Alam", "Kota Kemuning"]


def is_service_day(d):
    """Monday to Friday, excluding public holidays."""
    return d.weekday() < 5 and d not in HOLIDAYS


def rotation_week(d):
    """Map any date onto the repeating 4-week menu rotation."""
    week_index = (d - ROTATION_ANCHOR).days // 7
    return (week_index % 4) + 1


def dish_for(d, service):
    """Return the menu record for a given date and service."""
    return MENU[rotation_week(d)][d.weekday()][service]


def service_days_from(start, count):
    """Return the first `count` service days on or after `start`."""
    days, cursor = [], start
    while len(days) < count:
        if is_service_day(cursor):
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def holidays_between(start, end):
    return [h for h in HOLIDAYS if start <= h <= end and h.weekday() < 5]


def build():
    if OUT.exists():
        OUT.unlink()
    conn = sqlite3.connect(OUT)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE menu_rotation (
        rotation_week INTEGER,
        weekday_num   INTEGER,
        weekday_name  TEXT,
        service       TEXT,
        dish_zh       TEXT,
        dish_en       TEXT,
        protein       TEXT,
        price_daily   INTEGER,
        price_monthly INTEGER,
        is_premium    INTEGER
    );
    CREATE TABLE holidays (
        holiday_date TEXT PRIMARY KEY,
        holiday_name TEXT,
        is_service_day_affected INTEGER
    );
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        name        TEXT,
        area        TEXT,
        phone       TEXT,
        plan_type   TEXT,
        service     TEXT,
        joined_date TEXT,
        status      TEXT
    );
    CREATE TABLE subscriptions (
        subscription_id   TEXT PRIMARY KEY,
        customer_id       TEXT,
        service           TEXT,
        start_date        TEXT,
        service_days      INTEGER,
        meals_purchased   INTEGER,
        meals_delivered   INTEGER,
        meals_remaining   INTEGER,
        holidays_in_cycle INTEGER,
        cycle_end_date    TEXT,
        amount_rm         INTEGER,
        payment_status    TEXT,
        status            TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE orders (
        order_id     TEXT PRIMARY KEY,
        customer_id  TEXT,
        order_date   TEXT,
        weekday_name TEXT,
        service      TEXT,
        dish_zh      TEXT,
        dish_en      TEXT,
        protein      TEXT,
        meal_price   INTEGER,
        addons       TEXT,
        addons_rm    INTEGER,
        total_rm     INTEGER,
        plan_type    TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """)

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for wk in sorted(MENU):
        for wd in sorted(MENU[wk]):
            for svc in ("lunch", "dinner"):
                zh, en, protein, price, premium = MENU[wk][wd][svc]
                cur.execute(
                    "INSERT INTO menu_rotation VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (wk, wd + 1, weekday_names[wd], svc, zh, en, protein,
                     price, 15, premium))

    for hd, name in sorted(HOLIDAYS.items()):
        cur.execute("INSERT INTO holidays VALUES (?,?,?)",
                    (hd.isoformat(), name, 1 if hd.weekday() < 5 else 0))

    used_names = set()

    def make_name():
        while True:
            n = f"{random.choice(SURNAMES)} {random.choice(INITIALS)}"
            if n not in used_names:
                used_names.add(n)
                return n

    orders = []
    order_seq = 0

    def add_order(cust_id, d, svc, plan):
        nonlocal order_seq
        zh, en, protein, price_daily, _ = dish_for(d, svc)
        price = 15 if plan == "monthly" else price_daily
        picked = [a for a in ADDONS if random.random() < 0.18]
        addon_rm = sum(a[2] for a in picked)
        addon_txt = ", ".join(a[1] for a in picked) if picked else ""
        order_seq += 1
        orders.append((
            f"ORD{order_seq:04d}", cust_id, d.isoformat(),
            weekday_names[d.weekday()], svc, zh, en, protein,
            price, addon_txt, addon_rm, price + addon_rm, plan))

    # ---- 20 monthly subscribers, staggered start dates ----
    start_pool = [d for d in (date(2026, 8, 3) + timedelta(days=i) for i in range(26))
                  if is_service_day(d)]
    # Weight the 1st-of-month feel and the mid-month feel, then spread the rest.
    chosen_starts = ([date(2026, 8, 3)] * 3 + [date(2026, 8, 17)] * 3 +
                     random.sample(start_pool, 14))

    for i, start in enumerate(sorted(chosen_starts), start=1):
        cid = f"CUST{i:03d}"
        svc_choice = random.choices(["lunch", "dinner", "both"], weights=[8, 4, 8])[0]
        cur.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", (
            cid, make_name(), random.choice(AREAS),
            f"01{random.randint(2,9)}-{random.randint(200,999)} {random.randint(1000,9999)}",
            "monthly", svc_choice, start.isoformat(), "active"))

        days = service_days_from(start, MEALS_PER_CYCLE)
        end = days[-1]
        hol = holidays_between(start, end)
        n_services = 2 if svc_choice == "both" else 1
        amount = MONTHLY_PRICE_PER_SERVICE * n_services

        delivered_days = [d for d in days if d < AS_OF]
        # A "both" subscriber buys 20 lunches plus 20 dinners, so meals are
        # service days multiplied by the number of services on the plan.
        purchased = MEALS_PER_CYCLE * n_services
        delivered = len(delivered_days) * n_services

        cur.execute("INSERT INTO subscriptions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            f"SUB{i:03d}", cid, svc_choice, start.isoformat(),
            MEALS_PER_CYCLE, purchased, delivered, purchased - delivered,
            len(hol), end.isoformat(), amount, "paid",
            "completed" if len(delivered_days) >= MEALS_PER_CYCLE else "active"))

        svcs = ["lunch", "dinner"] if svc_choice == "both" else [svc_choice]
        for d in delivered_days:
            for s in svcs:
                add_order(cid, d, s, "monthly")

    # ---- 40 daily customers, varying frequency ----
    all_service_days = [d for d in (date(2026, 8, 3) + timedelta(days=i) for i in range(30))
                        if is_service_day(d) and d < AS_OF]

    for j in range(1, 41):
        cid = f"CUST{20 + j:03d}"
        svc_choice = random.choices(["lunch", "dinner", "both"], weights=[9, 6, 3])[0]
        freq = random.choices([1, 3, 12], weights=[4, 5, 3])[0]
        joined = random.choice(all_service_days[:10])
        cur.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", (
            cid, make_name(), random.choice(AREAS),
            f"01{random.randint(2,9)}-{random.randint(200,999)} {random.randint(1000,9999)}",
            "daily", svc_choice, joined.isoformat(), "active"))

        eligible = [d for d in all_service_days if d >= joined]
        picked_days = sorted(random.sample(eligible, min(freq, len(eligible))))
        svcs = ["lunch", "dinner"] if svc_choice == "both" else [svc_choice]
        for d in picked_days:
            for s in svcs:
                add_order(cid, d, s, "daily")

    cur.executemany(
        "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", orders)

    cur.executescript("""
    CREATE INDEX idx_orders_date ON orders(order_date);
    CREATE INDEX idx_orders_cust ON orders(customer_id);
    CREATE INDEX idx_menu_lookup ON menu_rotation(rotation_week, weekday_num, service);
    """)

    conn.commit()
    return conn


def report(conn):
    cur = conn.cursor()
    q = lambda s: cur.execute(s).fetchone()[0]

    print(f"Database: {OUT.name}")
    print(f"As-of date: {AS_OF}   Rotation anchor: {ROTATION_ANCHOR}")
    print()
    print(f"menu_rotation   {q('SELECT COUNT(*) FROM menu_rotation')} meal records")
    print(f"holidays        {q('SELECT COUNT(*) FROM holidays')} closure dates")
    print(f"customers       {q('SELECT COUNT(*) FROM customers')} total")
    print(f"  monthly       {q(chr(39).join(['SELECT COUNT(*) FROM customers WHERE plan_type=', 'monthly', '']))}")
    print(f"  daily         {q(chr(39).join(['SELECT COUNT(*) FROM customers WHERE plan_type=', 'daily', '']))}")
    print(f"subscriptions   {q('SELECT COUNT(*) FROM subscriptions')} monthly cycles")
    print(f"orders          {q('SELECT COUNT(*) FROM orders')} meal lines")
    print()

    rev = q("SELECT SUM(amount_rm) FROM subscriptions")
    daily_rev = q("SELECT COALESCE(SUM(total_rm),0) FROM orders WHERE plan_type='daily'")
    addon_rev = q("SELECT COALESCE(SUM(addons_rm),0) FROM orders WHERE plan_type='monthly'")
    print(f"Monthly subscription revenue   RM {rev:,}")
    print(f"Daily order revenue            RM {daily_rev:,}")
    print(f"Monthly add-on revenue         RM {addon_rev:,}")
    print(f"Total                          RM {rev + daily_rev + addon_rev:,}")
    print()

    print("Cycle end dates (staggered starts plus holiday extensions):")
    rows = cur.execute("""
        SELECT cycle_end_date, COUNT(*) FROM subscriptions
        GROUP BY cycle_end_date ORDER BY cycle_end_date""").fetchall()
    for d, n in rows:
        print(f"  {d}   {n} subscriber(s)")
    print(f"  {len(rows)} distinct end dates across 20 subscriptions")
    print()

    print("Holiday extension check:")
    for r in cur.execute("""
        SELECT subscription_id, start_date, holidays_in_cycle, cycle_end_date
        FROM subscriptions ORDER BY start_date LIMIT 6"""):
        print(f"  {r[0]}  start {r[1]}  holidays in cycle {r[2]}  ends {r[3]}")
    print()

    print("Protein mix across the 4-week rotation:")
    for r in cur.execute("""
        SELECT protein, COUNT(*) FROM menu_rotation
        GROUP BY protein ORDER BY COUNT(*) DESC"""):
        print(f"  {r[0]:<10} {r[1]}")
    print()

    print("Sample: delivery list for 2026-08-27 (a premium Thursday)")
    for r in cur.execute("""
        SELECT service, COUNT(*) FROM orders
        WHERE order_date='2026-08-27' GROUP BY service"""):
        print(f"  {r[0]:<8} {r[1]} meals")


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    c = build()
    report(c)
    c.close()
