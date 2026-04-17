"""Generate 7-day demo booking seed for Plumber WhatsApp Agent.

Rules enforced:
- 1-hour slots, 09:00-17:00 (last slot starts 17:00, ends 18:00), Mon 30 Mar - Sun 5 Apr 2026.
- Solo plumber: Jamal. One job at a time.
- Multi-slot: jobs > 60 min book consecutive slots.
- ~50% of total capacity booked (31-32 of 63 slot-units).
- Each day has at least 2 free slots.
- Realistic Malaysian customer names, PJ/Subang/Shah Alam addresses.
"""

import json
import math
import os
import random
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(42)

SERVICES = [
    # name, name_ms, duration_slots, price_rm, includes
    ("Pipe Leak Repair", "Paip bocor", 2, 200, "Labour + basic materials (tape, sealant, connector)"),
    ("Clogged Drain", "Sinki/drain tersumbat", 1, 120, "Labour + drain snake"),
    ("Tap Replacement", "Tukar tap/paip", 1, 100, "Labour only (customer supplies tap)"),
    ("Toilet Repair", "Tandas rosak", 1, 150, "Labour + standard parts"),
    ("Toilet Repair (Major)", "Tandas rosak teruk", 2, 280, "Labour + cistern set"),
    ("Water Heater Install", "Pasang/tukar water heater", 2, 300, "Labour + piping (unit by customer)"),
    ("Sink Installation", "Pasang sinki", 2, 250, "Labour + piping + sealant"),
    ("Pipe Burst (Emergency)", "Paip pecah", 2, 350, "Labour + replacement pipe + fittings"),
    ("Water Pump Repair", "Repair/tukar water pump", 2, 300, "Labour + wiring (pump by customer)"),
    ("Bathroom Renovation Plumbing", "Plumbing renovation bilik air", 3, 600, "Labour + all piping and fittings"),
]

# Weights: favor common jobs. Rare complex jobs appear 1-2 times total.
SERVICE_WEIGHTS = [20, 18, 12, 15, 3, 5, 4, 2, 3, 1]

SLOTS = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

NAMES = [
    "Ahmad Faizal", "Siti Nurhaliza", "Muhammad Danial", "Nur Aisyah",
    "Ismail bin Hussein", "Fatimah binti Abdullah", "Azman Yusof",
    "Rohana Abdul Rahman", "Zainab binti Omar", "Hakim bin Razak",
    "Noraini Ibrahim", "Syafiq Hassan", "Tan Mei Ling", "Lim Boon Keng",
    "Lee Choon Hock", "Chong Ah Fook", "Ng Chee Ming", "Chan Wai Kit",
    "Sarah Wong", "David Lee", "Jessica Tan", "Kenneth Ooi",
    "Raj Kumar", "Ramesh a/l Singh", "Priya Devi",
    "Suresh a/l Murugan", "Anitha Kumari", "Vijay Kumar",
]

ADDRESSES_PJ = [
    "12, Jalan SS2/55, Petaling Jaya",
    "8, Jalan 17/12, Seksyen 17, Petaling Jaya",
    "25A, Jalan SS22/19, Damansara Jaya",
    "3-2, Pangsapuri Kelana Puteri, Kelana Jaya",
    "17, Jalan 5/32A, Seksyen 5, Petaling Jaya",
]

ADDRESSES_SUBANG = [
    "22, Jalan USJ 6/2P, Subang Jaya",
    "10, Jalan SS15/4A, Subang Jaya",
    "45, Jalan USJ 2/1, Subang Jaya",
    "8-3, Pangsapuri USJ 1, Subang Jaya",
    "31, Jalan SS18/6, Subang Jaya",
]

ADDRESSES_SA = [
    "15, Jalan Bougainvillea 3, Shah Alam",
    "7, Jalan Kristal 7/47, Seksyen 7, Shah Alam",
    "28, Persiaran Kayangan, Shah Alam",
    "4-1, Pangsapuri Seksyen 18, Shah Alam",
    "19, Jalan Alam Megah 1, Shah Alam",
]

ALL_ADDRESSES = ADDRESSES_PJ + ADDRESSES_SUBANG + ADDRESSES_SA


def random_phone():
    return f"01{random.choice([0,1,2,3,6,7,8,9])}-{random.randint(100,999)} {random.randint(1000,9999)}"


def slot_index(slot_str):
    return SLOTS.index(slot_str)


# Daily target slot-units. Total capacity = 63. Target ~50% = 31-32.
# Weekdays slightly busier, Sunday lightest.
TARGET = {
    "2026-03-30": 5,   # Mon
    "2026-03-31": 3,   # Tue
    "2026-04-01": 5,   # Wed
    "2026-04-02": 4,   # Thu
    "2026-04-03": 5,   # Fri
    "2026-04-04": 5,   # Sat
    "2026-04-05": 4,   # Sun
}
# Total: 31 slot-units

# Anchor bookings: hand-placed multi-slot jobs for demo variety.
ANCHORS = {
    "2026-03-30": [("09:00", "Pipe Leak Repair"), ("14:00", "Water Heater Install")],
    "2026-04-01": [("10:00", "Sink Installation"), ("15:00", "Pipe Burst (Emergency)")],
    "2026-04-03": [("09:00", "Bathroom Renovation Plumbing")],
    "2026-04-04": [("13:00", "Toilet Repair (Major)")],
    "2026-04-05": [("10:00", "Water Pump Repair")],
}

svc_by_name = {s[0]: s for s in SERVICES}


def generate_days():
    out = []
    d = date(2026, 3, 30)
    end = date(2026, 4, 5)
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


def main():
    bookings = []
    bid = 1

    for day in generate_days():
        date_str = day.isoformat()
        schedule = [None] * 9  # 9 slots, one plumber
        placed = 0
        target = TARGET[date_str]
        attempts = 0

        # Phase 1: place anchor bookings.
        for start_slot, svc_name in ANCHORS.get(date_str, []):
            svc = svc_by_name[svc_name]
            name_en, name_ms, dur_slots, price, includes = svc
            start_idx = slot_index(start_slot)

            if start_idx + dur_slots > 9:
                continue
            if any(schedule[start_idx + i] is not None for i in range(dur_slots)):
                continue

            cust_name = random.choice(NAMES)
            booking = {
                "booking_id": f"JOB{bid:03d}",
                "date": date_str,
                "start_slot": SLOTS[start_idx],
                "slots_occupied": dur_slots,
                "slot_list": [SLOTS[start_idx + i] for i in range(dur_slots)],
                "service": name_en,
                "service_ms": name_ms,
                "duration_hours": dur_slots,
                "price_rm": price,
                "includes": includes,
                "customer_name": cust_name,
                "address": random.choice(ALL_ADDRESSES),
                "phone": random_phone(),
                "status": "confirmed",
            }
            bookings.append(booking)
            bid += 1
            for i in range(dur_slots):
                schedule[start_idx + i] = booking["booking_id"]
            placed += dur_slots

        # Phase 2: random fill until target reached.
        while placed < target and attempts < 200:
            attempts += 1
            # Only pick 1-slot jobs for random fill to avoid over-booking
            single_slot_svcs = [s for s in SERVICES if s[2] == 1]
            single_weights = [SERVICE_WEIGHTS[SERVICES.index(s)] for s in single_slot_svcs]
            svc = random.choices(single_slot_svcs, weights=single_weights)[0]
            name_en, name_ms, dur_slots, price, includes = svc

            start_idx = random.randint(0, 8)
            if schedule[start_idx] is not None:
                continue

            # Ensure at least 2 free slots remain after placing
            free_after = sum(1 for s in schedule if s is None) - 1
            if free_after < 2:
                break

            cust_name = random.choice(NAMES)
            booking = {
                "booking_id": f"JOB{bid:03d}",
                "date": date_str,
                "start_slot": SLOTS[start_idx],
                "slots_occupied": dur_slots,
                "slot_list": [SLOTS[start_idx]],
                "service": name_en,
                "service_ms": name_ms,
                "duration_hours": dur_slots,
                "price_rm": price,
                "includes": includes,
                "customer_name": cust_name,
                "address": random.choice(ALL_ADDRESSES),
                "phone": random_phone(),
                "status": "confirmed",
            }
            bookings.append(booking)
            bid += 1
            schedule[start_idx] = booking["booking_id"]
            placed += dur_slots

    # Stats
    total_units = sum(b["slots_occupied"] for b in bookings)
    capacity = 9 * 7
    density = round(total_units / capacity * 100, 1)

    day_stats = {}
    for day in generate_days():
        ds = day.isoformat()
        day_bookings = [b for b in bookings if b["date"] == ds]
        units = sum(b["slots_occupied"] for b in day_bookings)
        free = 9 - units
        day_stats[ds] = {
            "bookings": len(day_bookings),
            "slot_units": units,
            "free_slots": free,
            "pct": round(units / 9 * 100, 1),
        }

    result = {
        "meta": {
            "business_name": "Jamal Plumbing Services",
            "plumber": "Jamal",
            "service_area": ["Petaling Jaya", "Subang Jaya", "Shah Alam"],
            "demo_period_start": "2026-03-30",
            "demo_period_end": "2026-04-05",
            "operating_hours": "09:00-18:00",
            "slot_duration_minutes": 60,
            "slots_per_day": 9,
            "days_open": "Monday to Sunday",
            "total_bookings": len(bookings),
            "total_slot_units": total_units,
            "capacity_slot_units": capacity,
            "overall_density_pct": density,
            "day_stats": day_stats,
        },
        "services": [
            {
                "name": s[0],
                "name_ms": s[1],
                "duration_slots": s[2],
                "price_rm": s[3],
                "includes": s[4],
            }
            for s in SERVICES
        ],
        "bookings": bookings,
    }

    out_path = os.path.join(HERE, "plumber_bookings.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {out_path}")
    print(f"Bookings: {len(bookings)} | Slot-units: {total_units} / {capacity} ({density}%)")
    for ds, stats in day_stats.items():
        print(f"  {ds}: {stats['bookings']} bookings, "
              f"{stats['slot_units']}/9 ({stats['pct']}%), "
              f"{stats['free_slots']} free slots")


if __name__ == "__main__":
    main()
