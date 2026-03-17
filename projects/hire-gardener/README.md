# 🌿 Hire Gardener

An AI-powered grass cutting service finder that handles all vendor communication on your behalf — from first contact to job verification.

You describe the area and share a photo. The AI finds providers, sends messages, collects quotes, confirms the booking, and verifies completion. Service providers communicate naturally over WhatsApp without knowing they are talking to an AI.

---

## How It Works

| Stage | What Happens |
|---|---|
| 1. Discovery | AI finds 3 grass cutting providers in your area |
| 2. Outreach | Contacts all providers to confirm they cover your area |
| 3. Quoting | Sends your area photo and video, requests rates and availability |
| 4. Selection | You pick the best provider from a comparison table |
| 5. Confirmation | AI confirms booking and job scope with the chosen provider |
| 6. Verification | AI checks completion evidence against the agreed scope |

---

## Quick Start — Mock Mode (No WhatsApp Needed)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start Ollama (local LLM)
ollama serve

# Run the app
streamlit run ui.py
```

Open `http://localhost:8501` in your browser.

Mock mode simulates three vendors using Llama3 locally. No API keys or WhatsApp account needed.

---

## Switching to Real WhatsApp

1. Create a [Meta WhatsApp Business API](https://developers.facebook.com/docs/whatsapp) account
2. Register a dedicated phone number (a Malaysian prepaid SIM works)
3. Update `.env`:

```
MODE=real
WHATSAPP_API_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_id
```

See [user guide.md](user%20guide.md) for full setup instructions.

---

## Tech Stack

| Component | Tool |
|---|---|
| UI | Streamlit |
| LLM | Ollama + Llama3 (local, free, no API cost) |
| Vendor simulation | Llama3 with persona prompts |
| Real messaging | Meta WhatsApp Cloud API |
| Workflow logic | Python |

---

## Architecture

```
config.py  (MODE flag)
     │
     ├── mock mode  →  messaging/mock.py      (Llama3 simulates vendors)
     └── real mode  →  messaging/whatsapp.py  (Meta WhatsApp API)
                │
                └── workflow.py  (6-stage logic)
                         │
                         └── agent.py  (Llama3 composes messages)
                                  │
                                  └── ui.py  (Streamlit interface)
```

---

## Requirements

- Python 3.10 or above
- [Ollama](https://ollama.com) with `llama3` model installed
- Streamlit, requests, pandas, python-dotenv

---

## Why a Dedicated Phone Number?

Using a personal WhatsApp number with automation tools risks a ban. This app is designed to use a **dedicated number** registered through Meta's official WhatsApp Business Cloud API — no ban risk, and providers see a legitimate WhatsApp Business account.

---

## License

MIT — free to use, modify, and deploy.
