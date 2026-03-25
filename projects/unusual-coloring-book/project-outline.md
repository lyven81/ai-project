# Project Outline — Unusual Coloring Book

## Concept
- A web app that takes universally known public domain fairy tales and generates alternative coloring books
- Two narrative modes per story: Perspective Shift (another character's inner world) and What If (one decision changed)
- Each coloring book is 6 illustrated pages with story text and an interactive coloring canvas
- Output is both browser-interactive and exportable as a printable PDF

---

## App Name
**Unusual Coloring Book**
Tagline: *The coloring book for the other side of the story.*

---

## Design Direction
- Bright, cheerful color scheme: sunshine yellow, coral orange, sky blue, mint green, soft pink, lavender
- Playful typography — rounded, friendly fonts
- Card-based layout — each story is a colorful card
- Illustrations in clean outline/coloring-book style (no filled color — user does the coloring)

---

## Problem It Solves
- Standard AI coloring books generate generic disconnected images with no narrative depth
- Children's story apps generate text but no visual or coloring activity
- Existing personalised book products are static templates, not AI-generated narratives
- No product combines perspective-shifting storytelling with a coloring experience

---

## Target Audience
- Primary: Parents of children aged 5–10 wanting creative, educational screen time
- Secondary: Homeschool parents needing curriculum-aligned story activities on demand
- Secondary: Teachers using storytelling for empathy and critical thinking lessons
- Tertiary: Gift buyers wanting a personalised printable keepsake

---

## Demo Content — 10 Books

### 5 Source Stories (all public domain)
1. Snow White (Brothers Grimm)
2. Little Red Riding Hood (Charles Perrault / Brothers Grimm)
3. Cinderella (Charles Perrault)
4. The Ugly Duckling (Hans Christian Andersen)
5. The Tortoise and the Hare (Aesop)

### 10 Generated Books (5 stories × 2 modes)

| # | Story | Mode | Reframe |
|---|---|---|---|
| 1 | Snow White | Perspective Shift | The Evil Queen's inner world |
| 2 | Snow White | What If | Snow White refuses the apple |
| 3 | Little Red Riding Hood | Perspective Shift | The Wolf's backstory |
| 4 | Little Red Riding Hood | What If | Red Riding Hood knew all along |
| 5 | Cinderella | Perspective Shift | The Stepsisters' shame |
| 6 | Cinderella | What If | Cinderella left before midnight on purpose |
| 7 | The Ugly Duckling | Perspective Shift | The bully duck's fear |
| 8 | The Ugly Duckling | What If | Never finds the swans — still finds belonging |
| 9 | The Tortoise and the Hare | Perspective Shift | The Hare's exhaustion |
| 10 | The Tortoise and the Hare | What If | The Tortoise waits — they finish together |

---

## Core Features
- Story selector: 5 fairy tale cards with one-sentence summaries
- Mode selector: Perspective Shift or What If buttons per story
- Character/branch picker: choose which character's lens or which decision changes
- AI generation pipeline: character sheet → 6-page story arc → 6 illustrations (all via Gemini 3)
- Image editing: user can request illustration adjustments before coloring ("make the wolf less scary")
- Interactive coloring canvas: flood-fill, 16-colour bright palette, undo, clear, page navigation
- PDF export: print-ready layout, one illustration + story text per page
- Cover page: auto-generated title + cover illustration
- Physical print upsell: order a bound book via print-on-demand (Printful/Lulu)

---

## Generation Pipeline (Gemini 3 — Single Model)

### MiroFish-Inspired Character Engine
- Load original fairy tale text as input
- Extract characters: name, personality, motivation, fear, relationship to others
- For Perspective Shift: simulate the story events from chosen character's inner state
- For What If: alter one decision point, re-run simulation to produce branched outcome
- Output: character sheet + alternative narrative premise

### deer-flow-Inspired Story Pipeline
- Stage 1 — Structure agent: 6-page story arc (setup, conflict, climax, resolution)
- Stage 2 — Scene writer agent: 2–3 sentences of age-appropriate prose per page with dialogue
- Stage 3 — Image prompt agent: coloring-book style prompt per scene (clean outlines, minimal fill)
- Stage 4 — Consistency checker: cross-checks character names, appearance, setting across all 6 pages
- Memory layer: character traits and world rules injected into every agent call

### Image Generation + Editing (Gemini 3)
- 6 illustrations generated in parallel (one per page)
- Cover illustration generated separately
- User can request edits via text before coloring begins
- Same model context = better story-illustration coherence

---

## Speed Strategy
- Demo (10 fixed combinations): pre-generated and stored server-side, loads instantly
- Generation animation shown (3–5 seconds) to preserve the "wow" moment
- Live product: story text streams first (~10 seconds), images load in parallel (~15 seconds)
- Skeleton placeholders per page while images load
- Progress trail shown: "Building characters → Writing story → Creating illustrations"

---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | React + TypeScript |
| Backend | Python (FastAPI) |
| Single AI model | Gemini 3 (text + image generation + image editing) |
| Character engine | MiroFish-inspired (Python, in-memory) |
| Pipeline orchestration | deer-flow-inspired (Python multi-step agent chain) |
| Coloring canvas | Flood-fill algorithm (in-browser JavaScript) |
| PDF export | jsPDF (client-side, no external API) |

---

## APIs

| API | Purpose | When Needed |
|---|---|---|
| Gemini 3 | All text + image generation + image editing | Demo + production |
| jsPDF | PDF export (library, not API) | Demo + production |
| Stripe | Subscription and one-time payments | Production only |
| Printful or Lulu Direct | Print-on-demand physical book | Production only |

### API Cost Estimate (per book generated)
- Gemini 3 text calls (~8 calls per book): ~$0.02–0.05
- Gemini 3 image generation (6 images per book): ~$0.12–0.18
- Total per book: ~$0.15–0.23

---

## Coloring Experience

### Digital (in-browser)
- Flood-fill: click any area to fill with chosen colour
- 16-colour bright cheerful palette
- Undo, clear, page navigation buttons
- Works with mouse or touch screen (tablet-friendly)

### Physical (print)
- Export PDF: print at home on any printer
- Order physical book: Printful/Lulu ships a bound printed book
- Child colors with real crayons or markers

---

## Monetisation

| Tier | Price | What You Get |
|---|---|---|
| Free | $0 | 1 book per story, watermarked PDF |
| Monthly | $9.99/month | Unlimited books, all stories, clean PDF export |
| Physical book | $24.99 per book | Printed and bound, shipped to door |
| B2B license | Custom | School curriculum providers, publishers |

---

## IP & Content Safety
- All 5 source stories are fully public domain (Brothers Grimm, Hans Christian Andersen, Aesop)
- All generated text and illustrations are original — no reproduction of Disney or modern adaptations
- Gemini 3 prompts explicitly exclude branded visual styles
- Child-safe content enforced at prompt level (age-appropriate themes, no violence)

---

## Build Sequence
1. Character engine (MiroFish-inspired) — Python, test with Snow White in isolation
2. Story pipeline (deer-flow-inspired) — 4 agents in sequence, all Gemini 3 calls
3. Consistency checker — cross-page validation before image generation
4. Image generation — Gemini 3, coloring-book outline style, 6 parallel calls
5. Image editing — Gemini 3 edit endpoint, text-based adjustment before coloring
6. React frontend — story selector, mode picker, page viewer, coloring canvas
7. PDF export — print-ready layout, gates the paid feature
8. Cover page generator — auto title + cover illustration
9. Pre-generate all 10 demo books and store server-side
10. Polish UI — bright cheerful color scheme, animations, progress trail

---

## Reference Repos (Inspiration, Not Direct Copy)
- **MiroFish** (`C:\Users\Lenovo\Documents\Github files\MiroFish-main`) — character extraction and social simulation pattern
- **deer-flow** (`C:\Users\Lenovo\Documents\Github files\deer-flow-main`) — multi-agent orchestration and memory layer pattern
