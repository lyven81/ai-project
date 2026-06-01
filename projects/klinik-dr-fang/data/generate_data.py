"""
Generate a synthetic Klinik Dr Fang dataset and load it into SQLite.

EVERYTHING here is invented. No real patients, no real data.

Deliberate, plant-ed patterns so the demo questions have something to find:
  * a respiratory symptom CLUSTER in the last ~2 weeks (early-outbreak signal)
  * a RISING condition trend (dengue) over the past 6 months
  * NO-SHOW rate creeping up, worse on Mondays / month-end
  * a few FREQUENT ATTENDERS visiting unusually often
  * a set of LAPSING patients (no visit for > 1 year)
  * spread of invoice values for segmentation

Run:  python data/generate_data.py
Out:  data/klinik.db
"""

import sqlite3, random, json, math, hashlib, os
from datetime import date, datetime, timedelta

# ----------------------------------------------------------------------------
# Reproducible. Anchored to a fixed "today" so the planted patterns are stable.
# ----------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
TODAY = date(2026, 6, 1)
HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "klinik.db")
SCHEMA_PATH = os.path.join(HERE, "schema.sql")

DOCTORS = ["Dr Fang", "Dr Fang"]  # single-doctor practice; locum rarely
EMBED_DIM = 64

# ----------------------------------------------------------------------------
# Name pools — realistic PJ mix (Malay / Chinese / Indian). Invented combos.
# ----------------------------------------------------------------------------
MALAY_M = ["Ahmad", "Mohd Faiz", "Hafiz", "Zulkifli", "Amirul", "Syafiq", "Razak", "Iskandar"]
MALAY_F = ["Nurul", "Siti Aminah", "Farah", "Aisyah", "Zarina", "Liyana", "Suraya", "Hidayah"]
CHINESE = ["Tan Wei Ming", "Lim Mei Ling", "Wong Kok Wai", "Lee Hui Shan", "Ng Chee Keong",
           "Chua Siew Lan", "Goh Jia Hui", "Teoh Boon Hock", "Yap Li Wen", "Ong Kar Mun"]
INDIAN = ["Suresh Kumar", "Devi Anandan", "Rajesh Pillai", "Kavitha Raj", "Mohan Das",
          "Priya Subramaniam", "Arun Krishnan", "Latha Menon"]

def make_name():
    pool = random.choices([MALAY_M, MALAY_F, CHINESE, INDIAN], weights=[3, 3, 4, 2])[0]
    return random.choice(pool)

# ----------------------------------------------------------------------------
# Complaint themes. Shared vocabulary within a theme makes the embeddings
# cluster honestly (token-overlap cosine). Production would swap in Vertex /
# Gemini embeddings — see README. The clustering logic is identical.
# ----------------------------------------------------------------------------
THEMES = {
    "respiratory": [
        "fever and cough", "sore throat and cough", "runny nose and fever",
        "cough with phlegm", "high fever, body ache and cough", "blocked nose and sore throat",
        "dry cough and mild fever",
    ],
    "gastro": [
        "stomach pain and diarrhea", "vomiting and nausea", "loose stools and abdominal cramps",
        "food poisoning with vomiting", "stomach upset and diarrhea",
    ],
    "dengue_like": [
        "high fever and severe body ache", "fever with headache behind eyes",
        "fever, joint pain and rash", "persistent high fever and fatigue",
    ],
    "dermato": [
        "skin rash and itching", "itchy rash on arms", "eczema flare up", "allergic skin reaction",
    ],
    "musculo": [
        "lower back pain", "knee pain after a fall", "shoulder pain", "neck stiffness and pain",
    ],
    "chronic_followup": [
        "diabetes follow up", "blood pressure check", "hypertension review", "cholesterol follow up",
    ],
    "general": [
        "headache and dizziness", "fatigue and tiredness", "ear pain", "eye irritation and redness",
    ],
}
THEME_NOTE = {
    "respiratory": "URTI symptoms, advised rest and fluids, symptomatic treatment.",
    "gastro": "Acute gastroenteritis, hydration advised, ORS given.",
    "dengue_like": "Febrile illness, dengue cannot be excluded, advised monitoring and FBC.",
    "dermato": "Dermatitis / allergic reaction, topical treatment prescribed.",
    "musculo": "Musculoskeletal pain, analgesia and rest advised.",
    "chronic_followup": "Chronic disease review, medication continued, vitals recorded.",
    "general": "Reviewed, symptomatic management, advised follow up if persists.",
}

CONDITIONS = ["Hypertension", "Type 2 Diabetes", "High Cholesterol", "Asthma",
              "Eczema", "Migraine", "Gastritis"]
DRUGS = ["Paracetamol", "Amoxicillin", "Metformin", "Amlodipine", "Cetirizine",
         "Salbutamol inhaler", "Omeprazole", "Atorvastatin", "ORS sachets"]
ALLERGIES = [None, None, None, None, "Penicillin allergy", "NSAID sensitivity", "Sulfa allergy"]

# ----------------------------------------------------------------------------
# Lightweight, dependency-free text embedding: hashed bag-of-words, L2-normed.
# Genuine cosine clustering by shared vocabulary. Deterministic.
# ----------------------------------------------------------------------------
def embed(text: str):
    vec = [0.0] * EMBED_DIM
    for tok in "".join(c.lower() if c.isalpha() else " " for c in text).split():
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16) % EMBED_DIM
        vec[h] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / norm, 6) for v in vec]

def iso(d):  return d.isoformat()
def isodt(d, h, m): return datetime(d.year, d.month, d.day, h, m).isoformat(sep=" ")

# ----------------------------------------------------------------------------
# Build the data
# ----------------------------------------------------------------------------
patients, appointments, case_notes, conditions, prescriptions, invoices = [], [], [], [], [], []
appt_id = note_id = cond_id = presc_id = inv_id = 0

N_PATIENTS = 110

# Designate special cohorts up front
frequent_ids = set(range(1, 5))          # patients 1-4 = frequent attenders
lapsing_ids = set(range(90, 106))        # patients 90-105 = lapsing (>1yr)

for pid in range(1, N_PATIENTS + 1):
    reg_days_ago = random.randint(60, 365 * 3)
    reg = TODAY - timedelta(days=reg_days_ago)
    dob = date(random.randint(1945, 2020), random.randint(1, 12), random.randint(1, 28))
    patients.append((pid, make_name(), iso(dob), f"01{random.randint(2,9)}-{random.randint(1000000,9999999)}",
                     iso(reg), random.choice(ALLERGIES)))

    # how many visits this patient has had
    if pid in frequent_ids:
        n_visits = random.randint(11, 16)
    elif pid in lapsing_ids:
        n_visits = random.randint(1, 3)
    else:
        n_visits = random.randint(2, 7)

    # chronic patients get a condition + repeat meds + follow-ups
    has_chronic = random.random() < 0.35
    if has_chronic:
        cond = random.choice(CONDITIONS)
        cond_id += 1
        diag = TODAY - timedelta(days=random.randint(120, 900))
        conditions.append((cond_id, pid, cond, iso(diag)))

    # build the visit dates for this patient
    if pid in lapsing_ids:
        # all visits are old (between 13 and 30 months ago)
        visit_dates = sorted(TODAY - timedelta(days=random.randint(395, 900)) for _ in range(n_visits))
    else:
        visit_dates = sorted(TODAY - timedelta(days=random.randint(1, 420)) for _ in range(n_visits))

    for vd in visit_dates:
        # ---- appointment + status (no-show creep: worse Mon & month-end & recent) ----
        appt_id += 1
        weekday = vd.weekday()
        recency_factor = 1.0 if (TODAY - vd).days < 90 else 0.4   # no-shows rising lately
        p_noshow = 0.05 + (0.10 if weekday == 0 else 0) + (0.08 if vd.day >= 25 else 0)
        p_noshow *= recency_factor
        status = "no-show" if random.random() < p_noshow else (
                 "cancelled" if random.random() < 0.04 else "attended")
        hour = random.randint(9, 17)
        appointments.append((appt_id, pid, isodt(vd, hour, random.choice([0, 15, 30, 45])),
                             status, random.choice(DOCTORS)))
        if status != "attended":
            continue

        # ---- choose a theme for the visit ----
        if has_chronic and random.random() < 0.4:
            theme = "chronic_followup"
        else:
            theme = random.choices(
                ["respiratory", "gastro", "dengue_like", "dermato", "musculo", "general"],
                weights=[5, 3, 2, 3, 3, 4])[0]

        complaint = random.choice(THEMES[theme])
        note_id += 1
        case_notes.append((note_id, pid, iso(vd), complaint, THEME_NOTE[theme],
                           json.dumps(embed(complaint))))

        # ---- prescription ----
        presc_id += 1
        prescriptions.append((presc_id, pid, random.choice(DRUGS), iso(vd),
                              "y" if (has_chronic and theme == "chronic_followup") else "n"))

        # ---- invoice (value spread for segmentation) ----
        inv_id += 1
        base = 45 if theme == "chronic_followup" else random.choice([35, 55, 70, 90, 120, 160])
        amount = round(base + random.uniform(-5, 25), 2)
        invoices.append((inv_id, pid, amount, iso(vd),
                         "y" if random.random() < 0.85 else "n"))

# ----------------------------------------------------------------------------
# PLANT: a respiratory cluster in the last 2 weeks (early-outbreak signal)
# ----------------------------------------------------------------------------
cluster_complaints = THEMES["respiratory"]
for i in range(10):
    pid = random.randint(1, N_PATIENTS)
    vd = TODAY - timedelta(days=random.randint(1, 13))
    appt_id += 1
    appointments.append((appt_id, pid, isodt(vd, random.randint(9, 17), 0), "attended", "Dr Fang"))
    complaint = random.choice(cluster_complaints)
    note_id += 1
    case_notes.append((note_id, pid, iso(vd), complaint, THEME_NOTE["respiratory"],
                       json.dumps(embed(complaint))))
    inv_id += 1
    invoices.append((inv_id, pid, round(random.uniform(45, 90), 2), iso(vd), "y"))

# ----------------------------------------------------------------------------
# PLANT: dengue-like cases rising over the last 6 months (monotonic-ish climb)
# ----------------------------------------------------------------------------
for months_ago in range(6, 0, -1):
    n = max(0, 7 - months_ago)  # 1,2,3,4,5,6 cases as we approach now
    for _ in range(n):
        pid = random.randint(1, N_PATIENTS)
        vd = TODAY - timedelta(days=months_ago * 30 + random.randint(-10, 10))
        if vd >= TODAY:
            vd = TODAY - timedelta(days=1)
        appt_id += 1
        appointments.append((appt_id, pid, isodt(vd, random.randint(9, 17), 0), "attended", "Dr Fang"))
        complaint = random.choice(THEMES["dengue_like"])
        note_id += 1
        case_notes.append((note_id, pid, iso(vd), complaint, THEME_NOTE["dengue_like"],
                           json.dumps(embed(complaint))))
        cond_id += 1
        conditions.append((cond_id, pid, "Dengue (suspected)", iso(vd)))
        inv_id += 1
        invoices.append((inv_id, pid, round(random.uniform(60, 140), 2), iso(vd), "y"))

# ----------------------------------------------------------------------------
# Write to SQLite
# ----------------------------------------------------------------------------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
con = sqlite3.connect(DB_PATH)
with open(SCHEMA_PATH, encoding="utf-8") as f:
    con.executescript(f.read())

con.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?)", patients)
con.executemany("INSERT INTO appointments VALUES (?,?,?,?,?)", appointments)
con.executemany("INSERT INTO case_notes VALUES (?,?,?,?,?,?)", case_notes)
con.executemany("INSERT INTO conditions VALUES (?,?,?,?)", conditions)
con.executemany("INSERT INTO prescriptions VALUES (?,?,?,?,?)", prescriptions)
con.executemany("INSERT INTO invoices VALUES (?,?,?,?,?)", invoices)
con.commit()

# ----------------------------------------------------------------------------
# Validate row counts (mirrors the course's validation step)
# ----------------------------------------------------------------------------
print("Klinik Dr Fang synthetic DB built ->", DB_PATH)
for t in ["patients", "appointments", "case_notes", "conditions", "prescriptions", "invoices"]:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:<14} {n:>5} rows")

recent = con.execute(
    "SELECT COUNT(*) FROM case_notes WHERE visit_date >= ?",
    [iso(TODAY - timedelta(days=14))]).fetchone()[0]
print(f"  (sanity) case_notes in last 14 days: {recent}")
con.close()
