"""
One-time data preparation:
1. Rename students in data.db using _student_names.txt (S001..S185 in numerical order).
2. Add the new tables we promised in the design (pairings, group_sessions, peer_mentor_links).
3. Seed a demo group session and a demo peer-mentor link for the on-stage story.

Idempotent: safe to run multiple times.
"""
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "data.db"
NAMES_FILE = HERE / "_student_names.txt"


def load_names() -> list[str]:
    names = []
    with NAMES_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^\d+\.\s*(.+)$", line)
            names.append(m.group(1).strip() if m else line)
    return names


def main():
    names = load_names()
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # 1) Rename students -----------------------------------------------------
    c.execute("SELECT student_id FROM students ORDER BY CAST(SUBSTR(student_id, 2) AS INTEGER)")
    sids = [r[0] for r in c.fetchall()]
    if len(sids) != len(names):
        raise SystemExit(f"Mismatch: {len(sids)} students vs {len(names)} names")
    for sid, new_name in zip(sids, names):
        c.execute("UPDATE students SET name=? WHERE student_id=?", (new_name, sid))

    # 2) Update tutor join dates to North Star's 2016 founding ---------------
    tutor_joins = {
        "T001": "2016-03-01", "T003": "2016-03-01",
        "T013": "2017-01-15", "T015": "2017-08-01", "T017": "2018-04-20",
        "T005": "2019-01-10", "T007": "2019-06-15",
        "T009": "2020-01-10", "T011": "2020-08-01",
        "T014": "2021-02-01", "T019": "2021-05-15", "T021": "2021-09-01",
        "T010": "2022-03-01", "T012": "2022-06-01",
        "T002": "2023-01-15", "T004": "2023-03-01", "T016": "2023-06-01", "T020": "2023-08-15",
        "T006": "2024-01-10", "T008": "2024-04-15",
        "T018": "2025-01-20", "T022": "2025-06-01",
    }
    for tid, jd in tutor_joins.items():
        c.execute("UPDATE tutors SET join_date=? WHERE tutor_id=?", (jd, tid))

    # 3) Add new tables (idempotent) ----------------------------------------
    c.executescript("""
    CREATE TABLE IF NOT EXISTS pairings (
        pairing_id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        tutor_id   TEXT NOT NULL,
        subject    TEXT NOT NULL,
        status     TEXT DEFAULT 'active',
        health     TEXT DEFAULT 'steady',
        started_on TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(tutor_id)   REFERENCES tutors(tutor_id)
    );

    CREATE TABLE IF NOT EXISTS group_sessions (
        session_id TEXT PRIMARY KEY,
        class_id TEXT NOT NULL,
        session_date TEXT NOT NULL,
        problem_description TEXT,
        group_rubric TEXT,
        teacher_summary TEXT,
        FOREIGN KEY(class_id) REFERENCES classes(class_id)
    );

    CREATE TABLE IF NOT EXISTS group_session_participants (
        session_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        observation_strength TEXT,
        observation_growth TEXT,
        PRIMARY KEY(session_id, student_id),
        FOREIGN KEY(session_id) REFERENCES group_sessions(session_id),
        FOREIGN KEY(student_id) REFERENCES students(student_id)
    );

    CREATE TABLE IF NOT EXISTS peer_mentor_links (
        link_id TEXT PRIMARY KEY,
        senior_tutor_id TEXT NOT NULL,
        junior_tutor_id TEXT NOT NULL,
        reason TEXT,
        suggestion TEXT,
        status TEXT DEFAULT 'suggested',
        FOREIGN KEY(senior_tutor_id) REFERENCES tutors(tutor_id),
        FOREIGN KEY(junior_tutor_id) REFERENCES tutors(tutor_id)
    );
    """)

    # 4) Seed a demo group session for the David Chen / P5 Science story ----
    c.execute("DELETE FROM group_sessions WHERE session_id='GS_DEMO_001'")
    c.execute("DELETE FROM group_session_participants WHERE session_id='GS_DEMO_001'")
    c.execute("""
        INSERT INTO group_sessions (session_id, class_id, session_date, problem_description,
                                    group_rubric, teacher_summary)
        VALUES ('GS_DEMO_001', 'C043', '2026-04-18',
                'How does the boiling point of water change at different altitudes?',
                'Working strongly together',
                'Strong group dynamic. Harith led with a clear hypothesis; Nur Imani and Chloe built on it with their own observations.')
    """)
    demo_participants = [
        ('S006', 'Led the group with a clear hypothesis on altitude', 'Practise pausing to let others add'),
        ('S007', 'Built on the hypothesis with kitchen-experiment observations', 'Speak up earlier in the discussion'),
        ('S016', 'Suggested testing with salt water as a variable', 'Bring written notes to support ideas'),
    ]
    for sid, strong, growth in demo_participants:
        c.execute("""INSERT INTO group_session_participants (session_id, student_id,
                     observation_strength, observation_growth)
                     VALUES (?, ?, ?, ?)""",
                  ('GS_DEMO_001', sid, strong, growth))

    # 5) Seed the David Chen → Teacher Ravi peer-mentor link ----------------
    c.execute("DELETE FROM peer_mentor_links WHERE link_id='PM_DEMO_001'")
    c.execute("""
        INSERT INTO peer_mentor_links (link_id, senior_tutor_id, junior_tutor_id, reason, suggestion, status)
        VALUES ('PM_DEMO_001', 'T021', 'T022',
                'Teacher Ravi is new — his P6 Science class has 2 children whose grades are slipping',
                'Share your step-by-step teaching approach with him over coffee this week',
                'suggested')
    """)

    # 6) Enrol Arun (S105) in Teacher David Chen's P4 Science class (C058) -
    # so the demo narrative is coherent: manager flags him, teacher sees him,
    # parent letter is about Science.
    c.execute("DELETE FROM enrolments WHERE enrolment_id='E_DEMO_S105_SCI'")
    c.execute("""
        INSERT INTO enrolments (enrolment_id, student_id, class_id, start_date, end_date, status)
        VALUES ('E_DEMO_S105_SCI', 'S105', 'C058', '2025-01-15', NULL, 'active')
    """)

    # 7) Enforce 10-child cap (the small-class quality promise) ------------
    # Bright Path's original seed put some classes over 10 active enrolments.
    # For each over-cap class, move the OLDEST excess enrolments to 'completed'
    # so only the 10 most recent stay active. Demo enrolments are protected.
    PROTECTED = ('E_DEMO_S105_SCI',)

    c.execute("""
        SELECT cl.class_id, cl.max_students,
               (SELECT COUNT(*) FROM enrolments e2
                WHERE e2.class_id = cl.class_id AND e2.status = 'active') AS n
        FROM classes cl
        WHERE n > cl.max_students
    """)
    over_cap = c.fetchall()

    completed_count = 0
    for class_id, max_s, n in over_cap:
        excess = n - max_s
        placeholders = ','.join('?' * len(PROTECTED))
        c.execute(f"""
            SELECT enrolment_id FROM enrolments
            WHERE class_id=? AND status='active'
              AND enrolment_id NOT IN ({placeholders})
            ORDER BY start_date ASC
            LIMIT ?
        """, (class_id, *PROTECTED, excess))
        to_complete = [r[0] for r in c.fetchall()]
        for eid in to_complete:
            c.execute("UPDATE enrolments SET status='completed', end_date='2024-12-31' WHERE enrolment_id=?", (eid,))
            completed_count += 1

    conn.commit()
    conn.close()

    print("Data prepared:")
    print(f"  - 185 students renamed (first: {names[0]}, last: {names[-1]})")
    print("  - 22 tutor join dates updated to North Star 2016 founding")
    print("  - pairings, group_sessions, group_session_participants, peer_mentor_links tables ensured")
    print("  - 1 demo group session seeded (GS_DEMO_001, Teacher David Chen P5 Science)")
    print("  - 1 demo peer-mentor link seeded (PM_DEMO_001, David Chen → Ravi)")
    print("  - Arun (S105) enrolled in C058 (Teacher David Chen P4 Science)")
    print(f"  - 10-child cap enforced: {completed_count} excess enrolments moved to 'completed'")


if __name__ == "__main__":
    main()
