# Ecommerce Analyst

## What We Are Building
A private analyst-in-a-box for mid-size e-commerce sellers — answers plain-language questions about their sales data and ships a proactive Monday morning brief, all without sharing data with any outside party.

## Who It Is For
Mid-size Malaysian e-commerce seller (solo or 2–5 person team) running RM30K–RM300K/month GMV across multiple categories on an e-commerce platform, shipping nationwide, no analyst on staff.

## Domain
SME & Business Tools — specifically multi-category online retailers in Malaysia.

## The Problem
Busy sellers drown in packing, customer service, ads, and fulfillment. They can't afford freelance analysts (RM3–10K/project), can't trust them (confidentiality/competitor risk), and don't have time to DIY-analyze their own data. Platform-native dashboards show revenue but not net margin after discounts, returns, and shipping. The seller sees sales rise while profit silently erodes.

## Core Features
| No. | Feature | What It Does | AI or Standard |
|---|---|---|---|
| 1 | Ask Anything (Chat) | Plain-language questions → grounded answers with numbers | AI |
| 2 | Monday Morning Brief | Weekly auto-digest: 3 wins / 3 worries / 1 decision | AI |
| 3 | 6 Preset Quick-Actions | One-click common analyses | Standard → AI answer |
| 4 | CSV Upload + Smart Remap | Auto-detect columns, remap region to Malaysian states | Standard |
| 5 | Answer History + Export | Save every Q&A and brief; export PDF | Standard |

## What Makes It Different
A private analyst that lives inside the seller's own app instance, answers in plain Malay-flavored English at 11pm between packing runs, and proactively ships a "what you missed last week" brief every Monday — at a cost and confidentiality level no human consultant and no platform-native dashboard can match.

## Tech Stack
| Layer | Choice | Reason |
|---|---|---|
| AI Model | Gemini 2.5 Flash (primary), Claude Haiku 4.5 (fallback) | Fast, cheap, strong at structured data reasoning |
| Frontend | Vanilla HTML + Chart.js + Poppins font (Bright Path Tuition pattern) | Zero build step, mobile-friendly, GitHub Pages ready |
| Backend (v1.5 only) | FastAPI + pandas | Matches existing portfolio stack |
| Database | SQLite | Lightweight, per-instance |
| Scheduler | Cloud Run Cron | Native Monday 7am MYT trigger |
| Deployment | GitHub Pages (static demo) + Cloud Run (live v1.5) | Two-tier launch |

## Screens and User Flow
- **Upload & Setup** — CSV drop OR sample data option
- **Dashboard + Chat** — top KPIs / left = Monday Brief + 6 quick-actions / main = chat
- **Monday Brief** — full weekly digest view
- **History & Export** — all past answers, searchable

**Flow:** `[Upload & Setup] → drop CSV or pick sample → [Dashboard + Chat] → click quick-action OR type question → see answer → [Monday Brief] every Monday → read brief → back to chat → [History] to review`

## UI Style
Mobile-first two-panel layout, Poppins font, cream+gold palette (matches Bright Path Tuition), conversational tone ("speak like a smart friend, not a BI tool"). Suits the seller who lives on their phone between packing runs.

## Demo Scenario
**Meet Aminah** — 34, solo operator of "Rumah Aminah" online store selling home essentials + groceries across all 13 Malaysian states, 2,400 orders last month.

1. Monday 7am, Aminah is packing orders, coffee cold, bank balance ≠ her Seller Centre "Total Sales."
2. She opens Ecommerce Analyst on her phone. Monday Brief is waiting.
3. Brief: "3 wins: Kitchen +18%, Klang Valley returns 2.1%, RM5 Free Shipping voucher brought 142 new buyers. 3 worries: Sabah returns 12% (RM1,240 margin eaten), Baby category -RM0.80/order, 11.11 preview discount below break-even on 3 SKUs. 1 decision: Stop shipping the 2kg rice cooker to Sabah — losing RM34/order."
4. Aminah taps the Sabah finding → chat opens → asks "which SKUs specifically?" → ranked list of 3.
5. Pauses 2 worst SKUs in 5 minutes, moves on to packing. More useful business advice in 7 minutes than the RM4K consultant gave her last year.
