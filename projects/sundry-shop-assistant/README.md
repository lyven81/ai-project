# Sundry Shop Assistant — Adam

Voice-first Bahasa Malaysia (santai) business advisor for Malaysian kedai runcit owners. Ask your sales data out loud; hear the answer spoken back. Built on Gemini Live API + MCP-style tools over a POS dataset.

## Quick start (local)

1. Copy `.env.example` → `.env` and paste your Gemini API key (https://aistudio.google.com/apikey)
2. Double-click `run-local.bat` — creates venv, installs deps, starts backend, opens browser
3. Tap **Mula**, then the mic, and ask: *"Hari ni jualan berapa?"*

## Deploy to Cloud Run

See `deploy.md`.

## Architecture

```
Browser (index.html + js/)
  │
  │  WebSocket (/ws)
  │  ↓  PCM audio 16kHz  or  JSON text
  │  ↑  PCM audio 24kHz  or  JSON text
  │
FastAPI (backend/main.py)
  │
  │  google-genai SDK
  │
Gemini Live API (gemini-3.1-flash-live-preview)
  │
  │  function_call
  │  ↕
  └→ tool_bridge.py → mcp_tools.py → pandas(dataset.csv)
```

## Files

| Path | What it does |
|---|---|
| `index.html` | Welcome + Conversation screens |
| `css/style.css` | Mobile-first Poppins UI, green accent |
| `js/pcm-processor.js` | AudioWorklet — captures PCM from mic |
| `js/media-handler.js` | Mic capture at 16kHz, playback at 24kHz |
| `js/gemini-client.js` | WebSocket wrapper to backend `/ws` |
| `js/app.js` | UI logic, mode toggles, event handling |
| `backend/main.py` | FastAPI app, serves static + WebSocket `/ws` |
| `backend/gemini_live.py` | Gemini Live session wrapper |
| `backend/tool_bridge.py` | Gemini FunctionDeclarations for each tool |
| `backend/mcp_tools.py` | 10 MCP-style tools over `dataset.csv` |
| `backend/Dockerfile` | Container for Cloud Run |
| `backend/requirements.txt` | Pinned Python deps |
| `dataset.csv` | 150 rows — March 2024 sundry shop POS data |
| `system-prompt.txt` | Adam's santai BM persona + rules |
| `problem-statement.md` | Planner output — Step 2 |
| `project-outline.md` | Planner output — full design |
| `build-prompt.txt` | Reusable build prompt |
| `user-guide.md` | End-user guide in plain BM/English |
| `deploy.md` | Cloud Run deployment guide |
| `run-local.bat` | Start local dev server |
| `open-app.bat` | Open browser to localhost:8000 |

## Tools exposed to Gemini

All 10 tools live in `backend/mcp_tools.py` and are declared to Gemini in `backend/tool_bridge.py`.

| Tool | What it answers |
|---|---|
| `get_total_sales` | Total revenue, transaction count, avg basket |
| `get_top_day` | Best sales day |
| `get_weekly_summary` | Revenue by week |
| `get_sales_by_category` | Category ranking |
| `get_slowest_category` | Worst-performing categories |
| `compare_member_vs_visitor` | Loyalty program breakdown |
| `compare_gender` | Male vs Female spend |
| `get_payment_mix` | Cash vs card vs mobile |
| `get_payment_by_customer_type` | Payment preference by segment |
| `get_basket_stats` | Basket size, items per transaction, unit price |

## Swap to a real MCP server later

The tool contracts in `mcp_tools.py` mirror MCP's `tools/list` shape. To switch from in-process pandas to a real MCP server:

1. Spin up an MCP server exposing the same tool names + schemas
2. Replace the function bodies in `mcp_tools.py` with MCP client calls
3. Keep `tool_bridge.py` untouched — Gemini doesn't know the difference

## Tech stack

- **AI:** Gemini Live API (`gemini-3.1-flash-live-preview`) — voice-to-voice, native BM, barge-in, function calling
- **Backend:** FastAPI + WebSocket + google-genai SDK + pandas
- **Frontend:** Vanilla JS + Web Audio API + AudioWorklet
- **Deployment:** Google Cloud Run (owner-pays), region asia-southeast1 (Singapore)

## Known limitations

- Preview model — API may shift before GA
- Dataset is 150 rows (March 2024 only); multi-month trend questions cannot be answered
- No auth — add Firebase Auth before shipping to a real customer
- Mode toggle (voice ↔ text output) reconnects session; conversation history not preserved across switch yet
