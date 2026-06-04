# Bloom House Concierge — Problem Statement

**Date:** 2026-06-04
**Template base:** `ai-agent/ecommerce` (florist customer-service agent)
**Reference quality bar:** Bright Path Tuition

---

## The Problem

Bloom House is a Malaysian online florist that sells into emotional moments: birthdays, anniversaries, get-well wishes, and condolences. The buyer usually knows the occasion but not what to send, is unsure what a normal amount to spend is, and is anxious about getting it right, so many close the tab without ordering. The few who do buy then message the shop with the same handful of questions about delivery cut-off times, coverage areas, tracking, and flower care, and they wait in a queue staffed by one or two people.

What goes wrong is that the routine load and the sensitive cases sit in the same slow line: a delivery that must reach a funeral on time, or wilted flowers before an event, waits behind "what time do you deliver to Johor?" Off-the-shelf store chat tools (Shopify Inbox, Tidio, Gorgias, Intercom) answer set FAQs but cannot act like a florist, recommending by occasion, budget, and flower meaning from the shop's real catalogue, and they treat an emotional escalation as an ordinary support ticket rather than a reputation event. Bloom House needs an agent that consults and clears the routine questions itself, and hands the rest to a human with the full picture already in hand.

## Who It Is For

- **The buyer in the chat:** a Malaysian gift sender (roughly 25–45, Klang Valley / Penang / Johor Bahru) who knows the occasion but not the bouquet, is time-pressed, unsure of normal spend, and anxious about an emotional moment. Often shops on a phone, after hours.
- **The person who buys the tool:** the owner or a small support team of an online florist doing roughly 300–1,500 orders/month on a Shopify-style store, already running WhatsApp + email support during fixed hours.

## Market Fit Verdict

**Upgrades existing**

Generic store chat tools answer set FAQs and stop. This build adds the two things that make or break a florist sale: florist-grade consultation grounded in the real catalogue (occasion + budget + flower meaning), and an escalation gate tuned to flower-order stakes that hands sensitive cases to a human with a warm, summarized handoff.

## Architecture (confirmed by founder)

**Architecture 2 — AI-First Customer Service.** The AI talks to the customer directly. It resolves what it can safely; anything it cannot goes to a human (the founder).

```
Customer → AI Agent → Can solve? ── Yes → Resolve
                                  └─ No  → Human Agent (founder)
```

- **AI handles:** FAQs, routine requests, simple issues (recommendation, delivery/coverage/care answers, order-status read).
- **Human handles:** exceptions, complaints, sensitive situations (refunds, order changes, upset customers, time-critical failures).

## Knowledge Base (Bloom House)

- **Stores:** Petaling Jaya HQ + retail (Mon–Sun 9 AM–6 PM); KPJ Damansara Specialist Hospital 2 retail (Mon–Sat 9 AM–6 PM, closed Sun/PH).
- **Same-day cut-off:** order by 5 PM (KL / Selangor / Penang / Kedah / N. Sembilan) and 4 PM (Johor) for free same-day delivery.
- **Coverage:** KL, Selangor, Penang, Kedah, Negeri Sembilan, Johor; international to Singapore.
- **Support hours:** Mon–Sun 9 AM–7 PM MYT, via WhatsApp and email.
