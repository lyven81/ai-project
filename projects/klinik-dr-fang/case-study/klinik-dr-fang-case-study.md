# Case Study — A Front-Desk AI Assistant a Clinic Can Actually Trust

**Client (fictional):** Klinik Dr Fang, a single-doctor general practice in Petaling Jaya
**Type:** AI agent / agentic workflow over a private database
**Stack:** AI agent → MCP Toolbox–style governed tool layer → SQLite (read-only)
**Differentiator:** data governance over novelty

---

## The problem

A single-doctor clinic runs on one front-desk machine and a simple records system.
The practice manager wants quick answers to operational, population-level questions —
*"are we seeing a lot of similar cases lately?"*, *"who hasn't been in for a year?"* —
without learning to write database queries, and **without any risk of patient data
being over-exposed.**

Wiring an LLM straight to the database would answer the questions — and create exactly
the risk a clinic can't take: a cleverly worded prompt could make the model dump every
patient's record, or run a destructive query. For privacy-sensitive data, "it usually
behaves" is not good enough.

## The approach

The agent never touches the database. Between the agent and the data sits a **governed
tool layer**: a small set of pre-written, parameterized queries — the only actions the
agent can take. The agent's intelligence goes into *understanding the question and
choosing the right tool*, not into writing SQL.

Right-sizing matters: a single-file **SQLite** database is the correct store for a
one-desk clinic — matching infrastructure to the size of the business is part of the
consulting judgment, not a shortcut.

## The guarantee (four layers)

| Layer | Mechanism |
|---|---|
| Toolset = the agent's universe | No `execute_sql` tool exists; arbitrary SQL is not a capability the agent has |
| Fixed SQL, only values flow | Queries live in config; the agent supplies bound values — no injected `WHERE`/`UNION` |
| Toolset scoping | The front desk loads only its own tools; other roles get other toolsets |
| Read-only connection | Writes are physically impossible, even if every layer above were bypassed |

A scripted guardrail test confirms it: requests to dump records, delete appointments,
or author SQL are all **refused by design**, and the read-only connection rejects a
direct write.

## What it delivers

Conversationally, and in plain language:

- **Symptom clustering** — surfaced a respiratory cluster in the last two weeks
  (early-outbreak signal) that nobody explicitly searched for.
- **Condition trend** — suspected-dengue cases rising across six months.
- **Patient segmentation** — High-frequency / Regular / Occasional groups by visit
  frequency and spend.
- **Lapsing-patient recall** — patients not seen in over a year (name + last visit only).
- **No-show & demand patterns**, **frequent attenders**, **complaint spikes**.

These *are* the analytics service catalogue — segmentation, churn/recall, trend,
clustering — delivered as conversation: **the analytics a clinic needs, without anyone
learning to write a query.**

## Cost honesty

The database tier is rarely the biggest number — **model usage is.** At demo scale it
is cents (Gemini Flash). The public demo uses **bring-your-own-key**: the visitor
supplies their own free key, so the data layer and guardrails cost nothing to run.

## Why it matters

This is a concrete agentic-AI build that foregrounds **trust and governance over
novelty** — the difference between "wired an LLM to a database" and "built one a
regulated, privacy-sensitive business could put on its front desk."
