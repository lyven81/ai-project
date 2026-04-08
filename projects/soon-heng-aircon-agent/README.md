# Soon Heng Air-Cond Service — WhatsApp Service Agent

A scripted, self-contained WhatsApp customer service agent demo for **Soon Heng Air-Cond Service**, a Seremban/Nilai-based aircon servicing business.

## What it shows

The demo plays out a realistic 6-stage customer lifecycle on a WhatsApp-style interface — from first inquiry to post-service follow-up — entirely on the provider side. You watch the AI handle the conversation; you never type a message.

### 6 Stages

1. **Customer Inquiry** — Auntie Wong asks if Soon Heng services Seremban; AI confirms coverage and asks scoping questions
2. **Scoping** — Customer sends details + a photo of the unit; AI recommends a chemical wash and collects the address
3. **Quote** — AI generates a RM 220 chemical-wash quote for 2 units (1.5 hrs, chemicals included)
4. **Schedule** — Customer picks a 2:00 PM slot tomorrow
5. **Confirm + Reminder** — AI confirms booking and sends an automatic reminder that evening
6. **Follow-up** — Day after service, AI follows up, summarizes the work, and asks for a Google review

## Tech

- **Pure HTML/CSS/JS** — no backend, no API key, no build step
- WhatsApp dark-theme UI with sidebar dashboard (services, pricing, live stats)
- All conversation content is scripted — open `demo.html` in any browser

## Business Setup

- **Business:** Soon Heng Air-Cond Service
- **Service Areas:** Seremban, Nilai (only)
- **Hours:** 9am – 6pm, Mon–Sat
- **Services:** General Servicing, Chemical Wash, Gas Top-up, Compressor Repair, New Unit Installation

## Run

Open `demo.html` directly in a browser. Click **Play Demo**, then advance through each stage with the action button at the bottom of the chat.
