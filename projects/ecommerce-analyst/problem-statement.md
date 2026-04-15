# Ecommerce Analyst — Problem Statement

**Date:** 2026-04-15
**Template base:** `ai-agent/ecommerce` (`C:\Users\Lenovo\Documents\02_Pau-AI\template\ai-agent\ecommerce\`)
**Reference quality bar:** Bright Path Tuition

---

## The Problem

Mid-size Malaysian e-commerce sellers — solo founders or 2-5 person teams running RM30K–RM300K/month GMV across multiple categories on e-commerce platforms — are the busiest people in their business. They pack orders, answer customer chats, run ads, manage listings, and handle fulfillment themselves. There is no analyst on the team, no spare hour in the day, and no budget for the obvious external fix.

Freelance e-commerce consultants are expensive (RM3K–10K per project), jargon-heavy when the seller needs plain Malay / English, and raise a confidentiality concern the seller can't shake: the same consultant often serves competing sellers in the same niche. Platform-native seller dashboards give GMV and conversion views but do not cross-slice profit after discounts, returns, and shipping cost by state — so the seller sees revenue rise while net margin silently erodes.

The result: the seller knows their business is working in some places and leaking in others, but cannot see where, cannot hire to find out, and cannot trust an outsider enough to show the data.

## Who It Is For

A mid-size Malaysian e-commerce seller:
- Solo or 2-5 person team
- RM30K–RM300K/month GMV
- Multi-category store (home, grocery, lifestyle, general merchandise)
- Sells through an e-commerce platform (payments handled by the platform)
- Ships nationwide across all Malaysian states
- Has access to platform transaction export (CSV) but no analyst on staff
- Bilingual operator (English / Bahasa Malaysia)

## What Good Looks Like

The seller gets a private, always-available analyst-in-a-box that:

1. **Answers plain-language questions** — "what's eating my margin this month?", "is my 15% Raya discount actually profitable?", "which state is unprofitable to ship to?" — grounded in their own transaction data, no jargon.
2. **Delivers a Monday morning brief** — every Monday 7am, auto-generates a short "wins / worries / one decision to make this week" digest from the past week's data, without the seller asking.
3. **Preserves confidentiality** — runs on the seller's own app instance, no human consultant sees the data, no shared-consultant competitor-leak risk.
4. **Costs less than a part-time hire** — targets ~RM300/month all-in vs RM3K–10K for freelance equivalent.

## What Is Out of Scope (v1)

- Live e-commerce platform API integration — v1 is CSV upload
- Taking actions inside the seller's platform dashboard (pausing SKUs, adjusting prices) — advisory only
- Competitor / market intelligence beyond the seller's own data
- Anomaly alerts on every data refresh (deferred to v2)
- Suggested-next-question follow-up prompts (deferred to v2)

## Coverage Estimate

The v1 build solves approximately **80%** of the root problem (bandwidth + trust + affordability + plain language + proactive blind-spot flagging via the Monday brief). The ~20% gap is acting on recommendations inside the e-commerce platform (deferred) and full strategic consulting beyond the data (out of scope by design).

## Data

**Source dataset:** `Cash Cows Discounts and Delays/dataset.csv` (34,500 transactions, exactly matches the `ai-agent/ecommerce` template config).

**Data prep required before build:**
1. Remap `region` column from generic zones (West, South, etc.) to Malaysian states (Perlis, Kedah, Penang, Perak, Selangor, KL, Negeri Sembilan, Melaka, Johor, Pahang, Terengganu, Kelantan, Sabah, Sarawak, plus federal territories as applicable)
2. Drop `payment_method` column — on e-commerce platforms, payment is processed by the platform and the seller has no visibility
3. Preserve all other columns (order_id, customer_id, product_id, category, price, discount, quantity, order_date, delivery_time_days, returned, total_amount, shipping_cost, profit_margin, customer_age, customer_gender)
4. For the GitHub Pages demo, reduce to a random 150-row sample and pre-compute all 6 quick-action answers + one example Monday brief

## Deployment Targets

1. **GitHub Pages demo** (`lyven81/ai-project`) — static HTML, pre-computed answers, 150-row sample dataset. No live LLM calls. Uses Bright Path Tuition's two-panel demo layout.
2. **Cloud Run live app** (optional v1.5) — full FastAPI + Gemini backend, CSV upload, live Q&A, scheduled Monday brief.
3. **pauanalytics.com case study + AI assistant page** — published via the new-pau-analytics publish skills.

## Naming Note

App name: **Ecommerce Analyst**. No mention of any specific platform (Shopee, Lazada, TikTok Shop) anywhere in the product, problem statement, UI copy, or case study — to avoid trademark/copyright concerns and keep positioning platform-agnostic.
