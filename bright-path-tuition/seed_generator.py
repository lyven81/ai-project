"""
Bright Path Tuition Centre — Seed Data Generator
=================================================
Builds data.db directly with 7 tables populated with realistic demo data,
including 9 hard-coded "stories" so the demo is never empty.

Run once:  python seed_generator.py
Produces:  data.db (SQLite, ready for main.py)
"""

import sqlite3
import random
from datetime import date, timedelta
import os

random.seed(42)  # deterministic so the demo is reproducible

DB_FILE = "data.db"

# Delete existing db so we start clean
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# ---------------------------------------------------------------
# 1. Create all 7 tables
# ---------------------------------------------------------------
c.executescript("""
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    level TEXT,
    school_name TEXT,
    gender TEXT,
    join_date TEXT,
    status TEXT,
    p4_math_baseline REAL,
    p4_english_baseline REAL,
    p4_bm_baseline REAL,
    p4_mandarin_baseline REAL,
    p4_science_baseline REAL
);

CREATE TABLE tutors (
    tutor_id TEXT PRIMARY KEY,
    name TEXT,
    employment_type TEXT,
    band TEXT,
    subject TEXT,
    join_date TEXT
);

CREATE TABLE classes (
    class_id TEXT PRIMARY KEY,
    class_type TEXT,
    level TEXT,
    subject TEXT,
    tutor_id TEXT,
    day_of_week TEXT,
    start_time TEXT,
    max_students INTEGER,
    is_anchor_year INTEGER
);

CREATE TABLE enrolments (
    enrolment_id TEXT PRIMARY KEY,
    student_id TEXT,
    class_id TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT
);

CREATE TABLE attendance (
    attendance_id TEXT PRIMARY KEY,
    enrolment_id TEXT,
    class_date TEXT,
    status TEXT
);

CREATE TABLE assessments (
    assessment_id TEXT PRIMARY KEY,
    enrolment_id TEXT,
    assessment_date TEXT,
    assessment_type TEXT,
    subject TEXT,
    score REAL,
    max_score REAL,
    grade TEXT
);

CREATE TABLE development_notes (
    note_id TEXT PRIMARY KEY,
    student_id TEXT,
    tutor_id TEXT,
    note_date TEXT,
    dimension TEXT,
    observation TEXT
);
""")

# ---------------------------------------------------------------
# 2. Reference data
# ---------------------------------------------------------------
SUBJECTS = ["BM", "English", "Mandarin", "Math", "Science"]
MALAY_NAMES = ["Aisyah", "Ahmad", "Siti", "Hakim", "Nurul", "Imran", "Farah", "Zulkifli"]
CHINESE_NAMES = ["Wei Ming", "Li Ying", "Jun Hao", "Xin Yi", "Zi Han", "Mei Ling", "Kai Xuan", "Yi Ting"]
INDIAN_NAMES = ["Priya", "Arun", "Kavya", "Rajesh", "Deepa", "Vikram", "Lakshmi", "Dinesh"]
ALL_FIRST_NAMES = MALAY_NAMES + CHINESE_NAMES + INDIAN_NAMES
SCHOOLS = ["SK Damansara", "SJKC Puay Chai", "SK Taman Tun", "SJKT Vivekananda", "SK Bukit Damansara"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DIMENSIONS = ["academic_mastery", "critical_thinking", "participation", "discipline", "collaboration", "creativity"]


def grade_for(score):
    if score >= 85: return "A+"
    if score >= 75: return "A"
    if score >= 65: return "B"
    if score >= 55: return "C"
    if score >= 45: return "D"
    return "F"


def random_date(start, end):
    return (start + timedelta(days=random.randint(0, (end - start).days))).isoformat()


# ---------------------------------------------------------------
# 3. Create tutors (22 total)
# ---------------------------------------------------------------
# Named tutors so seeded stories can reference them
NAMED_TUTORS = {
    # Preschool (2)
    "T001": ("Teacher Aminah", "full-time", "preschool", None),
    "T002": ("Teacher Rachel", "part-time", "preschool", None),
    # P1-P3 band (10 — 2 per subject)
    "T003": ("Teacher Mei Lin", "full-time", "P1-P3", "Math"),
    "T004": ("Teacher David Tan", "part-time", "P1-P3", "Math"),
    "T005": ("Teacher Sarah Wong", "full-time", "P1-P3", "English"),
    "T006": ("Teacher James Lim", "part-time", "P1-P3", "English"),
    "T007": ("Teacher Noraini", "full-time", "P1-P3", "BM"),
    "T008": ("Teacher Hafiz", "part-time", "P1-P3", "BM"),
    "T009": ("Teacher Li Hua", "full-time", "P1-P3", "Mandarin"),
    "T010": ("Teacher Chong Wei", "part-time", "P1-P3", "Mandarin"),
    "T011": ("Teacher Priya", "full-time", "P1-P3", "Science"),
    "T012": ("Teacher Kumar", "part-time", "P1-P3", "Science"),
    # P4-P6 band (10)
    "T013": ("Teacher Daniel", "full-time", "P4-P6", "Math"),     # strong tutor
    "T014": ("Teacher Alicia", "full-time", "P4-P6", "Math"),
    "T015": ("Teacher Jessica", "full-time", "P4-P6", "English"),  # strong tutor
    "T016": ("Teacher Zara", "part-time", "P4-P6", "English"),     # weak tutor (seeded story)
    "T017": ("Teacher Siti Aminah", "full-time", "P4-P6", "BM"),
    "T018": ("Teacher Rahim", "part-time", "P4-P6", "BM"),
    "T019": ("Teacher Chen Wei", "full-time", "P4-P6", "Mandarin"),
    "T020": ("Teacher Wong Mei", "part-time", "P4-P6", "Mandarin"),
    "T021": ("Teacher David Chen", "full-time", "P4-P6", "Science"),  # strong — used in P5 fix story
    "T022": ("Teacher Ravi", "part-time", "P4-P6", "Science"),
}

for tid, (name, emp, band, subj) in NAMED_TUTORS.items():
    c.execute(
        "INSERT INTO tutors VALUES (?, ?, ?, ?, ?, ?)",
        (tid, name, emp, band, subj, "2022-01-15"),
    )

# ---------------------------------------------------------------
# 4. Create classes (63 total)
# ---------------------------------------------------------------
# Preschool: 3 classes, shared between 2 preschool tutors
classes_data = [
    ("C001", "level-specific", "Preschool", None, "T001", "Mon", "09:00", 10, 0),
    ("C002", "level-specific", "Preschool", None, "T001", "Wed", "09:00", 10, 0),
    ("C003", "level-specific", "Preschool", None, "T002", "Sat", "10:00", 10, 0),
]

# P1-P3 band: each of 10 tutors runs 3 classes (one per level)
p1p3_tutors = [(tid, NAMED_TUTORS[tid][3]) for tid in NAMED_TUTORS if NAMED_TUTORS[tid][2] == "P1-P3"]
cid = 4
for tid, subj in p1p3_tutors:
    for level in ["P1", "P2", "P3"]:
        day = random.choice(DAYS)
        tm = random.choice(["16:00", "17:00", "18:00"])
        classes_data.append((f"C{cid:03d}", "subject-specific", level, subj, tid, day, tm, 10, 0))
        cid += 1

# P4-P6 band: each of 10 tutors runs 3 classes (P4 has is_anchor_year=1)
p4p6_tutors = [(tid, NAMED_TUTORS[tid][3]) for tid in NAMED_TUTORS if NAMED_TUTORS[tid][2] == "P4-P6"]
for tid, subj in p4p6_tutors:
    for level in ["P4", "P5", "P6"]:
        day = random.choice(DAYS)
        tm = random.choice(["17:00", "18:00", "19:00"])
        anchor = 1 if level == "P4" else 0
        classes_data.append((f"C{cid:03d}", "subject-specific", level, subj, tid, day, tm, 10, anchor))
        cid += 1

c.executemany("INSERT INTO classes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", classes_data)
print(f"Created {len(classes_data)} classes")


# ---------------------------------------------------------------
# 5. Create students (P4-weighted, ~188 unique)
# ---------------------------------------------------------------
# Distribution matches policy pivot: P4 is anchor year (largest), P5/P6 are prep years
level_counts = {
    "Preschool": 18,
    "P1": 18,
    "P2": 20,
    "P3": 22,
    "P4": 45,  # 25% — MOE anchor
    "P5": 34,  # 18%
    "P6": 28,  # 15% (no UPSR drive)
}
age_by_level = {"Preschool": 5, "P1": 7, "P2": 8, "P3": 9, "P4": 10, "P5": 11, "P6": 12}

students_data = []
sid_counter = 1

# Seeded story children (hardcoded first so they stay pinned)
STORY_CHILDREN = {
    # P4 mastery gap story — 5 children flagged in Year 4 anchor report
    "S001": ("Ahmad Farid",        10, "P4", "SK Damansara",      "Male"),
    "S002": ("Nurul Aina",         10, "P4", "SJKC Puay Chai",    "Female"),
    "S003": ("Wei Ming Tan",       10, "P4", "SK Taman Tun",      "Male"),
    "S004": ("Priya Kumar",        10, "P4", "SJKT Vivekananda",  "Female"),
    "S005": ("Hakim Azlan",        10, "P4", "SK Bukit Damansara","Male"),
    # P5 CRITICAL escalation story — 2 children entered P5 with unresolved P4 gaps
    "S006": ("Rahim bin Zainal",   11, "P5", "SK Damansara",      "Male"),
    "S007": ("Li Ying Chen",       11, "P5", "SJKC Puay Chai",    "Female"),
    # P6 URGENT secondary-readiness story — 1 child with P4 Science gap, 5 months to Form 1
    "S008": ("Aisyah binti Rosli", 12, "P6", "SK Damansara",      "Female"),
    # P6 secondary-ready celebration — 4 children ready across all subjects
    "S009": ("Jun Hao Lim",        12, "P6", "SJKC Puay Chai",    "Male"),
    "S010": ("Farah Zahra",        12, "P6", "SK Taman Tun",      "Female"),
    "S011": ("Xin Yi Wong",        12, "P6", "SJKC Puay Chai",    "Female"),
    "S012": ("Deepa Ravi",         12, "P6", "SJKT Vivekananda",  "Female"),
    # Top improver children — 5 rising stars
    "S013": ("Siti Humaira",       11, "P5", "SK Damansara",      "Female"),
    "S014": ("Kai Xuan Tan",       10, "P4", "SJKC Puay Chai",    "Male"),
    "S015": ("Vikram Raj",         10, "P4", "SJKT Vivekananda",  "Male"),
    "S016": ("Mei Ling Ng",        11, "P5", "SJKC Puay Chai",    "Female"),
    "S017": ("Imran Hakim",         9, "P3", "SK Bukit Damansara","Male"),
}

for sid, (name, age, level, school, gender) in STORY_CHILDREN.items():
    students_data.append((sid, name, age, level, school, gender, "2025-01-15", "active",
                          None, None, None, None, None))  # baselines filled later
    sid_counter += 1

# Generate remaining children to hit level_counts targets
for level, target_count in level_counts.items():
    existing = sum(1 for s in students_data if s[3] == level)
    to_create = target_count - existing
    for _ in range(to_create):
        sid = f"S{sid_counter:03d}"
        sid_counter += 1
        name = f"{random.choice(ALL_FIRST_NAMES)} {random.choice(['Lee','Tan','Lim','Abdullah','Raj','Wong','Ismail'])}"
        students_data.append((sid, name, age_by_level[level], level, random.choice(SCHOOLS),
                              random.choice(["Male", "Female"]),
                              random_date(date(2024, 6, 1), date(2025, 10, 1)),
                              "active", None, None, None, None, None))

# Fill P4 baselines for P5 and P6 children (these are their Year 4 mastery snapshots)
def make_baseline(is_story_gap):
    """Generate a P4 baseline score. If this child has a seeded gap, make the baseline strong
    (so the CURRENT score below shows as a drop); otherwise strong across the board."""
    if is_story_gap:
        return round(random.uniform(72, 85), 1)  # solid P4 — they mastered it
    return round(random.uniform(65, 90), 1)

for i, row in enumerate(students_data):
    sid, name, age, level, school, gender, jd, status, *_ = row
    if level in ("P5", "P6"):
        math_b = make_baseline(sid in ("S006", "S007"))           # gap story
        eng_b = make_baseline(True)
        bm_b = make_baseline(True)
        mand_b = make_baseline(True)
        sci_b = make_baseline(sid == "S008")                       # P6 Science gap story
        students_data[i] = (sid, name, age, level, school, gender, jd, status,
                            math_b, eng_b, bm_b, mand_b, sci_b)

c.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students_data)
print(f"Created {len(students_data)} children")


# ---------------------------------------------------------------
# 6. Create enrolments (children enrol in subjects at their level)
# ---------------------------------------------------------------
# Fetch classes grouped by level for quick lookup
c.execute("SELECT class_id, level, subject FROM classes")
classes_by_level = {}
for class_id, level, subject in c.fetchall():
    classes_by_level.setdefault(level, []).append((class_id, subject))

enrolments_data = []
eid_counter = 1

for sid, name, age, level, *_ in students_data:
    if level == "Preschool":
        # Preschool children enrol in 1 preschool class only
        class_id = random.choice([cl[0] for cl in classes_by_level["Preschool"]])
        enrolments_data.append((f"E{eid_counter:04d}", sid, class_id, "2025-01-15", None, "active"))
        eid_counter += 1
    else:
        # Primary children enrol in 2-4 subjects
        level_classes = classes_by_level[level]
        n_subjects = random.randint(2, 4)
        # Group classes by subject then pick one random class per subject chosen
        by_subject = {}
        for cl_id, subj in level_classes:
            by_subject.setdefault(subj, []).append(cl_id)
        chosen_subjects = random.sample(list(by_subject.keys()), min(n_subjects, len(by_subject)))
        for subj in chosen_subjects:
            class_id = random.choice(by_subject[subj])
            enrolments_data.append((f"E{eid_counter:04d}", sid, class_id, "2025-01-15", None, "active"))
            eid_counter += 1

# Ensure all seeded-story children are enrolled in the subjects their stories require
# P4 gap stories (S001-S005) — all need Math + English + Science at P4
# P5 critical (S006, S007) — need P5 Math (S006) and P5 English (S007)
# P6 urgent (S008) — needs P6 Science
# P6 ready (S009-S012) — need all 5 subjects
# Top improvers — need the subjects they're improving in

# Helper: get class_id for (level, subject, preferred_tutor)
def find_class(level, subject, preferred_tutor=None):
    c.execute(
        "SELECT class_id FROM classes WHERE level=? AND subject=?" +
        (" AND tutor_id=?" if preferred_tutor else ""),
        ((level, subject, preferred_tutor) if preferred_tutor else (level, subject)),
    )
    rows = c.fetchall()
    return rows[0][0] if rows else None

# Helper: check if student already enrolled in (level, subject)
def is_enrolled(student_id, class_id):
    return any(e[1] == student_id and e[2] == class_id for e in enrolments_data)

def ensure_enrol(student_id, level, subject, tutor=None):
    global eid_counter
    class_id = find_class(level, subject, tutor)
    if not class_id:
        return
    if is_enrolled(student_id, class_id):
        return
    enrolments_data.append((f"E{eid_counter:04d}", student_id, class_id, "2025-01-15", None, "active"))
    eid_counter += 1

# Pin P4 gap story children to specific tutors so the "compare specialists" query has something to compare
# S001,S002 -> Teacher Daniel (T013) Math  |  S003,S004,S005 -> Teacher Alicia (T014) Math
for sid in ["S001", "S002", "S003", "S004", "S005"]:
    ensure_enrol(sid, "P4", "Math", "T013" if sid in ("S001", "S002") else "T014")
    ensure_enrol(sid, "P4", "English")
    ensure_enrol(sid, "P4", "Science")

# P5 critical stories
ensure_enrol("S006", "P5", "Math", "T014")   # Rahim in Teacher Alicia's P5 Math
ensure_enrol("S007", "P5", "English", "T016") # Li Ying in Teacher Zara's P5 English (weak tutor)

# P6 urgent story — Aisyah in Science
ensure_enrol("S008", "P6", "Science", "T022")  # currently with Teacher Ravi

# P6 secondary-ready — all 5 subjects
for sid in ["S009", "S010", "S011", "S012"]:
    for subj in SUBJECTS:
        ensure_enrol(sid, "P6", subj)

c.executemany("INSERT INTO enrolments VALUES (?, ?, ?, ?, ?, ?)", enrolments_data)
print(f"Created {len(enrolments_data)} enrolments")


# ---------------------------------------------------------------
# 7. Create attendance (6 weeks of weekly class sessions)
# ---------------------------------------------------------------
attendance_data = []
att_counter = 1
start_week = date(2026, 2, 23)  # Mon of week 1
for e in enrolments_data:
    eid = e[0]
    for week in range(6):
        class_date = start_week + timedelta(days=week * 7)
        # 90% present, 8% absent, 2% replacement
        r = random.random()
        if r < 0.90:
            status = "present"
        elif r < 0.98:
            status = "absent"
        else:
            status = "replacement"
        attendance_data.append((f"A{att_counter:05d}", eid, class_date.isoformat(), status))
        att_counter += 1

c.executemany("INSERT INTO attendance VALUES (?, ?, ?, ?)", attendance_data)
print(f"Created {len(attendance_data)} attendance records")


# ---------------------------------------------------------------
# 8. Create assessments (2 monthly test cycles: March and April 2026)
# ---------------------------------------------------------------
assessments_data = []
asmt_counter = 1

# Build lookup from enrolment_id -> (student_id, level, subject, tutor_id)
c.execute("""
    SELECT e.enrolment_id, e.student_id, cl.level, cl.subject, cl.tutor_id
    FROM enrolments e
    JOIN classes cl ON e.class_id = cl.class_id
""")
enrolment_details = {row[0]: row[1:] for row in c.fetchall()}

# Strong tutors (whose children improve more) — used to give seeded tutor quality story
STRONG_TUTORS = {"T013", "T015", "T021"}
WEAK_TUTORS = {"T016"}  # Teacher Zara, P4-P6 English

def base_score(level):
    """Baseline score range by level — younger kids score higher on their simpler material."""
    return {"Preschool": 82, "P1": 80, "P2": 78, "P3": 76, "P4": 72, "P5": 70, "P6": 68}.get(level, 70)

for eid, (sid, level, subject, tid) in enrolment_details.items():
    if level == "Preschool":
        continue  # preschool children don't sit monthly tests

    base = base_score(level)

    # March score
    march = base + random.uniform(-10, 10)
    # April score — normally slight improvement
    delta = random.uniform(0, 3)
    if tid in STRONG_TUTORS:
        delta += random.uniform(4, 8)      # strong tutors = bigger improvement
    elif tid in WEAK_TUTORS:
        delta -= random.uniform(3, 7)       # weak tutor = flat or regress

    # Seeded story overrides
    if sid in ("S001", "S002", "S003", "S004", "S005") and subject in ("Math", "English", "Science"):
        # P4 mastery gap — low current scores
        march = random.uniform(40, 52)
        delta = random.uniform(-2, 4)
    elif sid == "S006" and subject == "Math":
        # P5 Rahim — current BELOW his p4_math_baseline (CRITICAL)
        march = random.uniform(48, 58)
        delta = random.uniform(-3, 2)
    elif sid == "S007" and subject == "English":
        # P5 Li Ying — current BELOW her p4_english_baseline (CRITICAL)
        march = random.uniform(50, 60)
        delta = random.uniform(-4, 1)
    elif sid == "S008" and subject == "Science":
        # P6 Aisyah — URGENT secondary-readiness risk
        march = random.uniform(42, 52)
        delta = random.uniform(-2, 3)
    elif sid in ("S009", "S010", "S011", "S012"):
        # P6 secondary-ready — consistently strong across all subjects
        march = random.uniform(80, 92)
        delta = random.uniform(1, 5)
    elif sid in ("S013", "S014", "S015", "S016", "S017"):
        # Top improvers — big jump
        march = random.uniform(55, 65)
        delta = random.uniform(14, 22)

    april = march + delta
    march = max(0, min(100, round(march, 1)))
    april = max(0, min(100, round(april, 1)))

    assessments_data.append((f"AS{asmt_counter:05d}", eid, "2026-03-15", "monthly_test",
                             subject, march, 100.0, grade_for(march)))
    asmt_counter += 1
    assessments_data.append((f"AS{asmt_counter:05d}", eid, "2026-04-15", "monthly_test",
                             subject, april, 100.0, grade_for(april)))
    asmt_counter += 1

# Add school PBD snapshots for P4-P6 children (captured from school reports)
for eid, (sid, level, subject, tid) in enrolment_details.items():
    if level not in ("P4", "P5", "P6"):
        continue
    # PBD is one of: TP1, TP2, TP3, TP4, TP5, TP6 — we map to score
    # Normally track the monthly_test score but with some divergence
    centre_avg = 70 + random.uniform(-5, 5)
    school_pbd = centre_avg + random.uniform(-8, 5)

    # PBD divergence story — 3 children whose centre score is strong but school PBD is weak
    if sid in ("S013", "S014", "S015") and subject == "Math":
        school_pbd = random.uniform(45, 55)  # school says weak even though centre says improving

    school_pbd = max(0, min(100, round(school_pbd, 1)))
    assessments_data.append((f"AS{asmt_counter:05d}", eid, "2026-04-05", "school_pbd",
                             subject, school_pbd, 100.0, grade_for(school_pbd)))
    asmt_counter += 1

c.executemany("INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?, ?)", assessments_data)
print(f"Created {len(assessments_data)} assessments")


# ---------------------------------------------------------------
# 9. Create development notes (holistic PBD dimensions)
# ---------------------------------------------------------------
notes_data = []
nid_counter = 1

POSITIVE_OBS = {
    "academic_mastery": "Grasps new concepts quickly and applies them independently.",
    "critical_thinking": "Asks thoughtful questions and proposes alternative approaches.",
    "participation": "Actively joins discussions and volunteers to answer.",
    "discipline": "Consistently completes homework on time with care.",
    "collaboration": "Works well with classmates and helps others when stuck.",
    "creativity": "Comes up with original solutions the class hasn't seen.",
}
CONCERN_OBS = {
    "academic_mastery": "Struggling to retain concepts from previous weeks — needs reinforcement.",
    "critical_thinking": "Tends to memorise rather than reason through problems.",
    "participation": "Quiet in class, rarely volunteers to answer.",
    "discipline": "Homework often incomplete or rushed.",
    "collaboration": "Prefers to work alone, avoids group activities.",
    "creativity": "Gives textbook answers, hesitant to try new approaches.",
}

# For each active enrolment, create 1 note per month across 2 months (March, April)
# Pick a random dimension; concern notes seeded for specific story children
CONCERN_CHILDREN = {"S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008"}
WEAK_TUTOR_CHILDREN = set()  # children under Teacher Zara should show weak critical_thinking
for e in enrolments_data:
    eid, sid, cid, *_ = e
    c.execute("SELECT tutor_id, subject FROM classes WHERE class_id=?", (cid,))
    row = c.fetchone()
    if row and row[0] == "T016":
        WEAK_TUTOR_CHILDREN.add(sid)

# One note per child per month (not per enrolment — to avoid over-counting)
children_by_sid = {s[0]: s for s in students_data}
for sid, student_row in children_by_sid.items():
    # Find this child's main tutor (first active enrolment)
    child_enrols = [e for e in enrolments_data if e[1] == sid]
    if not child_enrols:
        continue
    first_cid = child_enrols[0][2]
    c.execute("SELECT tutor_id FROM classes WHERE class_id=?", (first_cid,))
    tid_row = c.fetchone()
    if not tid_row:
        continue
    tid = tid_row[0]

    for note_date in ("2026-03-20", "2026-04-20"):
        if sid in CONCERN_CHILDREN:
            dim = random.choice(["academic_mastery", "critical_thinking"])
            obs = CONCERN_OBS[dim]
        elif sid in WEAK_TUTOR_CHILDREN:
            dim = "critical_thinking"
            obs = CONCERN_OBS[dim]
        else:
            dim = random.choice(DIMENSIONS)
            obs = POSITIVE_OBS[dim]
        notes_data.append((f"N{nid_counter:04d}", sid, tid, note_date, dim, obs))
        nid_counter += 1

c.executemany("INSERT INTO development_notes VALUES (?, ?, ?, ?, ?, ?)", notes_data)
print(f"Created {len(notes_data)} development notes")

conn.commit()
conn.close()

# ---------------------------------------------------------------
# 10. Summary
# ---------------------------------------------------------------
print("\n" + "=" * 55)
print("Bright Path Tuition Centre — data.db built successfully")
print("=" * 55)
print(f"  Classes:            {len(classes_data)}")
print(f"  Tutors:             {len(NAMED_TUTORS)}")
print(f"  Children:           {len(students_data)}")
print(f"  Enrolments:         {len(enrolments_data)}")
print(f"  Attendance records: {len(attendance_data)}")
print(f"  Assessments:        {len(assessments_data)}")
print(f"  Development notes:  {len(notes_data)}")
print("\nSeeded demo stories ready:")
print("  1. Year 4 anchor gaps        (S001-S005, Teacher Daniel vs Alicia)")
print("  2. P5 CRITICAL escalation    (S006 Math, S007 English)")
print("  3. P6 URGENT secondary risk  (S008 Science)")
print("  4. P6 secondary-ready        (S009-S012, all 5 subjects)")
print("  5. Top improvers             (S013-S017)")
print("  6. Underperforming specialist (Teacher Zara T016)")
print("  7. PBD divergence            (strong centre, weak school PBD)")
print("  8. Holistic development      (concern dimensions per child)")
print("  9. Class fill-rate variance  (natural from enrolment spread)")
print("\nNext: set GOOGLE_API_KEY in .env and run:  python main.py")
