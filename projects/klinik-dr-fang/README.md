# Front-Desk AI Assistant — Klinik Dr Fang

A front-desk AI assistant that surfaces **patterns** across a clinic's patient
records in plain language — busy periods, symptom clusters, lapsing patients,
frequent attenders — while being **structurally incapable of leaking data or
running its own queries.**

The headline isn't *"I built an AI agent."* It's **"I built one a
privacy-sensitive clinic could actually trust."**

> All patient data here is **fully synthetic** (invented by `data/generate_data.py`).
> Klinik Dr Fang is a fictional clinic. No real records are used.

---

## Architecture

```
user question
   │
   ▼
agent  (Gemini Flash, or a deterministic router)   ── reasons about WHICH tool to call
   │                                                   never writes SQL
   ▼
GovernedToolset  (tool_runner.py ⟵ toolbox/tools.yaml)   ── the only gate to the data
   │                                                         fixed queries, bound params
   ▼
SQLite  (data/klinik.db, opened READ-ONLY)              ── right-sized for a one-desk clinic
```

This mirrors the enterprise **MCP Toolbox for Databases** pattern (agent → governed
tool layer → database), scaled down to a single-file SQLite store — the realistic,
right-sized choice for a single-doctor practice, not a shortcut.

## The no-free-SQL guarantee (the point of the build)

Enforced at four layers — see `toolbox/tools.yaml` and `demo/guardrails_demo.py`:

1. **The toolset is the agent's entire universe.** No `execute_sql` tool is defined,
   so arbitrary SQL is not a capability the agent has.
2. **The SQL is fixed; only values flow.** Each tool's query lives in `tools.yaml`;
   the agent supplies bound parameter *values* only — no injected `WHERE`/`UNION`.
3. **Toolset scoping = access control.** The front desk loads only `front_desk`;
   other roles would load other toolsets.
4. **Read-only database user (backstop).** The connection is opened `mode=ro`;
   no `INSERT`/`UPDATE`/`DELETE` is physically possible.

`execute_sql`, `list_tables`, and NL2SQL are all *available* in MCP Toolbox and are
deliberately switched **off** here. Choosing not to let the agent generate SQL is the
portfolio statement.

---

## Run it

```bash
pip install -r requirements.txt
python data/generate_data.py          # build the synthetic SQLite DB
python agent/tool_runner.py           # direct tool test (bypasses the agent)
python demo/guardrails_demo.py        # prove the guardrails (everything should be refused)
python agent/agent.py                 # chat — DEMO mode (no LLM, zero cost)
python agent/agent.py --live          # chat — LIVE mode (Gemini, BYOK)
```

### Bring-your-own-key (BYOK)

Live mode never ships a key. You supply your own:

1. Get a free key: <https://aistudio.google.com/apikey>
2. `cp .env.example .env` and paste your key into `.env` (git-ignored, stays local).
3. `python agent/agent.py --live`

Your key, your (tiny) Gemini Flash cost — cents at demo scale. Everything else
(SQLite, the tool layer, the guardrails) is free and local.

---

## What the agent can / can't do

**Can:** symptom clustering, condition trends, no-show & demand patterns, frequent
attenders, complaint spikes, patient segmentation, lapsing-patient recall lists —
all conversationally.

**Can't (by design):** write/edit/delete anything, dump full records, run free-form
SQL, or diagnose. It *surfaces* patterns; the clinician interprets.

## Files

| Path | Role |
|---|---|
| `data/schema.sql`, `data/generate_data.py` | Synthetic clinic schema + generator |
| `toolbox/tools.yaml` | The governed toolset — fixed, parameterized tools |
| `agent/tool_runner.py` | The only component that touches the DB (read-only) |
| `agent/embeddings.py` | Dependency-free embedding + cosine for the vector tools |
| `agent/agent.py` | Conversational layer — live (Gemini/BYOK) or deterministic |
| `demo/guardrails_demo.py` | Proves the four governance layers fail by design |
| `demo/demo_script.md` | The 3–4 minute walkthrough script |
| `showcase/index.html` | Live in-browser demo for GitHub Pages (BYOK explained) |
| `case-study/` | One-page case study (Refined Trust style) |
