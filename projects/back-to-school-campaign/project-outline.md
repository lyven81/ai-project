# Back-to-School

## What We Are Building
A BYO-key AI copywriting team that generates a coordinated 5-channel back-to-school campaign in Bahasa Melayu from a single brief.

## Who It Is For
Owner of a children's clothing store in Bangi, Malaysia. 1–3 staff, physical shop + WhatsApp catalogue, RM15K–80K/month revenue. Sells school uniforms (shirts, pinafores, PE attire, shoes, socks, bags). Runs marketing personally with no dedicated staff.

## Domain
Campaign management / copywriting for Malaysian SME retail

## The Problem
Every December/January and June, the owner needs to push back-to-school uniform campaigns across WhatsApp, Instagram, email, blog, and Google search. She writes one generic paragraph and pastes it everywhere — or skips channels entirely because writing different copy for each platform takes too long.

Free LLM chat tools can generate copy, but she re-explains her store, products, and tone every session and gets one draft back. This app bakes in the store context once and outputs a coordinated 5-channel campaign in Bahasa Melayu in one go.

## Core Features

| No. | Feature | What It Does | AI or Standard |
|---|---|---|---|
| 1 | Campaign Brief Input | User fills in store name, products, prices, campaign dates, target audience | Standard |
| 2 | 5-Channel Copy Generation | Gemini generates BM copy for WhatsApp, Instagram, Email, Blog, SEO from one brief | AI |
| 3 | Preset Campaign Briefs | 3 ready-made briefs (Back to School Jan, Mid-Year June, Year-End Clearance) | Standard |
| 4 | Copy-to-Clipboard | One-click copy per channel output | Standard |
| 5 | Tone Selector | Formal BM / Casual BM / Campur (BM-English mix) | AI |

## What Makes It Different
One brief produces five platform-tuned outputs simultaneously in Bahasa Melayu — WhatsApp urgency, Instagram hook, email drip, blog story, SEO keywords — at zero subscription cost via BYO-key.

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| AI Model | Gemini 2.0 Flash (BYO-key) | Fast, cheap, good at structured multi-output. User's own key. |
| Frontend | Single static HTML + Vanilla JS | GitHub Pages. No framework overhead. |
| Backend | None | Client-side Gemini API calls. |
| Database | None | No persistent data. |
| Deployment | GitHub Pages (lyven81/ai-project) | Free, instant. |

## Screens and User Flow

**Screen 1 — Campaign Brief Panel (left side)**
Store context form (pre-filled for demo), campaign details, tone selector, 3 preset buttons.

**Screen 2 — Copy Output Panel (right side)**
5 tabbed sections (WhatsApp, Instagram, Email, Blog, SEO), each with BM copy + copy button.

Flow: `[Brief Panel: fill or pick preset] → [Generate] → [Output Panel: 5 tabs] → [Copy per tab] → [Paste into platform]`

## UI Style
Two-panel desktop layout, brown/gold Poppins (portfolio standard). Form on left, tabbed output on right. Designed for a shop owner at a laptop between customers.

## Demo Scenario
1. Puan Siti owns Kiddoz Uniform House in Bangi. Early December — school reopens January 2. 200 sets in stock.
2. She clicks "Back to School (Januari)" preset. Form auto-fills with store details and product list.
3. She hits "Jana Kempen" and selects "BM Santai" tone. Five tabs light up in 8 seconds.
4. WhatsApp tab: punchy 4-line broadcast ending with "Balas 1 untuk tempah, balas 2 untuk carta saiz." Instagram tab: hook caption with BM hashtags. Email tab: 3-part drip. Blog tab: mum-buying-last-minute story. SEO tab: "baju sekolah murah Bangi" paragraph.
5. She copies WhatsApp version, pastes into broadcast list, sends before next walk-in. Total: 3 minutes.
