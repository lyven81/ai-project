# North Star Learning Center

> An AI ecosystem for personalized small-class education — built for Malaysia's post-UPSR PBD + UASA era.

**Live demo:** https://north-star-learning-center-522143897885.asia-southeast1.run.app

Submitted to **Build With AI 2026 KL — MyHack** (Sunway University, 16–17 May 2026).
Answers the Cradle hackathon brief: *"AI-enabled platform that treats ecosystem relationships as first-class, programmable entities."*

---

## What this is

A web app that gives three roles their own view of one supportive ecosystem:

| Role | What they see | What the AI does for them |
|---|---|---|
| **Manager** (Cikgu Mei) | Critical escalations, teacher check-ins, parent stories drafted, capacity | Detect gaps early; propose support (not surveillance); draft warm parent letters |
| **Teacher** (David Chen — featured) | Class care board, children needing help, wins to celebrate, lab grouping, Help-a-Colleague flag | Per-child 2-line interventions; AI-suggested lab groups; peer-mentor nudges |
| **Parent** (Arun Prakash's family) | A warm monthly story — no raw scores | Gemini drafts a dignified growth letter grounded in real dev notes |

Plus a **Centre Directory** secondary screen and a one-click **reskin to Crescendo Music Academy** (proves the engine is template-reusable across small-class learning verticals).

## Stack

| Layer | Tool |
|---|---|
| LLM | Gemini 2.0 Flash (Google AI Studio key) |
| Tool dispatch | MCP-style functions wrapped by Gemini Function Calling |
| Backend | FastAPI (Python 3.11) |
| Database | SQLite (ships in container) |
| Frontend | Vanilla HTML + CSS + JS (no framework) |
| Container | Docker (python:3.11-slim) |
| Hosting | Google Cloud Run (asia-southeast1) |

## Quickstart (local)

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Prepare data (renames students, seeds demo rows). Idempotent.
python prepare_data.py

# 3. Set your Gemini API key
cp .env.example .env
# edit .env and paste the key from https://aistudio.google.com/apikey

# 4. Run locally
python main.py
# Open http://localhost:8080
```

## Deploy to Cloud Run

One command from this folder:

```bash
gcloud run deploy north-star-learning-center \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_KEY_HERE
```

Cloud Build builds the Dockerfile and deploys. You get a public HTTPS URL in 2–3 minutes.

## The featured demo case

- **Featured at-risk child:** Arun Prakash (S105, P4, in C041 P4 Science with Teacher David Chen)
- **Featured teacher:** Teacher David Chen (T021, Experienced, 4 yrs)
- **Featured junior teacher needing support:** Teacher Ravi (T022, Junior, 0 yrs)
- **The pattern:** No student transfer. AI suggests scaffolded multi-step support intervention with current specialist; surfaces a peer-mentor nudge from David Chen to Teacher Ravi.

## Design principles (deliberately anti-surveillance)

1. **No raw scores to parents** — only a warm story
2. **No teacher rankings** — only wellbeing pulse + Help-a-Colleague support
3. **No social-skills scoring of children** — collaboration / discipline / creativity observed qualitatively only
4. **Children never access the platform directly** — protected from algorithmic exposure
5. **Same engine reskins across verticals** — config-driven, demo'd live with the piano-academy toggle

## Brief alignment

| Brief requirement | How North Star answers |
|---|---|
| AI-enabled platform | Gemini grounds every narrative output; MCP-style tools do the deterministic work |
| Relationships as first-class entities | `pairings`, `peer_mentor_links`, `group_sessions` are real DB tables |
| Created, managed, reused, improved automatically | Pairing health recomputed each assessment; outcomes feed back to match weights |
| Across programmes, countries, ecosystem actors | Vertical config swaps `children → students`, `specialists → instructors`, etc. |

## Files

```
north-star-app/
├── main.py              FastAPI backend + 6 MCP-style tools + Gemini call
├── demo.html            Single-page UI with 5 screens + role switcher
├── prepare_data.py      One-time data migration (rename, seed demo rows)
├── data.db              SQLite (already migrated and seeded)
├── Dockerfile           Cloud Run container build
├── requirements.txt     Python deps
├── .env.example         API key template
├── .gitignore           Excludes .env, etc.
└── README.md            This file
```

## License

Portfolio project by Lee Yih Ven · lyven81
