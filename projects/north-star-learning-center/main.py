"""
North Star Learning Center — AI Ecosystem for Personalized Small-Class Education

FastAPI backend serving:
  - 4 role views: Manager / Teacher / Parent / Centre Directory
  - 6 MCP-style tools the AI dispatches
  - 1 live Gemini call (parent monthly story)

Built for the MyHack 2026 hackathon. Reskins to other small-class learning verticals
via the VERTICAL_CONFIG dict (piano academy demo included).
"""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

# Gemini SDK (optional — app falls back to canned text if no key)
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()
GEMINI_AVAILABLE = False
gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        GEMINI_AVAILABLE = True
    except Exception as e:
        print(f"[warn] Gemini init failed: {e}. Falling back to canned text.")

HERE = Path(__file__).parent
DB_PATH = HERE / "data.db"
HTML_PATH = HERE / "demo.html"

app = FastAPI(title="North Star Learning Center")


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Vertical config — swap to reskin the same engine to piano academy etc.
# ---------------------------------------------------------------------------
VERTICAL_CONFIG = {
    "tuition": {
        "centre_name": "North Star Learning Center",
        "location": "Subang",
        "actor_child": "children",
        "actor_specialist": "specialists",
        "actor_class": "classes",
        "primary_subjects": "BM, English, Math, Mandarin, Science",
        "anchor_year": "Year 4 (P4)",
        "lab_label": "Science lab",
    },
    "piano": {
        "centre_name": "Crescendo Music Academy",
        "location": "Subang",
        "actor_child": "students",
        "actor_specialist": "piano instructors",
        "actor_class": "practice sessions",
        "primary_subjects": "Classical, Pop, Jazz, Theory",
        "anchor_year": "Grade 5 (ABRSM)",
        "lab_label": "ensemble practice",
    },
}


# ===========================================================================
# MCP-style tools — deterministic computations the AI dispatches.
# Each returns plain JSON-ready dicts.
# ===========================================================================
def tool_centre_snapshot() -> dict:
    """Return the centre's at-a-glance numbers for the Manager Home."""
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM students")
        students_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tutors")
        tutors_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM classes")
        classes_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*), MAX(max_students) FROM classes")
        classes_count, cap = c.fetchone()

        # Enrolled per class
        c.execute("""
            SELECT cl.class_id, cl.subject, cl.level, COUNT(e.enrolment_id) AS enrolled, cl.max_students
            FROM classes cl
            LEFT JOIN enrolments e ON cl.class_id = e.class_id AND e.status = 'active'
            GROUP BY cl.class_id
        """)
        rows = c.fetchall()
        open_by_band = {"Preschool": 0, "P1-P3 BM": 0, "P1-P3 English": 0, "P1-P3 Math": 0,
                        "P1-P3 Mandarin": 0, "P1-P3 Science": 0, "P4-P6 BM": 0,
                        "P4-P6 English": 0, "P4-P6 Math": 0, "P4-P6 Mandarin": 0, "P4-P6 Science": 0}
        total_open = 0
        for r in rows:
            open_slots = (r["max_students"] or 10) - (r["enrolled"] or 0)
            total_open += max(open_slots, 0)
            if r["level"] == "Preschool":
                key = "Preschool"
            elif r["level"] in ("P1", "P2", "P3"):
                key = f"P1-P3 {r['subject']}"
            else:
                key = f"P4-P6 {r['subject']}"
            if key in open_by_band:
                open_by_band[key] += max(open_slots, 0)

        # Pick the top 4 with open slots
        top4 = sorted(open_by_band.items(), key=lambda x: -x[1])[:4]
        top4 = [{"category": k, "open": v} for k, v in top4 if v > 0]

    return {
        "students_count": students_count,
        "tutors_count": tutors_count,
        "classes_count": classes_count,
        "total_open_slots": total_open,
        "open_by_band": top4,
    }


def tool_at_risk_children() -> list[dict]:
    """Find children with a critical or urgent gap based on assessment data."""
    out = []
    with db() as conn:
        c = conn.cursor()
        # Critical: P5/P6 child whose latest monthly_test in a subject is below their P4 baseline
        c.execute("""
            SELECT s.student_id, s.name, s.level,
                   a.subject, a.score AS current_score,
                   CASE a.subject
                     WHEN 'Math'     THEN s.p4_math_baseline
                     WHEN 'English'  THEN s.p4_english_baseline
                     WHEN 'BM'       THEN s.p4_bm_baseline
                     WHEN 'Mandarin' THEN s.p4_mandarin_baseline
                     WHEN 'Science'  THEN s.p4_science_baseline
                   END AS baseline,
                   t.name AS tutor_name
            FROM assessments a
            JOIN enrolments e ON a.enrolment_id = e.enrolment_id
            JOIN students s   ON e.student_id = s.student_id
            JOIN classes cl   ON e.class_id = cl.class_id
            JOIN tutors t     ON cl.tutor_id = t.tutor_id
            WHERE a.assessment_type = 'monthly_test'
              AND s.level IN ('P5', 'P6')
              AND a.assessment_date = (
                  SELECT MAX(a2.assessment_date)
                  FROM assessments a2 JOIN enrolments e2 ON a2.enrolment_id = e2.enrolment_id
                  WHERE e2.student_id = s.student_id AND a2.subject = a.subject
              )
        """)
        for r in c.fetchall():
            if r["baseline"] is None or r["current_score"] is None:
                continue
            gap = r["current_score"] - r["baseline"]
            if gap < -5:  # significant gap
                out.append({
                    "student_id": r["student_id"],
                    "name": r["name"],
                    "level": r["level"],
                    "subject": r["subject"],
                    "current_score": round(r["current_score"], 1),
                    "baseline": round(r["baseline"], 1),
                    "gap": round(gap, 1),
                    "tutor_name": r["tutor_name"],
                    "risk": "urgent" if r["level"] == "P6" else "critical",
                })

        # Featured demo case: Arun Prakash (S105, P4) with anchor concern, even if not naturally in query above
        c.execute("SELECT name, level FROM students WHERE student_id='S105'")
        row = c.fetchone()
        if row:
            out.insert(0, {
                "student_id": "S105",
                "name": row["name"],
                "level": row["level"],
                "subject": "Science",
                "current_score": 52.0,
                "baseline": None,
                "gap": None,
                "tutor_name": "Teacher David Chen",
                "risk": "anchor",
                "note": "Year 4 anchor concern — concept understanding plateauing"
            })

    # De-duplicate and cap at 3 for the home view
    seen = set()
    deduped = []
    for item in out:
        key = (item["student_id"], item["subject"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:3]


def tool_teacher_wellbeing() -> list[dict]:
    """Identify teachers who may be stretched (lightweight signal from dev notes)."""
    with db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT t.tutor_id, t.name, t.band, t.subject, t.join_date,
                   COUNT(dn.note_id) AS note_count
            FROM tutors t LEFT JOIN development_notes dn ON t.tutor_id = dn.tutor_id
            GROUP BY t.tutor_id
        """)
        rows = c.fetchall()
        flagged = []
        for r in rows:
            # Demo signal: low dev-note frequency for a non-preschool teacher
            if r["band"] != "preschool" and r["note_count"] < 5:
                flagged.append({
                    "tutor_id": r["tutor_id"],
                    "name": r["name"],
                    "subject": f"{r['band']} {r['subject'] or ''}".strip(),
                    "issue": f"Dev notes activity is below typical level ({r['note_count']} this period)",
                })
        # Always feature Teacher Zara if present (matches the brief story)
        c.execute("SELECT tutor_id, name, band, subject FROM tutors WHERE tutor_id='T016'")
        zara = c.fetchone()
        if zara:
            featured = {
                "tutor_id": "T016",
                "name": zara["name"],
                "subject": f"{zara['band']} {zara['subject'] or ''}".strip(),
                "issue": "Her teacher notes dropped 40% this month. She may be stretched too thin.",
            }
            flagged = [featured] + [f for f in flagged if f["tutor_id"] != "T016"]
        return flagged[:2]


def tool_teacher_home(tutor_id: str) -> dict:
    """Build the Teacher Home view for one specialist."""
    with db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT t.tutor_id, t.name, t.band, t.subject, t.join_date, t.employment_type
            FROM tutors t WHERE t.tutor_id=?
        """, (tutor_id,))
        t = c.fetchone()
        if not t:
            raise HTTPException(404, "Teacher not found")

        c.execute("""
            SELECT cl.class_id, cl.level, cl.subject, cl.day_of_week, cl.start_time, cl.max_students,
                   COUNT(e.enrolment_id) AS enrolled
            FROM classes cl
            LEFT JOIN enrolments e ON cl.class_id = e.class_id AND e.status='active'
            WHERE cl.tutor_id=? GROUP BY cl.class_id
        """, (tutor_id,))
        classes = [dict(r) for r in c.fetchall()]

        # Peer mentor link (David Chen featured)
        c.execute("""
            SELECT pml.*, jt.name AS junior_name, jt.band AS junior_band,
                   jt.subject AS junior_subject, jt.join_date AS junior_join
            FROM peer_mentor_links pml
            JOIN tutors jt ON pml.junior_tutor_id = jt.tutor_id
            WHERE pml.senior_tutor_id=? AND pml.status='suggested'
        """, (tutor_id,))
        pml = c.fetchone()
        peer = dict(pml) if pml else None

    # Demo-canned children-needs-help + celebrate (curated for stage clarity)
    needs_help = [
        {"name": "Arun Prakash", "level": "P4", "issue": "Year 4 Science anchor — concept understanding plateauing",
         "suggestion": "Scaffold multi-step reasoning with a hands-on activity."},
        {"name": "Tan Wei Jie", "level": "P4", "issue": "Quiet in last 2 group sessions",
         "suggestion": "Pair him with Suresh Kumar — they have a strong working history."},
        {"name": "Muhammad Hilmi", "level": "P5", "issue": "Multi-step word problems",
         "suggestion": "Smaller sub-questions; revisit unit basics."},
    ]
    celebrate = [
        "Priya Nair asked her first clarifying question.",
        "Chloe Tan jumped 14 pts in Science this cycle.",
        "The Monday P5 group worked strongly together.",
    ]

    # Lab grouping for C043 (David Chen's P5 Science class)
    lab_grouping = None
    if tutor_id == "T021":
        with db() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT s.student_id, s.name FROM enrolments e
                JOIN students s ON e.student_id = s.student_id
                WHERE e.class_id='C059' AND e.status='active' LIMIT 10
            """)
            roster = [r["name"] for r in c.fetchall()]
        # Smart grouping — minimum group size 2, never leave a child alone
        # 10 → 3-3-4 · 9 → 3-3-3 · 8 → 3-3-2 · 7 → 3-2-2 · 6 → 3-3 · 5 → 3-2
        def make_groups(names):
            n = len(names)
            if n < 2:
                return [names]
            if n <= 4:
                return [names]
            out, i = [], 0
            while i < n:
                if n - i == 4:           # take 4 to avoid leaving 1 behind
                    out.append(names[i:i+4]); i += 4
                else:
                    out.append(names[i:i+3]); i += 3
            # If the last group still ended up with 1, merge it into the previous
            if len(out) > 1 and len(out[-1]) < 2:
                out[-2].extend(out[-1]); out.pop()
            return out

        raw_groups = make_groups(roster)
        # Curated AI reasoning per group (rotated by position)
        notes = [
            "Strong working history from last term — see GS_DEMO_001.",
            "Balanced mix of leaders and listeners — voices stay even.",
            "Fresh combination to broaden their working network.",
            "Quieter children get more space to think aloud together.",
        ]
        groups_with_notes = [
            {"members": g, "note": notes[i % len(notes)]}
            for i, g in enumerate(raw_groups)
        ]
        lab_grouping = {
            "class_id": "C059",
            "class_name": "P5 Science",
            "date": "Thursday",
            "groups": groups_with_notes,
        }

    return {
        "tutor": dict(t),
        "classes": classes,
        "needs_help": needs_help,
        "celebrate": celebrate,
        "lab_grouping": lab_grouping,
        "peer_mentor": peer,
    }


def tool_centre_directory() -> dict:
    """Static org-chart view."""
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT band, subject, COUNT(*) AS cnt FROM tutors GROUP BY band, subject")
        rows = [dict(r) for r in c.fetchall()]
        # Seniority breakdown — compute from join_date
        c.execute("SELECT name, join_date FROM tutors")
        seniors = experienced = mid = junior = 0
        for r in c.fetchall():
            yrs = 2026 - int((r["join_date"] or "2025-01-01")[:4])
            if yrs >= 8: seniors += 1
            elif yrs >= 5: experienced += 1
            elif yrs >= 3: mid += 1
            else: junior += 1
    return {
        "classes_by_band": {
            "Preschool": 4, "P1-P3": 20, "P4-P6": 20, "Total": 44,
        },
        "teachers_by_subject_band": rows,
        "seniority": {
            "Senior (8-10 yrs)": seniors,
            "Experienced (5-7 yrs)": experienced,
            "Mid-career (3-4 yrs)": mid,
            "Junior (1-2 yrs)": junior,
        },
    }


def tool_student_profile(student_id: str) -> dict:
    """Compute a child's mastery profile + recent dev notes."""
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        s = c.fetchone()
        if not s:
            raise HTTPException(404, "Student not found")
        # Recent assessments
        c.execute("""
            SELECT a.subject, a.score, a.assessment_date
            FROM assessments a JOIN enrolments e ON a.enrolment_id = e.enrolment_id
            WHERE e.student_id=? ORDER BY a.assessment_date DESC LIMIT 12
        """, (student_id,))
        recent = [dict(r) for r in c.fetchall()]
        # Recent dev notes
        c.execute("""
            SELECT dimension, observation FROM development_notes
            WHERE student_id=? ORDER BY note_date DESC LIMIT 6
        """, (student_id,))
        notes = [dict(r) for r in c.fetchall()]
        # Current classes / specialists
        c.execute("""
            SELECT cl.subject, cl.class_id, t.name AS tutor_name, t.tutor_id
            FROM enrolments e JOIN classes cl ON e.class_id = cl.class_id
            JOIN tutors t ON cl.tutor_id = t.tutor_id
            WHERE e.student_id=? AND e.status='active'
        """, (student_id,))
        pairings = [dict(r) for r in c.fetchall()]

    return {
        "student": dict(s),
        "recent_assessments": recent,
        "dev_notes": notes,
        "pairings": pairings,
    }


# ===========================================================================
# AI tool — Gemini generates the warm parent monthly story
# ===========================================================================
def tool_parent_story(student_id: str, subject_filter: Optional[str] = None) -> dict:
    """Generate a warm monthly story for the parent of `student_id`.

    `subject_filter` lets the caller anchor the letter on a specific subject
    (e.g. Science for the demo case S105, to align with the featured teacher).
    Falls back to the child's first pairing if not specified.
    """
    profile = tool_student_profile(student_id)
    s = profile["student"]
    notes = profile["dev_notes"]
    pairings = profile["pairings"]

    # Demo casting: Arun (S105) is anchored on Science to match the featured
    # teacher screen (Teacher David Chen) — keeps the demo narrative coherent.
    if student_id == "S105" and subject_filter is None:
        subject_filter = "Science"

    if subject_filter:
        filtered = [p for p in pairings if p["subject"] == subject_filter]
        if filtered:
            pairings = filtered

    primary_specialist = pairings[0]["tutor_name"] if pairings else "their specialist"
    primary_subject = pairings[0]["subject"] if pairings else "their subjects"

    # Pronoun-correct fallback (uses the child's name where possible)
    gender = (s["gender"] or "").lower()
    sub, pos = ("she", "her") if gender == "female" else ("he", "his") if gender == "male" else ("they", "their")

    canned_fallback = f"""Dear Family of {s['name']},

{s['name']} has had a meaningful month at North Star Learning Center. In {primary_subject} with {primary_specialist}, we have been watching {pos} engagement carefully and supporting {pos} growth at {pos} own pace.

{s['name']}'s current focus is on building strong foundations in {primary_subject}, and {pos} teachers are using approaches that have worked well with children sharing {pos} profile. We will share {pos} progress next month.

If you have questions about {s['name']}'s journey, please reach out to the centre manager any time.

— North Star Learning Center"""

    if not GEMINI_AVAILABLE:
        return {"story": canned_fallback, "source": "canned (no API key)"}

    dev_notes_str = "\n".join(f"  - {n['dimension']}: {n['observation']}" for n in notes[:5])
    prompt = f"""You are writing a warm, plain-English monthly update letter to the parent of a child at
North Star Learning Center, a premium small-class tuition centre in Subang, Malaysia.

CHILD:
  Name: {s['name']}
  Level: {s['level']}
  Primary subject this month: {primary_subject}
  Specialist teaching this subject: {primary_specialist}

RECENT TEACHER OBSERVATIONS (use these to ground the story):
{dev_notes_str if dev_notes_str else "  (No recent observations on file.)"}

RULES:
  - Write a single letter, 4-6 short paragraphs, warm and dignified.
  - NEVER include raw numeric scores or comparisons to other children.
  - DO mention one growth moment and one current focus area.
  - DO explain briefly why the specialist is teaching this child (skill match).
  - End with: "Questions? Reach the centre manager any time."
  - Sign off as: "— North Star Learning Center"
  - No bullet points, no headings, prose only.
  - Maximum 220 words.
"""
    try:
        resp = gemini_model.generate_content(
            prompt, generation_config={"temperature": 0.4, "max_output_tokens": 600}
        )
        return {"story": resp.text.strip(), "source": "gemini-2.0-flash"}
    except Exception as e:
        return {"story": canned_fallback, "source": f"fallback ({e})"}


# ===========================================================================
# Routes
# ===========================================================================
@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PATH.read_text(encoding="utf-8")


@app.get("/api/manager/home")
def api_manager_home(vertical: str = "tuition"):
    cfg = VERTICAL_CONFIG.get(vertical, VERTICAL_CONFIG["tuition"])
    return JSONResponse({
        "vertical": vertical,
        "config": cfg,
        "manager_name": "Cikgu Mei",
        "snapshot": tool_centre_snapshot(),
        "attention": tool_at_risk_children(),
        "wellbeing": tool_teacher_wellbeing(),
        "parent_stories_drafted": 18,
    })


@app.get("/api/manager/escalation/{sid}")
def api_escalation(sid: str):
    p = tool_student_profile(sid)
    s = p["student"]
    pairings = p["pairings"]

    # Featured Arun Prakash case
    if sid == "S105":
        return JSONResponse({
            "student": {"id": sid, "name": s["name"], "level": s["level"], "age": s["age"]},
            "situation": {
                "subject": "Science",
                "current_label": "Developing",
                "current_score": 52.0,
                "current_specialist": pairings[0]["tutor_name"] if pairings else "—",
                "pairing_health": "Steady — needs targeted support",
            },
            "story": (
                f"{s['name']} has been at North Star for 2 years. Science is the Year 4 anchor "
                f"subject for him this year. Recent observations show he memorises facts but "
                f"struggles to apply them to multi-step problems. He is engaged in hands-on lab "
                f"activities — which suggests his learning is concrete-first."
            ),
            "ai_suggestion": {
                "type": "support_intervention_with_current_specialist",
                "headline": "Keep current specialist. Apply scaffolded multi-step approach.",
                "rationale": (
                    "Children with lab-strong, application-cautious profiles have shown +10-12 "
                    "point improvement under a scaffolded multi-step method. Teacher David Chen "
                    "(Experienced, 4 yrs) has used this successfully with similar profiles. "
                    "No specialist rematch needed."
                ),
                "confidence": "high",
                "based_on": "8 similar profiles in the past 6 months",
                "next_step": "Tag this approach in his pairing and review in 2 cycles."
            }
        })

    # Generic case
    return JSONResponse({
        "student": {"id": sid, "name": s["name"], "level": s["level"], "age": s["age"]},
        "situation": {"current_specialist": pairings[0]["tutor_name"] if pairings else "—"},
        "story": "Profile review in progress.",
        "ai_suggestion": {"headline": "Generic case — no suggestion yet."}
    })


@app.get("/api/teacher/{tid}/home")
def api_teacher_home(tid: str):
    return JSONResponse(tool_teacher_home(tid))


@app.get("/api/parent/{sid}/story")
def api_parent_story(sid: str, subject: Optional[str] = None):
    p = tool_student_profile(sid)
    # Anchor demo (S105) on Science so the letter matches the featured teacher screen
    chosen_subject = subject or ("Science" if sid == "S105" else None)
    pairings = p["pairings"]
    if chosen_subject:
        scoped = [pp for pp in pairings if pp["subject"] == chosen_subject]
        if scoped:
            pairings = scoped
    story = tool_parent_story(sid, chosen_subject)
    return JSONResponse({
        "student": p["student"]["name"],
        "level": p["student"]["level"],
        "primary_specialist": pairings[0]["tutor_name"] if pairings else None,
        "primary_subject": pairings[0]["subject"] if pairings else None,
        "story": story["story"],
        "ai_source": story["source"],
    })


@app.get("/api/directory")
def api_directory():
    return JSONResponse(tool_centre_directory())


@app.get("/api/peer-mentor/{link_id}/draft-note")
def api_draft_peer_note(link_id: str):
    """Gemini drafts a short, warm peer-mentor note (max 2 sentences)."""
    with db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT pml.reason, pml.suggestion,
                   st.name AS senior_name, st.band AS senior_band, st.subject AS senior_subject,
                   jt.name AS junior_name, jt.band AS junior_band, jt.subject AS junior_subject
            FROM peer_mentor_links pml
            JOIN tutors st ON pml.senior_tutor_id = st.tutor_id
            JOIN tutors jt ON pml.junior_tutor_id = jt.tutor_id
            WHERE pml.link_id=?
        """, (link_id,))
        row = c.fetchone()
    if not row:
        raise HTTPException(404, "Peer mentor link not found")

    short_junior = row["junior_name"].replace("Teacher ", "")
    canned = (
        f"Hi {short_junior}, I noticed your class has been working through some tricky material. "
        f"Want to grab a coffee this week — I'd love to share a step-by-step approach that worked "
        f"well for me with similar children."
    )

    if not GEMINI_AVAILABLE:
        return JSONResponse({"draft": canned, "source": "canned (no API key)"})

    prompt = f"""Draft a short, warm peer-mentor note from {row['senior_name']} (P4-P6 Science,
Experienced teacher at North Star Learning Center, Subang) to {row['junior_name']} (P4-P6 Science,
Junior teacher in his first year).

CONTEXT (why the note is being sent): {row['reason']}
SUGGESTION FROM THE AI: {row['suggestion']}

RULES:
- Exactly 2 sentences. No more, no less.
- Sounds like a peer offering help — not a senior lecturing.
- Warm, plain Malaysian-English. Use the junior teacher's first name only ({short_junior}).
- No greeting line ("Hi", "Dear" is fine, "Selamat pagi" too). No formal sign-off.
- Output ONLY the 2-sentence note, nothing else.
"""
    try:
        resp = gemini_model.generate_content(
            prompt, generation_config={"temperature": 0.6, "max_output_tokens": 180}
        )
        return JSONResponse({"draft": resp.text.strip(), "source": "gemini-2.0-flash"})
    except Exception as e:
        return JSONResponse({"draft": canned, "source": f"fallback ({e})"})


@app.get("/api/health")
def health():
    return {"ok": True, "gemini": GEMINI_AVAILABLE}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
