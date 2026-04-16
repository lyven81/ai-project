# Deploy to Google Cloud Run

Sundry Shop Assistant needs a persistent backend for WebSocket + Gemini Live API + MCP tools. Cloud Run is the right fit: pay per request, scales to zero, easy WebSocket support.

## One-time setup

### 1. Install Google Cloud CLI

Follow: https://cloud.google.com/sdk/docs/install

Verify:
```bash
gcloud --version
```

### 2. Log in and pick a project

```bash
gcloud auth login
gcloud projects list
gcloud config set project YOUR_PROJECT_ID
```

If you need a new project:
```bash
gcloud projects create sundry-shop-assistant --name="Sundry Shop Assistant"
gcloud config set project sundry-shop-assistant
```

### 3. Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### 4. Get a Gemini API key

https://aistudio.google.com/apikey

## Build and deploy

From the project root (`C:\Users\Lenovo\Documents\03_Portfolios\AI-Project\sundry shop assistant\`):

```bash
gcloud run deploy sundry-shop-assistant \
  --source . \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=YOUR_API_KEY_HERE,MODEL=gemini-3.1-flash-live-preview,VOICE_NAME=Puck" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 3600 \
  --concurrency 10 \
  --port 8080
```

**Why these flags:**
- `--region asia-southeast1` — Singapore, closest Google Cloud region to Kajang (lowest voice latency)
- `--allow-unauthenticated` — public URL (fine for demo; secure later)
- `--min-instances 0` — scales to zero when idle (no standing cost)
- `--max-instances 3` — hard ceiling to prevent runaway cost
- `--concurrency 10` — each instance handles up to 10 simultaneous users
- `--timeout 3600` — 1-hour max connection (WebSockets need long timeouts)
- `--memory 1Gi` — pandas + the Live API SDK fit comfortably

After deploy, you'll get a URL like `https://sundry-shop-assistant-xxxxxxx.a.run.app`.

## Cost cap (critical before sharing the URL)

Gemini Live API bills **per audio second**, not per token. A chatty user can burn through credits. Set a budget alert before anyone else tests the link.

```bash
# Create a budget that alerts at 50%, 90%, 100% of RM 50 (~USD 11) monthly
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="Sundry Shop Assistant budget" \
  --budget-amount=50MYR \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

Find your billing account ID:
```bash
gcloud billing accounts list
```

## Update after code changes

Re-run the same `gcloud run deploy` command — it redeploys in-place.

## Check logs

```bash
gcloud run services logs read sundry-shop-assistant --region asia-southeast1 --limit 50
```

## Tail logs live

```bash
gcloud run services logs tail sundry-shop-assistant --region asia-southeast1
```

## Rollback

```bash
gcloud run revisions list --service sundry-shop-assistant --region asia-southeast1
gcloud run services update-traffic sundry-shop-assistant \
  --region asia-southeast1 \
  --to-revisions=REVISION_NAME=100
```

## Delete (if you need to tear down)

```bash
gcloud run services delete sundry-shop-assistant --region asia-southeast1
```

---

## Local development

For faster iteration, run locally first:

1. Copy `.env.example` → `.env` and fill in `GEMINI_API_KEY`
2. Double-click `run-local.bat` — creates venv, installs deps, starts server, opens browser
3. App runs at `http://localhost:8000`

## Preview model caveat

We pin `gemini-3.1-flash-live-preview`. As of April 2026, this is **preview**, not GA — the API surface may shift before general availability. If deploys start failing after a SDK upgrade:

1. Re-pin `google-genai` in `backend/requirements.txt` to the version that last worked
2. Check https://ai.google.dev/gemini-api/docs/live for breaking changes
3. Adjust `gemini_live.py` to match the new API

## Known limitations

- **Preview model + preview SDK** — expect occasional quirks
- **Voice quality depends on model's BM coverage** — Puck voice handles BM reasonably; test Kore/Charon/Aoede if Puck sounds off
- **Mode switch reconnects session** — changing voice ↔ text output drops and reopens the WebSocket (~500ms). Conversation history is lost unless session_resumption is added.
- **No auth yet** — anyone with the URL can use it. Add Firebase Auth or Identity-Aware Proxy before shipping to a real customer.
