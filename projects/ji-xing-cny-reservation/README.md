# Ji Xing 吉星饭厅 — CNY 2026 Reservation Demo

[![WebMCP](https://img.shields.io/badge/WebMCP-W3C%20spec-CBA135)](https://github.com/webmachinelearning/webmcp)
[![Status](https://img.shields.io/badge/Status-Demo-2D7A3E)](#)
[![Browser](https://img.shields.io/badge/Chrome-146%2B-403B36)](#)

A WebMCP-powered **Chinese New Year reunion dinner reservation page** for a fictional Malaysian Cantonese banquet restaurant. Demonstrates the W3C WebMCP standard (`navigator.modelContext`) in a real-world reservation domain — agents can search menus, check availability, reserve tables, and manage bookings via typed tool calls, all from inside the user's browser session.

**Reference implementation:** Sunny Car Accessories ([../sunny-car-accessories/](../sunny-car-accessories/)) — same single-HTML SPA pattern, adapted for restaurant reservations.

---

## What This Is

A single self-contained `index.html` (~2,300 lines, ~120 KB) that delivers:

- **6 CNY set menus** (RM 688 – RM 1,288) with full bilingual course lists, dietary options, and auspicious meanings
- **9-day reservation grid** for CNY 2026 (14–22 Feb), with 4 sittings per normal day and 2 dinner-only sittings on Reunion Eve & Day 1
- **480 bookable slots** allocated across 6/8/10-pax tables and 4 private rooms (with first-come-first-serve policy)
- **7 typed WebMCP tools** registered per-view via `navigator.modelContext.provideContext()`
- **Floating Inspector Panel** (bottom-right, 4 tabs: Tools / Try as Agent / Log / Source) for live introspection of the WebMCP layer
- **`requestUserInteraction()` confirmation flow** for all destructive actions (reserve, modify, cancel) with a custom-modal fallback for browsers without native WebMCP
- **localStorage persistence** for last booking lookup
- **Schema.org JSON-LD** (Restaurant + ReserveAction + FAQPage) for rich SERP snippets
- **Bilingual content** (English + 中文) for dual-keyword search capture
- **Mobile responsive** (1024px → 768px breakpoints, full-width Inspector drawer on phones)
- **Browser compatibility mode** — Inspector Panel shows ⚠️ banner on browsers without `navigator.modelContext`; human UI works fully on all modern browsers

No backend, no build step, no real payment processing. Everything runs client-side on GitHub Pages.

---

## Try It

### As a Human

1. Open `https://lyven81.github.io/ai-project/projects/ji-xing-cny-reservation/` in any modern browser
2. Browse the 6 CNY set menus
3. Click any menu card → see full course list + dietary options
4. Click **Reserve** → pick a date and sitting → fill customer info → confirm
5. Get your booking reference (`JX-CNY26-XXXXX`)
6. Use **Manage Booking** to look up, modify, or cancel — try `JX-CNY26-DEMO1` to test without booking first

### As an AI Agent

1. Install [Auto Browser](https://autobrowser.dev) (the first WebMCP-aware agent)
2. Open the demo URL
3. Try one of these prompts:

> *"Find me a CNY reunion dinner at Ji Xing for 10 people, no pork, around RM 1,500 budget."*

> *"Book Ji Xing for Reunion Eve dinner, 6 pax, vegetarian, private room if available."*

> *"Look up booking JX-CNY26-DEMO1 and change the dietary preference to vegetarian."*

4. Watch the **Inspector Panel** show the tool calls fire in real time

### Verify WebMCP is Real (Console)

Open DevTools and paste:

```js
'modelContext' in navigator                                              // → true (Chrome 146+)
navigator.modelContext.tools.length                                      // → 2-3 (changes per view)
navigator.modelContext.tools.find(t => t.name === 'checkAvailability')  // → full tool object
await navigator.modelContext.tools.find(t => t.name === 'searchSetMenus').execute({pax:10})
// → returns 2 sets (10-pax A and B)
```

---

## Why It Matters

### The 5 business values for Malaysian Chinese restaurant operators

1. **Get found by AI shopping agents** — "next-generation SEO." Customers asking ChatGPT, Gemini, Perplexity, and Auto Browser to *do* the booking, not just search. Agent-ready sites win the agent traffic; non-agent-ready sites are invisible to it.
2. **Higher conversion when agents book on customer's behalf** — pixel-clicking agents abandon carts when forms break or A/B tests change. WebMCP agents call `reserveTable({...})` directly and reliably.
3. **Free 24/7 customer support deflection** — `getSetMenuDetails`, `checkAvailability`, `getReservation` answer pre-sale and post-sale questions without staff time.
4. **A "public API" at frontend-developer cost** — most Malaysian SMEs can't justify gateway/OAuth/docs/versioning. WebMCP delivers 80% of API value at 10% of the cost.
5. **Measurable agent-traffic analytics** — `submitEvent.agentInvoked` flags agent vs human actions. Agent traffic stops being invisible.

### Why CNY-specific (not a full restaurant website)

A festival-bound reservation page concentrates 95% of the page on bookable actions, every WebMCP tool registration earns its place, and the typed-contract advantage is maximally visible. A full restaurant site dilutes WebMCP density to ~30% (mostly static content). Same template can be reused annually — bump the dates forward, swap menus, repeat.

---

## How It Works

### Per-view tool scoping

Each of the 5 views registers ONLY the tools relevant to that page's context. The agent's tool surface is intentionally small (2–3 tools at a time, not all 7 at once):

| View | Tools registered | Why |
|---|---|---|
| Home | `searchSetMenus`, `getSetMenuDetails` | Discovery only — no booking commitments from homepage |
| Set Detail | `getSetMenuDetails`, `checkAvailability` | Detail browsing + availability check |
| Booking | `checkAvailability`, `reserveTable` | Final destination for the destructive action |
| Confirmation | `getReservation` | Read-only follow-up |
| Manage | `getReservation`, `modifyReservation`, `cancelReservation` | Lifecycle management — destructive actions live ONLY here |

This is the "per-page scoping" feature WebMCP is designed for. An agent on the home page **cannot** trigger `reserveTable` — that tool simply doesn't exist in their tool surface until they're on the Booking view.

### The 7 typed tools

| # | Tool | Purpose |
|---|---|---|
| 1 | `searchSetMenus` | Filter the 6-set catalog by pax / dietary / max price |
| 2 | `getSetMenuDetails` | Full course list, dietary options, auspicious notes for one set |
| 3 | `checkAvailability` 🔑 | **Killer tool** — table inventory by date/sitting/partySize, broken down by table type |
| 4 | `reserveTable` | Create a confirmed reservation. Gated by `requestUserInteraction()` |
| 5 | `getReservation` | Look up a reservation by reference. Read-only |
| 6 | `modifyReservation` | Change dietary or special requests. Gated by `requestUserInteraction()` |
| 7 | `cancelReservation` | Cancel reservation. Subject to cancellation policy. Gated by `requestUserInteraction()` |

### Token efficiency vs pixel-clicking

Per the WebMCP spec ([§20 of the deck](https://github.com/webmachinelearning/webmcp)):

| Approach | Tokens per booking flow |
|---|---|
| Pixel-clicking agent (screenshot + DOM tree) | ~2,000–5,000 per page |
| WebMCP typed tool calls | ~20–100 per call |
| **Reduction** | **~89%** |

A full booking flow (search → details → check availability → reserve) on this page = **4 tool calls = ~120–400 tokens** vs **~8,000–20,000 tokens** for pixel-clicking the same flow.

---

## Browser Support

| Browser | WebMCP | Booking UI |
|---|---|---|
| **Chrome 146+** | ✅ Full — `navigator.modelContext` live, all 7 tools agent-callable | ✅ Works |
| Edge 147 (flag-gated) | ⚠️ With flag | ✅ Works |
| Firefox / Safari | 🟡 Compat mode — Inspector shows ⚠️ banner | ✅ Works (no agent layer) |

The booking flow works for human visitors on every modern browser. WebMCP is purely additive — it adds the agent layer without changing the human experience.

---

## Restaurant Operating Model (Mock Data)

| Field | Value |
|---|---|
| Capacity | 30 tables (9 × 6-pax + 10 × 8-pax + 7 × 10-pax + 4 private rooms) |
| Booking-vs-walk-in split | 15 / 15 per sitting (50/50 mid-tier MY pattern) |
| Sittings | Lunch 11:30am · Lunch 1:30pm · Dinner 6:00pm · Dinner 8:30pm |
| Peak day rule | Reunion Eve (16 Feb) & Day 1 (17 Feb) = dinner only |
| Lead time | 24 hours minimum |
| Cancellation | Free ≥48hrs · 50% forfeit <48hrs · full forfeit on no-show |
| Deposit | 50% at booking |
| Booking ref format | `JX-CNY26-XXXXX` |
| Halal status | Non-halal · No-pork option on every set |
| Private room rule | Available with surcharge for all sets EXCEPT 10-pax Set B (VIP Room bundled) |

For the full restaurant operating spec, see [`restaurant outline.md`](./restaurant outline.md).

For the full app architecture, see [`app outline.md`](./app outline.md).

---

## File Structure

```
ji-xing-cny-reservation/
├── index.html                  # The whole app — HTML + CSS + JS + WebMCP layer
├── README.md                   # This file
├── restaurant outline.md       # Restaurant operating decisions (capacity, slots, menu, policies)
├── app outline.md              # App architecture spec (views, tools, mock data, build sequence)
├── menu/                       # Per-set menu detail (.md files for reference)
│   ├── 6-pax-set-a-menu.md
│   ├── 6-pax-set-b-menu.md
│   ├── 8-pax-set-a-menu.md
│   ├── 8-pax-set-b-menu.md
│   ├── 10-pax-set-a-menu.md
│   └── 10-pax-set-b-menu.md
└── images/
    ├── logo.jpeg               # 吉 brand mark
    ├── hero.jpeg               # CNY banquet hero banner
    └── menus/                  # 6 set-menu hero images (1024×1024, AI-generated)
        ├── 6-pax-set-a.jpeg
        ├── 6-pax-set-b.jpeg
        ├── 8-pax-set-a.jpeg
        ├── 8-pax-set-b.jpeg
        ├── 10-pax-set-a.jpeg
        └── 10-pax-set-b.jpeg
```

---

## Built With

- **WebMCP** — W3C spec, `navigator.modelContext` API
- **Vanilla HTML5 / CSS / JS** — no framework, no build step
- **Google Fonts** — Poppins (English) + Noto Sans SC (Chinese)
- **Schema.org JSON-LD** — Restaurant, ReserveAction, FAQPage types
- **GitHub Pages** — static hosting
- **AI-generated imagery** — Imagen 3 (Google AI Studio) for hero, logo, and 6 menu photos

No external runtime dependencies. No backend, no database, no payment processing — fully client-side. Mock data persists in `localStorage` for the user's last booking lookup.

---

## What's NOT Included (Deliberately)

- ❌ Real backend / server / API — every interaction is client-side
- ❌ Real payment processing — checkout is mocked with deposit confirmation
- ❌ Real-time inventory sync — mock data baseline; production tier upsell
- ❌ User accounts / login — anonymous booking only
- ❌ Multi-language UI toggle — course names are bilingual inline; full translation is a Pau AI Standard tier upsell
- ❌ Lion dance / yee sang upgrade / tea ceremony / bird's nest add-on bookings — mentioned in menus, handled in person, not in WebMCP tool surface
- ❌ Customer reviews / testimonials — would dilute the WebMCP demo

These are out of scope for the template demo. A real merchant deployment would extend the architecture for any of the above as a custom Pau AI Standard or Custom tier engagement.

---

## Reusability — The Booking Template Pattern

This app's structure is a canonical reservation-template pattern. The same 5-view SPA + 7-tool WebMCP layer + Inspector Panel can be cloned for:

- 💇 Salon booking (haircut + colour appointment)
- 🦷 Dental clinic appointment booking
- 💪 Gym class booking
- 🛠️ Workshop slot booking (e.g., car servicing)
- 🏥 Medical clinic appointment booking
- 💆 Spa / massage booking

What changes:
- **Catalog** (set menus → service packages)
- **Inventory unit** (tables → service slots, sized by duration / staff / room)
- **Slot rule** (4 sittings × 9 days → domain-specific schedule)
- **Killer tool schema** (`checkAvailability` parameters domain-specific)

What stays the same:
- 5-view SPA (Home / Detail / Booking / Confirmation / Manage)
- 7-tool WebMCP layer (search / details / availability / reserve / get / modify / cancel)
- Per-view tool scoping via `provideContext()`
- Inspector Panel (4 tabs, floating, Sunny pattern)
- `requestUserInteraction()` gating for destructive actions
- Schema.org structured data
- Brown/gold theme baseline

---

## License & Credits

Demo built by Lee Yih Ven as part of the [lyven81/ai-project](https://github.com/lyven81/ai-project) portfolio.

The Ji Xing 吉星饭厅 brand, address, and content are fictional — created solely for demonstration purposes. Any resemblance to a real restaurant is coincidental.

WebMCP is a W3C draft specification by the [Web Machine Learning Community Group](https://github.com/webmachinelearning/webmcp), led by Google Chrome and Microsoft Edge.

---

*Last updated: 2026-05-03. Demo URL: https://lyven81.github.io/ai-project/projects/ji-xing-cny-reservation/*
