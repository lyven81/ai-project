# Power BI Report Pages — Lead Source Intelligence

Five pages, matching the five tabs of the live web dashboard (`ui-1`) one-to-one. Each page lists its visuals, the measures behind them, and the planted insight it is built to surface. A single global slicer panel (Month range, Source, Segment, Listing) sits on every page via a synced slicer.

Palette: navy `#1E3A5F`, mid-blue `#4A7FB5`, soft `#EAF1F8`; green `#2F7D5C` / amber `#B07A2A` / red `#A8453A` for verdicts. Fonts: Fraunces (titles), Manrope (body) — or Segoe UI if Fraunces is unavailable on the client machine.

---

## Page 1 — Overview
**Question it answers:** is the portfolio healthy this month, and where are tenancies coming from?

| Visual | Type | Measures / fields |
|---|---|---|
| KPI cards (5) | Card | `Total Enquiries`, `Qualified Enquiries` + `Qualified Rate`, `Viewings Booked`, `Tenancies Signed`, `Cost per Tenancy` (portfolio avg) |
| Monthly enquiries by source | Stacked column | Axis `DateDim[MonthName]`, legend `SourceDim[source_label]`, value `Total Enquiries` |
| Tenancy wins | Table | `Listings[property_name]`, `Listings[signed_source]`, `Listings[signed_date]`, filtered to `Tenancies Signed > 0` |
| Restock flag | Card / text | `Restock Warning` |

**Surfaces:** insight #8 (portfolio sell-through). The stacked column visibly steps down Feb→May (299→64) as listings sign; the restock card fires the warning before the pipeline empties.

---

## Page 2 — Source comparison
**Question it answers:** which channel is worth the money?

| Visual | Type | Measures / fields |
|---|---|---|
| Cost-per-tenancy matrix (headline) | Matrix | Rows `SourceDim[source_label]`; values `Total Enquiries`, `Qualified Rate`, `Enquiry to Viewing Rate`, `Cost per Enquiry`, `Cost per Viewing Booked`, `Tenancies Signed`, `Cost per Tenancy (label)` |
| Volume vs quality | Clustered column | Axis `SourceDim[source_label]`; columns: share of enquiries % and `Qualified Rate` |
| Verdict cards | Card + conditional format | `Cost per Tenancy`; green ≤ RM1,400, blue ≤ RM2,000, amber ≤ RM2,500, red/undefined otherwise |

**Surfaces:** insights #1 (Mudah inversion — top volume, RM cost-per-tenancy "Undefined"), #2 (Google pays off — highest CPE, second-cheapest tenancy), #3 (Referral champion — RM0). The matrix is the page everyone remembers.

---

## Page 3 — Listing performance
**Question it answers:** which listings are moving, and which are stuck?

| Visual | Type | Measures / fields |
|---|---|---|
| Portfolio health | Table | `Listings[property_name]`, `segment`, `asking_rent_myr`, `Total Enquiries`, `Qualified Enquiries`, `Viewings Booked`, `Days on Market`, `Stale Flag` |
| The stale signal | Line | Axis `Enquiries[WeekOfLife]`; value `Total Enquiries`; two lines: L09 Sunway Velocity Two (RM3,400) vs L05 Nexus whole unit (RM2,999) |
| Velocity read | Card | `Early Velocity`, `Recent Velocity`, `Velocity Drop %` for the selected listing |

**Surfaces:** insight #4 (the stale listing) and #7 (the star — L07 Lavile, 23 days on market, the healthy benchmark). The line chart shows L09 collapsing ~70% after week 2 while L05 keeps moving.

---

## Page 4 — Lead quality
**Question it answers:** what is actually wrong with the leads we are paying for?

| Visual | Type | Measures / fields |
|---|---|---|
| Outcome distribution | Doughnut | Legend `Enquiries[outcome]`, value `Total Enquiries` (1,140) |
| Funnel by source | Bar + data bars | `SourceDim[source_label]`, `Qualified Rate`, `Enquiry to Viewing Rate` |
| Mismatch hotspot | Text + card | `Total Enquiries` filtered to `Listings[gender_rule] = "female"` and `source = "mudah"` and `outcome = "requirement_mismatch"` |

**Surfaces:** insight #6 (channel × segment) via the funnel-by-source bars, and the planted J.Dupion female-room mismatch (≈28% of its Mudah traffic) via the hotspot card. Shows that cheap volume is mostly no-reply / lowball / mismatch.

---

## Page 5 — Responsiveness
**Question it answers:** how much money are we losing by not replying fast enough?

| Visual | Type | Measures / fields |
|---|---|---|
| KPI cards (5) | Card | `Median Response Time — Office`, `After-Hours Share`, `Unanswered Rate — Office`, `Unanswered Rate — After Hours`, `Paid Leads Lost (RM)` |
| The after-hours leak | Clustered column | Axis: office hours vs after hours; value `Unanswered Rate`; red on the after-hours bar |
| Response-time distribution | Histogram (or binned column) | `Enquiries[first_response_min]` bucketed, split by `after_hours` |

**Surfaces:** insight #5 (the after-hours leak — 20.2% vs 6.8%, roughly 3×, about RM700 of paid leads lost). The recommendation (a WhatsApp auto-acknowledgement holding the lead overnight at zero cost) is placed as a text box beside the leak chart.

---

## Cross-page elements
- **Slicer panel** (synced across all pages): `DateDim[MonthName]` range, `SourceDim[source_label]`, `Listings[segment]`, `Listings[property_name]`.
- **Tooltips:** a report-page tooltip on the source visuals showing `Cost per Enquiry`, `Cost per Qualified Enquiry`, `Cost per Viewing Booked` together.
- **Insight notes:** each page carries a short text box with the plain-language finding, mirroring the panel notes in the web dashboard. These are the same sentences the monthly insight engine (`insights/`) generates, so the dashboard and the written report never disagree.
