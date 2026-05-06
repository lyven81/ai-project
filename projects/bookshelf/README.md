# Bookshelf

Multi-agent AI system that turns a Malaysian book shop owner's sales data into a ranked product decision brief — what to push, drop, restock, and source.

Built on the Course Creator pattern: 5 specialised agents on Cloud Run, A2A protocol, with quality gating via a Pydantic-structured Judge.

---

## Architecture

```
USER → Web App (FastAPI + HTML/JS) → Orchestrator (SequentialAgent)
                                          ↓
                       LoopAgent(max_iterations=2)
                          ┌─────────────────────────────┐
                          │ Researcher → Judge → EscalationChecker
                          └─────────────────────────────┘
                                          ↓ pass
                                       Analyst
                                          ↓
                          ConditionalAgent(Trend Spotter)  ← only if user asked for sourcing
                                          ↓
                                       Writer → Markdown brief
```

**6 Cloud Run services:**
- `bookshelf-researcher`  (port 8001) — pandas-based metrics tool
- `bookshelf-judge`       (port 8002) — Pydantic verdict, data quality gate
- `bookshelf-analyst`     (port 8003) — SKU classification (push/hold/drop/restock-seasonal/discontinue/source-similar)
- `bookshelf-trend-spotter` (port 8004) — `google_search` for sourcing ideas
- `bookshelf-writer`      (port 8005) — final Markdown brief composition
- `bookshelf-web`         (port 8000) — UI + Orchestrator (folded together)

---

## Project Structure

```
book shop assistant/
├── pyproject.toml          ← root project deps
├── .env.example            ← copy to .env, set GOOGLE_API_KEY
├── run_local.sh            ← start all 6 services locally
├── init.sh                 ← one-time GCP project setup
├── deploy.sh               ← one-shot deploy to Cloud Run
├── README.md
├── user-guide.md
├── shared/                 ← imported by every agent service
│   ├── authenticated_httpx.py   ← service-to-service identity tokens
│   ├── a2a_utils.py             ← session-state save callbacks
│   └── adk_app.py               ← FastAPI A2A wrapper
├── agents/
│   ├── researcher/         ← Data Researcher (most domain-specific)
│   │   ├── agent.py
│   │   ├── data_tool.py    ← pandas-based metrics computation
│   │   ├── adk_app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── judge/              ← Forensic Judge (Pydantic verdict)
│   ├── analyst/            ← Portfolio Analyst (SKU classification)
│   ├── trend_spotter/      ← Trend Spotter (google_search)
│   └── writer/             ← Recommendation Writer (Markdown brief)
├── app/                    ← Web App + Orchestrator
│   ├── main.py             ← FastAPI: routes, SSE, run state
│   ├── orchestrator.py     ← SequentialAgent + LoopAgent + EscalationChecker + ConditionalAgent
│   ├── frontend/
│   │   ├── index.html      ← Course Creator-style landing + 5 quick questions
│   │   ├── style.css
│   │   └── app.js          ← state machine, SSE consumer, Markdown render, Copy
│   ├── Dockerfile
│   └── requirements.txt
└── dataset/
    ├── dataset.xlsx        ← bundled sample (Malaysian book shop, 2024–2025, 100k rows)
    ├── dataset-sample-150.csv
    └── generate_dataset.py ← reproducible generator (seeded)
```

---

## Quick Start (Local)

### 1. Install dependencies

```bash
# Use uv (recommended) or pip
pip install -r app/requirements.txt
pip install -r agents/researcher/requirements.txt
```

### 2. Get a Gemini API key

Free at <https://aistudio.google.com/apikey>.

```bash
cp .env.example .env
# Edit .env and paste GOOGLE_API_KEY=AIza...
```

### 3. Run all 6 services

```bash
chmod +x run_local.sh
./run_local.sh
```

Open <http://localhost:8000>.

The web UI will:
1. Ask you to set the API key (top-right; same key from .env will do, but the UI stores it in browser localStorage so it follows the visitor)
2. Pick a question or type your own
3. Watch the live agent log
4. Get the Markdown brief with a Copy button

### 4. Stop

`Ctrl+C` in the terminal — the script kills all 6 background services on exit.

---

## Deploy to Cloud Run

### One-time setup

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_REGION=asia-southeast1   # or us-central1, etc.
chmod +x init.sh deploy.sh
./init.sh
```

### Deploy all 6 services

```bash
./deploy.sh
```

The script deploys:
- 5 agents as **private** services (`--no-allow-unauthenticated`) — only the Web App SA can invoke them
- 1 Web App as **public** (`--allow-unauthenticated`) — visitors come here
- All with `min-instances=0` for cost control

### Costs

- **Cloud Run hosting:** with `min-instances=0` and low traffic, RM 0–10/month
- **Gemini API:** **paid by the visitor's BYO key**, not you. Each portfolio review = ~5 LLM calls on Flash = roughly USD 0.001
- **Trend Spotter:** uses `google_search` — extra cost only when triggered by question #5

---

## How the 5 Quick Questions Route

| Question | Behaviour |
|---|---|
| What's selling and what's not? | Standard pipeline; Writer emphasises Pareto + dead stock |
| What should I stock up for the next season? | Standard pipeline; Writer emphasises Seasonal Alerts |
| Which products should I drop? | Standard pipeline; Writer emphasises Dead Stock |
| Where am I wasting floor space? | Standard pipeline; Writer emphasises Channel Insights |
| Find me new product ideas to source | **Triggers Trend Spotter** + standard pipeline |

For free-form questions, the same routing logic looks for keywords (`source`, `new product`, `trend`) to decide whether to trigger Trend Spotter.

---

## Reference

- Architecture inspired by [Course Creator](https://github.com/lyven81/ai-project/tree/main/projects/course-creator)
- Google ADK + A2A protocol
- Gemini 2.5 Flash via BYO API key (Google AI Studio)

---

## License

MIT (see LICENSE).
