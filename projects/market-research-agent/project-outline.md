# Market Research Agent — Project Outline

**Status:** Approved scope, pre-build
**Date:** 2026-06-06
**Career-review bucket:** 🔵 Asset (portfolio showcase + Upwork demo). Not a productized platform under current strategy.
**Location:** `Documents/03_Portfolios/AI-Project/market-research agent`

---

## 1. Concept

A market research agent that helps a local, consumer-facing business owner answer the questions they actually ask before opening a shop, expanding, or launching a product. It is modelled on Google's "Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps" codelab, with three deliberate changes:

1. **Minus ADK.** The codelab uses Google's Agent Development Kit. We rebuild the same design with raw model function-calling (or a light framework), so it is not tied to ADK and can run anywhere.
2. **Predefined (governed) queries.** Following the klinik dr fang pattern, the agent never writes free-form SQL. It picks from an approved set of parameterized query-tools. Safer, cheaper, predictable.
3. **Cached Maps.** Google Maps is called only on a scheduled refresh and the results are stored as local tables. Every user question is then answered from the cache, so Maps is not billed per request.

### Design lineage
| Source | What we take |
|---|---|
| Codelab (Location Intelligence ADK agent) | The two-source design (data + maps), the 4 data tables, the question themes |
| klinik dr fang / `ai-agent-mcp-build` | Governed predefined-query pattern, agent picks approved tools, never writes SQL |

---

## 2. Architecture

```
Browser UI
   │
   ▼
Backend (Cloud Run, pay-per-use, scales to zero)
   │
   ├── Router: cheap model (Gemini Flash / Claude Haiku) maps the user's
   │   wording to ONE approved predefined query-tool, then phrases the answer
   │
   ├── Query layer: 10 predefined, parameterized SQL tools (no free-form SQL)
   │
   └── Data store: SQLite / Postgres
         ├── 4 data tables  (the business "data pack")
         └── 3 cached-Maps tables (refreshed on a schedule, not per request)

Scheduled refresh job  ──>  Google Maps API  ──>  fills the 3 cached tables
```

### Cost design (the whole point)
- **6 of 10 questions are pure SQL** on local tables: near-zero marginal cost.
- **4 of 10 questions read cached-Maps tables:** free per query; Maps is billed only on the scheduled refresh.
- **No live drive-time / Routes call** is in the approved 10 (the single most expensive call was deliberately excluded).
- **One cheap-model call per turn** to route + phrase. Tiny token count because the tool list is small and data is pre-fetched.
- **Recurring spend = scheduled refresh of 2 cached tables** (competitor places + reviews) + cheap-model tokens. About as low as possible while still feeling like a live agent.

---

## 3. Data model (7 tables)

### 3a. Data pack — the 4 codelab tables (swap rows per business)
Real columns, taken from the codelab repo (`google/mcp`, `examples/launchmybakery/data`).

| Table | Columns | Grain |
|---|---|---|
| `demographics` | `zip_code, city, neighborhood, total_population, median_age, bachelors_degree_pct, foot_traffic_index` (+ optional `chinese_population_pct` for the tong shui pack) | one row per area |
| `foot_traffic` | `zip_code, time_of_day, foot_traffic_score` | area × daypart (morning/afternoon/evening) |
| `competitor_prices` | `store_name, product_type, price, region, is_organic` | competitor × product (region-level) |
| `sales_history_weekly` | `week_start_date, store_location, product_type, quantity_sold, total_revenue` | store × product × week |

> Note on data gaps: `demographics` has no income or household-size column (use `bachelors_degree_pct`, `median_age`, `total_population` as the customer-profile proxies). `competitor_prices` is region-level, so price cannot be sliced by area.

### 3b. Cached-Maps tables (filled from Google Maps on a schedule)
| Table | Columns | Filled by |
|---|---|---|
| `competitors` | `name, business_type, zip_code, lat, lng, rating, review_count` | Maps Places search |
| `competitor_reviews` | `competitor_id, rating, review_text, theme` | Maps Places reviews |
| `suppliers` | `name, zip_code, lat, lng` | Maps Places search *(reserved for future logistics questions; not used by the approved 10)* |

---

## 4. The 10 approved research questions

Generic templates with `[business]`, `[product]`, `[area]` slots. Selected for real owner relevance, full decision-journey coverage, and lowest cost.

| # | Question (generic) | Stage | Table(s) | Cost |
|---|---|---|---|---|
| 1 | Which area has the highest foot traffic for `[business]`, and at what daypart? | Where | `foot_traffic` | SQL ~0 |
| 2 | Which area's resident profile best fits my target customer? | Who | `demographics` | SQL ~0 |
| 3 | Which areas have strong foot traffic but few existing `[business]`? | Where + Competition | `foot_traffic` + `competitors` | Cached |
| 4 | How many `[business]` already operate in `[area]`? Is it saturated? | Competition | `competitors` | Cached |
| 5 | What price range (low/avg/high) do competitors charge for `[product]`? | Price | `competitor_prices` | SQL ~0 |
| 6 | Is there a price point no competitor occupies for `[product]`? | Price | `competitor_prices` | SQL ~0 |
| 7 | What revenue can I expect from `[product]` in `[period]`? | Economics | `sales_history_weekly` | SQL ~0 |
| 8 | Which `[product]` sells best, and which is growing or declining? | Demand | `sales_history_weekly` | SQL ~0 |
| 9 | What do customers complain about most in competing `[business]`? | Differentiation | `competitor_reviews` | Cached |
| 10 | Should I launch `[product]` in `[area]`? | Go / No-go | multiple | Cached |

> These map to the original 20-question numbering as: 1, 2, 3, 4, 8, 9, 11, 12, 15, 20.

### Deliberately excluded (and why)
| Excluded | Reason |
|---|---|
| Supplier / catchment drive time | Highest cost (live Maps Routes). Add later with a one-time precomputed distance, not live calls. |
| Complementary placement, competitor density | Overlap with #3/#4; need extra cached categories for marginal value. |
| Top-rated competitors | Already served by #9's review insight. |
| Proposed-price-vs-range, seasonality, review praise/underserved | Near-duplicates of the chosen price, demand, and review questions. |

---

## 5. Universality across businesses

The 7-table schema and the 10 queries are **identical for every local consumer-facing business** (nasi lemak, chicken rice, contact lens shop, stationery shop, etc.). Only the **data pack** changes. Two business-specific parameters per pack:

| Parameter | Examples |
|---|---|
| Competitor search keyword (`business_type`) | "nasi lemak", "chicken rice", "optician", "stationery shop" |
| Product list (`product_type`) | nasi lemak / rendang ; chicken rice / roast ; daily lenses / solution ; notebooks / pens |

**Boundary:** the review question (#9) depends on competitors having Google reviews. Strong for F&B and consumer retail; thin for B2B or online-only. The target segment is local, consumer-facing businesses with a physical presence.

---

## 6. First build target

- **Business:** Tong shui shop (Chinese sweet dessert soup)
- **Market:** Klang Valley, Chinese-dense supper areas (e.g. SS2 Petaling Jaya, Cheras, Kepong, Setapak, Pudu, Old Klang Road)
- **Daypart emphasis:** evening / night (supper culture), so question #1 is expected to peak in the evening, not morning
- **Products (`product_type`):** cheng tng, tau fu fa, bubur cha cha, red bean soup, green bean soup, black glutinous rice, leng chee kang, mango pomelo sago, sea coconut, ginger sweet potato soup
- **Competitor keyword (`business_type`):** "tong shui", "tong sui", "Chinese dessert", "dessert shop"
- **Optional column:** `chinese_population_pct` added to `demographics` to sharpen questions #2 and #3 for this use case
- **Goal:** Demonstrate all 10 questions answering end to end against a realistic Klang Valley tong shui data pack, at near-zero marginal cost.

---

## 7. Tech stack

| Layer | Choice |
|---|---|
| Backend | Cloud Run (pay-per-use, scales to zero) |
| Data store | SQLite (single committed file) or Postgres |
| Query layer | 10 predefined, parameterized SQL tools |
| Router / phrasing model | Gemini Flash or Claude Haiku (cheap tier) |
| Maps | Google Maps Places API, called only by the scheduled refresh job |
| Refresh | Scheduled job (Cloud Scheduler / cron) populating `competitors` + `competitor_reviews` |
| Frontend | Lightweight chat UI (suggested prompts for the 10 questions + free-text routing) |

---

## 8. Build phases

1. **Schema + sample data pack.** Create the 7 tables; generate a realistic Malaysian nasi lemak data pack (4 data tables) and a small cached-Maps snapshot.
2. **Query layer.** Write the exact predefined SQL for all 10 questions (note any that join cached + data tables).
3. **Maps refresh job.** Script the Places search + reviews pull that fills `competitors` and `competitor_reviews`; field-mask to minimize cost.
4. **Router.** Cheap-model intent routing from user wording to one approved tool, plus answer phrasing. Deterministic keyword fallback for the 10 known questions to skip the model where possible.
5. **Backend + UI.** Cloud Run service, chat UI with the 10 suggested prompts and refusal for out-of-scope asks.
6. **Demo + portfolio writeup.** End-to-end run on the nasi lemak pack; package as an Upwork / portfolio showcase.

---

## 9. Open decisions (for later)

- SQLite vs Postgres for the data store.
- Refresh cadence (daily vs weekly) for the 2 cached Maps tables.
- Whether to add the logistics/drive-time questions back with a precomputed distance matrix.
- Which router model (Gemini Flash vs Claude Haiku) on final cost test.

---

## 10. Writing-style note

All written output for this project (UI copy, portfolio writeup, README) follows the global rule: **no em-dashes**; use commas, colons, semicolons, parentheses, or full stops.
