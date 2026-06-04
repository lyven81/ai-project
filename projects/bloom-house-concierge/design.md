# Bloom House Concierge ("Lucy") — Design

**Date:** 2026-06-04
**Slug:** `bloom-house-concierge`
**Template base:** `ai-agent/ecommerce` (florist customer-service agent)
**Reference quality bar:** Bright Path Tuition
**Architecture:** AI-First Customer Service (Architecture 2) + governed fixed-query toolset (klinik-dr-fang pattern)

---

## App name

**Lucy** — the Bloom House flower concierge. Talks to the customer directly; resolves what it can safely, escalates the rest to a human (the founder, surfaced to the customer as "Ms. Young, our manager").

## Core features

| No. | Feature | What it does | AI or Standard |
|---|---|---|---|
| 1 | Florist consultant | Recommends 2 real bouquets by occasion + budget + colour, each with a flower-meaning reason | AI (grounded) |
| 2 | Three-way decision gate | Routes every message to resolve / escalate / decline before answering | AI |
| 3 | Support answers | Delivery cut-off, coverage, care, hours, store location from the knowledge base | AI (grounded) |
| 4 | Order-status read | Looks up an order number; read only | Standard (SQL SELECT) |
| 5 | Warm handoff | Writes a Situation / Order / Mood / Reason summary for the human; shown owner-side only | AI + Standard |

## The three outcomes (the whole product)

Lucy decides, in this order, and the customer never sees the machinery:

1. **Resolve (information-type)** — answered by one of 8 fixed, approved tools.
2. **Escalate (decision-type)** — refund, cancel, order change, custom/bulk, complaint, upset, time guarantee. No tool exists for these, so they go to a human. Customer hears: *"One moment please, let me check this with our manager, Ms. Young."*
3. **Decline (out-of-bounds)** — private/internal/non-business. Not answered, not transferred. Customer hears: *"I'm sorry, but I'm unable to help with that. Is there anything else I can assist you with today?"*

### AI resolves vs human vs declined

| Resolve (AI) | Escalate (human) | Decline (neither) |
|---|---|---|
| Recommend by occasion/budget/colour | Refunds, cancellations | Staff counts |
| Delivery cut-off, coverage | Order changes (address, date, contents) | Staff schedules |
| Flower care, hours, store location | Custom / wedding / corporate / bulk | Staff names (except Ms. Young) & contacts |
| Flower meaning | Complaints, upset customers | Suppliers, profit/margins |
| Order-status read | Time-critical guarantees | Ownership, internal metrics |
| | | Non-business questions |

**Hard line:** Lucy can read, never commit. No refund/cancel/change tool exists, so those cannot run autonomously.

## Governed toolset (8 fixed tools)

`recommend_bouquets` · `get_delivery_cutoff` · `get_coverage_areas` · `get_care_tips` · `get_hours` · `get_store_location` · `flower_meaning` · `get_order_status`

The agent chooses **which** tool and supplies **parameter values only**. SQL strings are fixed in the page; no `execute_sql`, no schema browsing, no write tool. Read-only by construction.

## Tech stack

| Layer | Choice | Reason |
|---|---|---|
| Decision logic | Rule-based router + 3-way gate (JS) | Honest, self-contained, the governance brain |
| Data engine | **SQLite via sql.js (WASM)**, DB embedded as base64 in `data/db.js` | Real fixed queries run in-browser; works on GitHub Pages and from `file://` |
| Catalogue + orders | `bloom-house.db` (products, orders tables), built by `build_db.py` | Single source of truth for recommendations and order lookups |
| Knowledge | Fixed strings in the tools (delivery, care, hours, store) | Small, stable shop facts |
| Frontend | Single static `index.html` + 3 product pages | No backend, no API key |
| Hosting | GitHub Pages via `lyven81/ai-project` | Free, public, link-in-proposal |

Production path (paid build): swap the rule router for one Gemini classification call at the same function boundaries; vector store over the shop's pages; live Shopify order status; WhatsApp/email handoff to the founder. The gate and handoff logic stay unchanged.

## Knowledge base (Bloom House)

- **Stores:** Petaling Jaya HQ (Mon–Sun 9 AM–6 PM); KPJ Damansara Specialist Hospital 2 (Mon–Sat 9 AM–6 PM).
- **Delivery:** same-day in **KL & Selangor** (order by 5 PM); **within 2 days** to Penang, Johor and the rest of Peninsular Malaysia (about five hours' drive from PJ).
- **Every order:** free personalised card + a photo on delivery.
- **Support:** daily 9 AM–7 PM via WhatsApp and email.

## Screens and flow

- **Chat home** — storefront frame, Lucy greeting, 3 tabbed chip groups (Lucy can help · 11 / To a human · 10 / Declined · 8).
- **Recommendation result** — 2 bouquet cards (motif, price, reason); **View** opens the live product page.
- **Behind-the-scenes panel** (owner-facing) — detected intent, approved tool used, confidence, mood, decision (Resolved / Escalated / Declined), and the handoff summary passed to Ms. Young.
- **Product pages** — `products/peony-box.html`, `products/lily-pink.html`, `products/cond-stand.html`. Same palette and fonts as the chat page.

Flow: `Chat → read message → escalate? → decline? → pick approved tool → resolve (answer / recommend / track)`; otherwise escalate with summary, or decline politely.

## Files

```
bloom-house-concierge/
  index.html              # Lucy — the governed concierge (sql.js)
  data/db.js              # bloom-house.db embedded as base64 (auto-generated)
  bloom-house.db          # SQLite source (products, orders)
  build_db.py             # rebuilds the DB + db.js
  products/
    peony-box.html        # birthday pick 1 (RM189)
    lily-pink.html        # birthday pick 2 (RM169)
    cond-stand.html       # condolence (RM239)
  problem-statement.md
  design.md               # this file
  showcase.html           # code walkthrough (portfolio)
```

## Deployment

Published to `lyven81/ai-project` via `ai-project-publish`; live at `https://lyven81.github.io/ai-project/`.
