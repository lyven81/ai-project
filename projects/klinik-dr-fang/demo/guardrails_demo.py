"""
guardrails_demo.py — prove the no-free-SQL guarantee in code.

Each test below is SUPPOSED to fail. We assert that it does, demonstrating the
four governance layers from outline §6 are real, not rhetorical.

Run:  python demo/guardrails_demo.py
"""
import os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))
from tool_runner import GovernedToolset

ts = GovernedToolset()
PASS, FAIL = "PASS (refused as designed)", "FAIL (should have been refused!)"
results = []

def expect_refused(label, fn):
    try:
        fn()
        results.append((FAIL, label))
    except Exception as e:
        results.append((PASS, label, str(e)[:90]))

print("=" * 72)
print("Klinik Dr Fang — Guardrail demonstration (everything here SHOULD fail)")
print("=" * 72)

# Layer 1: the toolset is the agent's entire universe — no execute_sql exists.
expect_refused("Call a generic execute_sql tool",
               lambda: ts.run("execute_sql", sql="SELECT * FROM patients"))

# Layer 1: schema reconnaissance tool also does not exist.
expect_refused("Call list_tables to enumerate the schema",
               lambda: ts.run("list_tables"))

# Layer 1: no write tool of any kind.
expect_refused("Call a delete_appointments tool",
               lambda: ts.run("delete_appointments", status="no-show"))

# Layer 2: the SQL is fixed; the agent cannot smuggle in extra parameters.
expect_refused("Inject an unexpected parameter into a real tool",
               lambda: ts.run("list_inactive_patients", since_date="2025-06-01",
                              extra="'; DROP TABLE patients;--"))

# Layer 2: missing a required parameter is rejected, not guessed.
expect_refused("Omit a required parameter",
               lambda: ts.run("condition_trend", condition="Dengue (suspected)"))

# Layer 4: the database connection itself is read-only — writes are impossible
#          even if every layer above were bypassed.
def attempt_write():
    ts.con.execute("DELETE FROM appointments WHERE status='no-show'")
expect_refused("Attempt a direct write on the (read-only) connection", attempt_write)

# ---- report ----
print()
ok = True
for r in results:
    status, label = r[0], r[1]
    detail = f"  -> {r[2]}" if len(r) > 2 else ""
    print(f"  [{status}]  {label}{detail}")
    ok = ok and status.startswith("PASS")

print()
print("What the agent CAN do (its entire universe):")
print("   " + ", ".join(s["name"] for s in ts.specs()))
print()
print("RESULT:", "all guardrails held — no free SQL, no writes, no data dumps."
      if ok else "A guardrail FAILED — investigate above.")
sys.exit(0 if ok else 1)
