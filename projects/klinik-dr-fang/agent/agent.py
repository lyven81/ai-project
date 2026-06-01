"""
agent.py — the conversational layer for the Klinik Dr Fang front-desk assistant.

Two interchangeable modes, BOTH driving the SAME governed toolset:

  LIVE  (--live)   Gemini Flash does the reasoning + summarising.
                   Bring-your-own-key: reads GEMINI_API_KEY from the environment
                   or a local .env file. Your key, your (tiny) cost. Nothing is
                   hard-coded and nothing is committed.

  DEMO  (default)  A deterministic keyword router — no LLM call, zero cost,
                   fully reproducible. Same tools, same guardrails.

Whichever mode runs, the agent can ONLY act through tool_runner.GovernedToolset.
It has no ability to author SQL, reach other tables, or change a query.

Usage:
    python agent/agent.py            # deterministic demo mode
    python agent/agent.py --live     # live Gemini mode (needs GEMINI_API_KEY)
"""
import os, sys, re
from datetime import date, timedelta
from tool_runner import GovernedToolset

TODAY = date.today()
TS = GovernedToolset()

PERSONA = (
    "You are the front-desk assistant for Klinik Dr Fang, a single-doctor GP clinic "
    "in Petaling Jaya. You help the practice manager spot PATTERNS in patient records "
    "(busy periods, symptom clusters, lapsing patients, trends). "
    "You may ONLY answer using the provided tools. You cannot write SQL, list tables, "
    "or read anything a tool does not return. If a request needs a capability you do "
    "not have a tool for, say so plainly and explain why (the system is built so the "
    "assistant can only run pre-approved, read-only queries). "
    "You SURFACE information; you never diagnose or give clinical advice — the clinician "
    "interprets. Today's date is " + TODAY.isoformat() + "."
)

# ----------------------------------------------------------------------------
# Thin, typed wrappers — one per governed tool. The LLM (live mode) calls these
# by name; each simply forwards to the governed toolset. No tool can do more
# than tools.yaml allows.
# ----------------------------------------------------------------------------
def cluster_recent_symptoms(start_date: str, end_date: str) -> list:
    """Group recent presenting complaints into clusters of similar symptoms (outbreak signal). Dates are YYYY-MM-DD."""
    return TS.run("cluster_recent_symptoms", start_date=start_date, end_date=end_date)

def find_similar_cases(case_id: int, top_k: int) -> list:
    """Find past cases whose presentation most resembles a given case_notes id."""
    return TS.run("find_similar_cases", case_id=case_id, top_k=top_k)

def theme_complaints(start_date: str, end_date: str) -> list:
    """Group a period's complaints into themes and count each. Dates are YYYY-MM-DD."""
    return TS.run("theme_complaints", start_date=start_date, end_date=end_date)

def condition_trend(condition: str, since_date: str) -> list:
    """Monthly count of a diagnosed condition since a date, e.g. condition='Dengue (suspected)'."""
    return TS.run("condition_trend", condition=condition, since_date=since_date)

def attendance_trend(start_date: str, end_date: str) -> list:
    """No-show rate by weekday within a date window. Dates are YYYY-MM-DD."""
    return TS.run("attendance_trend", start_date=start_date, end_date=end_date)

def demand_pattern(start_date: str, end_date: str) -> list:
    """Attended-visit volume by weekday within a window (when the clinic is busiest)."""
    return TS.run("demand_pattern", start_date=start_date, end_date=end_date)

def frequent_attenders(min_visits: int, since_date: str) -> list:
    """Patients with at least min_visits attended visits since a date. Returns name + count."""
    return TS.run("frequent_attenders", min_visits=min_visits, since_date=since_date)

def complaint_spike(month: str) -> list:
    """Top presenting complaints in a given month (YYYY-MM)."""
    return TS.run("complaint_spike", month=month)

def segment_patients() -> list:
    """Segment the whole patient base by visit frequency and average spend."""
    return TS.run("segment_patients")

def list_inactive_patients(since_date: str) -> list:
    """Patients with no visit on/after the cut-off date (lapsing / recall list). Name + last visit only."""
    return TS.run("list_inactive_patients", since_date=since_date)

LIVE_TOOLS = [cluster_recent_symptoms, find_similar_cases, theme_complaints,
              condition_trend, attendance_trend, demand_pattern, frequent_attenders,
              complaint_spike, segment_patients, list_inactive_patients]


# ----------------------------------------------------------------------------
# LIVE mode — Gemini with automatic function calling (BYOK)
# ----------------------------------------------------------------------------
def load_env():
    """Minimal .env loader so BYOK works without extra dependencies."""
    path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def run_live():
    load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("No GEMINI_API_KEY found. Get a free key at https://aistudio.google.com/apikey")
        print("then put  GEMINI_API_KEY=...  in a .env file, or export it. "
              "Falling back to deterministic demo mode.\n")
        return run_demo()
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        tools=LIVE_TOOLS,
        system_instruction=PERSONA,
    )
    chat = model.start_chat(enable_automatic_function_calling=True)
    print("Klinik Dr Fang assistant — LIVE (Gemini). Type 'quit' to exit.\n")
    while True:
        try:
            q = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"quit", "exit"}:
            break
        if not q:
            continue
        try:
            resp = chat.send_message(q)
            print("\nassistant >", resp.text, "\n")
        except Exception as e:
            print("\nassistant > (error)", e, "\n")


# ----------------------------------------------------------------------------
# DEMO mode — deterministic keyword router (no LLM, zero cost)
# ----------------------------------------------------------------------------
def _fmt(rows):
    if not rows:
        return "No matching records."
    return "\n".join("   " + ", ".join(f"{k}: {v}" for k, v in r.items()) for r in rows[:12])

def route(q: str) -> str:
    ql = q.lower()
    d14 = (TODAY - timedelta(days=14)).isoformat()
    d180 = (TODAY - timedelta(days=180)).isoformat()
    d365 = (TODAY - timedelta(days=365)).isoformat()
    today = TODAY.isoformat()

    # ---- guardrail intents: requests with no matching tool ----
    if any(w in ql for w in ["delete", "drop", "update ", "insert", "remove "]):
        return ("Refused. I have no write tool of any kind — the database connection is "
                "read-only and no INSERT/UPDATE/DELETE capability exists for me.")
    if any(w in ql for w in ["full record", "everything", "all patients' phone", "phone number",
                             "raw sql", "custom sql", "run a query", "select *", "join all"]):
        return ("Refused. There is no tool that dumps full records or runs arbitrary SQL. "
                "I can only call pre-approved, parameterised pattern-finding queries — "
                "authoring SQL is not a capability I have.")

    # ---- pattern-finding intents ----
    # find_similar_cases needs an explicit case reference; clustering wins otherwise.
    if "resembl" in ql or re.search(r"case\s*#?\d+", ql) or ("similar" in ql and "case" in ql):
        m = re.search(r"case\s*#?(\d+)", ql)
        cid = int(m.group(1)) if m else 1
        return _fmt(find_similar_cases(cid, 5))
    if "cluster" in ql or "similar symptom" in ql or "outbreak" in ql or "similar symptoms" in ql:
        return _fmt(cluster_recent_symptoms(d14, today))
    if "theme" in ql or ("group" in ql and "complaint" in ql):
        return _fmt(theme_complaints(d180, today))
    if "no-show" in ql or "no show" in ql or "attendance" in ql:
        return _fmt(attendance_trend(d180, today))
    if "busiest" in ql or "busy" in ql or "demand" in ql:
        return _fmt(demand_pattern(d180, today))
    if "frequent" in ql or "visiting often" in ql or "too often" in ql or "unusually often" in ql:
        return _fmt(frequent_attenders(10, d365))
    if "spike" in ql:
        m = re.search(r"(\d{4}-\d{2})", ql)
        return _fmt(complaint_spike(m.group(1) if m else TODAY.strftime("%Y-%m")))
    if "segment" in ql:
        return _fmt(segment_patients())
    if any(w in ql for w in ["inactive", "lapsing", "haven't been", "havent been", "not been", "over a year", "recall"]):
        return _fmt(list_inactive_patients(d365))
    if "trend" in ql or "rising" in ql or "becoming more common" in ql or "more common" in ql:
        # try to lift a condition word
        for cond in ["dengue", "diabetes", "hypertension", "cholesterol", "asthma", "eczema", "migraine"]:
            if cond in ql:
                name = "Dengue (suspected)" if cond == "dengue" else cond.title()
                if cond == "diabetes": name = "Type 2 Diabetes"
                if cond == "hypertension": name = "Hypertension"
                if cond == "cholesterol": name = "High Cholesterol"
                return _fmt(condition_trend(name, d180))
        return _fmt(condition_trend("Dengue (suspected)", d180))

    return ("I can surface patterns: symptom clusters, condition trends, no-show/demand "
            "patterns, frequent attenders, complaint spikes, patient segments, and lapsing "
            "patients. I can't run free-form queries. What pattern would you like to see?")

def run_demo():
    print("Klinik Dr Fang assistant — DEMO (deterministic, no LLM, zero cost). "
          "Type 'quit' to exit.\n")
    while True:
        try:
            q = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"quit", "exit"}:
            break
        if q:
            print("\nassistant >\n" + route(q) + "\n")


if __name__ == "__main__":
    (run_live if "--live" in sys.argv else run_demo)()
