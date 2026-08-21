# Deploying Kuala Sepetang Tour Boat to Cloud Run

The app is a single Python container. No build step, no Node, no database.

## What runs where

| Piece | Where it lives |
|---|---|
| Forecast | Open-Meteo, free tier, no key, called at request time and cached on disk |
| Engine | `src/config.py`, `forecast.py`, `moon.py`, `brain.py`, `rebooking.py` |
| Tools and loop | `src/tools.py`, `editor.py`, `agent.py` |
| API and page | `src/app.py`, `web/index.html` |
| Bookings | `data/bookings.json` |
| Schedules the assistant writes | `data/schedules/` |

## Before the first deploy

Two API keys. Claude is primary, Gemini is the fallback on the same tool
interface, so an outage on one does not take the jetty offline.

Put them in Secret Manager rather than in the image. The `.dockerignore` and
`.gcloudignore` both exclude `.env`, so a stray local key cannot ship by
accident.

```bash
PROJECT=your-project-id
REGION=asia-southeast1          # Singapore, closest to Perak

gcloud config set project $PROJECT
gcloud services enable run.googleapis.com secretmanager.googleapis.com \
                       cloudbuild.googleapis.com

printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-
printf '%s' "$GEMINI_API_KEY"    | gcloud secrets create gemini-api-key    --data-file=-
```

## Deploy

```bash
gcloud run deploy kuala-sepetang-tour-boat \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 120 \
  --concurrency 20 \
  --min-instances 0 \
  --max-instances 3 \
  --set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest
```

`--timeout 120` matters: a chat turn that chains several tool calls can take
thirty seconds or more, and the default would cut the stream off mid-answer.

`--min-instances 0` keeps the bill near nothing when the boat is not running.
The first request after an idle period pays a cold start of a few seconds. If
the operator finds that annoying at 6am, set it to 1 and accept the small
standing cost.

## After deploying

```bash
URL=$(gcloud run services describe kuala-sepetang-tour-boat --region $REGION --format='value(status.url)')
curl -s $URL/api/health
curl -s "$URL/api/board?days=5" | head -c 400
```

`/api/health` should report `confidence_measured: true`, `auth:
bring-your-own-key` and `server_holds_no_key: true`. If it reports false,
the Stage B results did not ship and the booking tiers on the page are the
hand-written estimates rather than the measured ones.

## Abuse and cost

`/api/board` and `/api/chat` are capped at 20 requests a minute per address.
Open-Meteo's open tier allows 10,000 calls a day and the cache does not survive
an instance recycling, so without the cap one impatient visitor could spend the
quota. Chat tokens are the visitor's own cost, but `MAX_ROUNDS 8`,
`max_tokens 2000` and `web_search max_uses 4` still apply: a runaway loop
spending someone else's money is worse, not better.

## Two things that will not survive a restart

Cloud Run containers have an ephemeral filesystem, so both of these are lost
when an instance recycles:

- **the forecast cache** in `data/cache/`, which only costs a repeat API call
- **the schedule files** in `data/schedules/{session}/`, which is the one that
  matters. Each visitor gets their own folder, so two people using the demo no
  longer edit the same file

For a demo that is fine. For an operator actually using it, mount a GCS bucket
with the Cloud Run volume mount, or move the schedules into Firestore. Until
then the schedule file is a working document inside a session, not a record.

## Running it locally

```bash
pip install -r requirements.txt
cd src
python -m uvicorn app:app --reload --port 8080
```

Then open http://127.0.0.1:8080. Keys are read from the environment, then a
project `.env`, then `~/.env`, so nothing machine-specific has to ship.

## Re-running the gates

Do this after any change to the thresholds, the activity table or the
classifier. Both must pass before the app is worth trusting.

```bash
cd src
python eval_stage_a.py        # classifier: planted shapes, invariants, distribution
python eval_rebooking.py      # reallocation: seven harm properties
python eval_stage_b.py        # horizon: forecast skill by lead time, refreshes the tiers
```

Stage B is worth re-running every few months. It reads the last 92 days, so the
measured tiers drift with the season, and the monsoon months will not score the
same as the inter-monsoon ones.
