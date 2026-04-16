# Sundry Shop Assistant

## What We Are Building

A voice-first Malay business advisor that lets a Malaysian kedai runcit owner ask his own sales data business questions aloud and get spoken answers in seconds, with four flexible I/O modes to match changing shop conditions. Agent name: Adam.

## Who It Is For

Pak Ahmad, a 52-year-old Malay-speaking sundry shop owner in Kajang, Selangor. Runs his ~800 sqft shop alone from 7am to 10pm, 40–80 transactions a day, ~RM 2,500–4,500 daily revenue. Hands-busy behind the counter all day, never opens a dashboard.

## Domain

Retail analytics for Malaysian SME owner-operators — specifically voice-first business intelligence over POS sales data, backed by MCP-exposed tools.

## The Problem

Pak Ahmad has rich sales data sitting inside his POS but cannot open the dashboard during his 15-hour working day — he can't stop serving customers to type on a phone screen. By the time he closes at 10pm he is too tired to review anything, so every reorder, every loyalty decision, and every judgement about which category is actually paying his rent is made on gut feel.

The tools currently in the market do not fit his reality. Loyverse and StoreHub dashboards are English-only and visual. Grab Merchant only shows delivery. A bookkeeper costs RM 300–800/month with monthly cadence. No existing option lets him ask his sales data a question aloud in Malay and get a spoken answer in seconds, with a text fallback for moments when a customer is within earshot.

## Core Features

1. **Voice Q&A in Malay** — speak a question, hear a spoken answer (AI — Gemini Live API)
2. **MCP-backed sales tools** — 8 tools over the 150-row sundry shop dataset (AI + Standard)
3. **4-mode I/O toggle** — voice/text input × voice/text output, switchable anytime (Standard)
4. **Always-visible transcript** — scrollable Q&A log, works as verification and end-of-day review (Standard)
5. **Preset BM question chips** — 6 starter prompts for first-time discovery (Standard)

## What Makes It Different

The only voice-first Malay business advisor that sits on top of the owner's own sales data via MCP, with 4-mode I/O that adapts to changing shop conditions through the day — no POS dashboard, delivery platform, or generic voice assistant offers this combination for a Malaysian kedai runcit owner.

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| AI Model | Gemini Live API (`gemini-3.1-flash-live-preview`) | Native voice-to-voice in 70 languages (BM fluent), streaming WebSocket, barge-in, function calling during audio session |
| Frontend | Vanilla JS + Web Audio API + HTML/CSS | Lightweight, no build step, deploys as static assets; Web Speech API fallback for portfolio demo |
| Backend | FastAPI (Python) + WebSocket + MCP client | Hosts Live API session, mints ephemeral tokens, bridges MCP tool calls to Gemini function handlers |
| Database | Pandas-in-memory over `dataset.csv` (150 rows fits easily) | MCP server reads CSV at startup and exposes tools; sub-100ms query latency keeps voice flow natural |
| Deployment | Google Cloud Run (Option C — owner-pays) | WebSocket + MCP requires persistent backend; ephemeral token minting must be server-side |

## Screens and User Flow

**Screens:** Welcome / Mode Select, Conversation, Settings drawer.

**User flow (voice mode):**
`[Welcome] → tap Mula → [Conversation] → tap mic + speak BM question → agent transcribes + runs MCP tool + streams BM audio + shows text → follow up or barge in → continue asking`

**User flow (silent mode — customer nearby):**
`[Conversation] → toggle to ⌨️ Taip + 📄 Baca → type BM question → agent replies as text only → continue typing`

## UI Style

Mobile-first portrait layout, large tap targets, calm off-white background with green accent (#10B981), Poppins typography, single-column conversation view — suits a 52-year-old shopkeeper holding the phone in one hand while running the shop with the other.

## Demo Scenario

**Character:** Pak Ahmad, 52, sole owner of Kedai Runcit Pak Ahmad in Taman Sri Minang, Kajang.

1. It's 3:45pm on a Wednesday. A customer just picked up a packet of Milo and walked out. Pak Ahmad has 30 seconds before the next auntie arrives.
2. He taps the big green mic button: *"Tekan untuk bertanya."*
3. He asks: *"Hari ini kategori apa paling laku?"* The app shows the transcript live, runs MCP tool `top_categories_today`, and streams back: *"Sampai pukul 4 petang, sayur-sayuran paling laku hari ni, RM 312. Kedua, dairy, RM 215."*
4. Pak Ahmad barges in mid-answer: *"Sayur, perbandingan dengan minggu lepas?"* The app stops speaking, runs `compare_week_category`, replies: *"Minggu lepas tempoh sama, sayur RM 258. Minggu ni naik 21 peratus."* A small bar chart pops up.
5. Pak Ahmad nods, taps stop, opens WhatsApp to his vegetable supplier: *"Esok tambah 3 peti kangkung."* Total elapsed: 22 seconds. The next auntie walks in. He has never stopped running the shop.
