# Plumber WhatsApp Agent

## What We Are Building
A WhatsApp AI agent named Jamal that handles plumbing customer inquiries — scoping problems, quoting fixed prices, and booking time slots — so the real plumber Jamal never misses a job while he's on-site.

## Who It Is For
Solo plumber or 1-2 person plumbing team in the Klang Valley (PJ, Subang Jaya, Shah Alam). Handles 4-6 jobs per day, earns RM8,000-15,000/month. All customer communication on personal WhatsApp. No website, no booking system, no admin assistant.

## Domain
Home plumbing services — Malaysian residential market.

## The Problem
Encik Rajan (Jamal) is a solo plumber serving PJ, Subang, and Shah Alam. His entire business runs on WhatsApp — customers text him to ask about leaks, clogs, and installations, and he replies when he can. But for most of the day, his hands are wet and his phone is in his pocket, so messages sit unread for 1-2 hours at a time.

By the time he checks, 2-3 customers have already texted another plumber. WhatsApp Business auto-reply only sends a canned "I'll get back to you" — it can't scope the problem, give a price, or book a time slot. Full chatbot platforms cost RM200-500/month and require technical setup a solo tradesman won't do.

## Core Features
1. **Inquiry handler** — Greets customer, confirms service area, asks what the problem is (AI)
2. **Problem scoping** — Asks follow-up questions, requests photo, classifies issue to job type (AI)
3. **Fixed-price quoting** — Matches problem to job type, quotes a single fixed price with what's included (AI + Config)
4. **Schedule-aware slot booking** — Reads live schedule, offers next available slots, blocks double-booking, handles multi-slot jobs (Standard logic)
5. **Post-job follow-up** — Messages customer after appointment to confirm issue resolved, requests review (AI)

## What Makes It Different
A self-hosted, BYO-key AI agent that handles full 6-stage plumbing conversations on WhatsApp in bahasa santai, quotes fixed prices, and books slots from a real schedule — at ~1,000 tokens per turn (4-5x cheaper than general-purpose agent frameworks like OpenClaw or n8n AI agents), with zero monthly subscription.

## Tech Stack
| Layer | Choice | Reason |
|---|---|---|
| AI Model | Google Gemini Flash (BYO key) | Fast, cheap, good at bilingual EN-MS, free tier available |
| Frontend | Static HTML/CSS/JS (WhatsApp-style chat UI) | GitHub Pages compatible, no server needed for demo |
| Backend | None for demo; Flask/FastAPI for production | Demo uses client-side LLM calls |
| Database | localStorage + JSON seed (demo); SQLite (production) | Demo loads pre-seeded schedule |
| Deployment | GitHub Pages (demo); Cloud Run (production) | Free hosting for portfolio |

## Screens and User Flow

### Screen 1 — Landing / API Key Entry
- Shows: App title, what it does, API key input field
- User action: Pastes Gemini API key, clicks "Start Chat"

### Screen 2 — WhatsApp-Style Chat Interface
- Shows: Green header bar, white/light-green message bubbles, text input
- User action: Types customer messages, receives Jamal's replies in bahasa santai
- Displays 6-stage flow naturally through conversation

### Screen 3 — Booking Confirmation (inline in chat)
- Shows: Summary card — job type, price, date, time, address
- User action: Views confirmation within the chat flow

**User flow:**
[Landing] -> enter API key -> [Chat] -> describe problem -> Jamal scopes -> Jamal quotes fixed price -> Jamal offers available slots -> [Confirmation card in chat] -> Jamal follows up

## UI Style
Mobile-first WhatsApp-style chat interface with green header bar (#075E54), white/light-green (#DCF8C6) message bubbles, and rounded input field. Familiar to every Malaysian smartphone user, zero learning curve.

## Demo Scenario
1. **Situation:** Puan Siti notices water leaking from under her kitchen sink at 9 AM. She WhatsApps the plumber number she got from a neighbor.
2. **First action:** Jamal replies instantly: "Ha boleh boleh. Area mana ni? Saya cover PJ, Subang, Shah Alam."
3. **Core interaction:** Puan Siti says "kitchen sink bocor lah, dripping nonstop." Jamal asks "Kat bawah sinki ke, paip yang bocor? Boleh snap gambar?" She describes it. Jamal says "Ok paip bocor macam ni RM200, termasuk barang. Nak saya datang?"
4. **Result:** Jamal checks schedule: "Esok Selasa 10 pagi saya free. Atau Rabu 2 petang. Mana satu ok?" Puan Siti picks Tuesday. Jamal confirms: "Ok settle. Selasa 31 Mac, 10 pagi. Alamat Puan Siti kat mana? Nanti saya WhatsApp before sampai."
5. **What happens next:** After the job, Jamal messages: "Puan Siti, paip ok dah? Kalau ada masalah lagi boleh WhatsApp saya. Terima kasih ya!"

## Agent Personality
- Name: Jamal (same as the real plumber)
- Language: Bahasa santai — short, casual, friendly. Mix of Malay and English naturally.
- Never reveals he is AI. Customer must believe they are texting the real Jamal.
- Quotes fixed prices confidently — no ranges, no "tengok keadaan".
- Asks for photo before quoting if the problem description is unclear.

## Schedule
- Period: 30 March - 5 April 2026 (7 days, Mon-Sun)
- Hours: 9 AM - 6 PM (9 hourly slots per day)
- Capacity: 63 total slots, ~50% pre-booked (~31 slot-units)
- Stored as plumber_bookings.json, loaded at runtime

## Pricing (Fixed)
| Job | Slots | Price (RM) | Includes |
|---|---|---|---|
| Pipe leak repair | 2 | 200 | Labour + basic materials |
| Clogged drain / floor trap | 1 | 120 | Labour + drain snake |
| Tap/faucet replacement | 1 | 100 | Labour only (customer supplies tap) |
| Toilet repair (flush/leak) | 1 | 150 | Labour + standard parts |
| Toilet repair (major) | 2 | 280 | Labour + cistern set |
| Water heater install/replace | 2 | 300 | Labour + piping |
| Sink installation | 2 | 250 | Labour + piping + sealant |
| Pipe burst (emergency) | 2-3 | 350 | Labour + replacement pipe |
| Water pump repair/replace | 2 | 300 | Labour + wiring |
| Bathroom renovation plumbing | 3 | 600 | Labour + all piping and fittings |
