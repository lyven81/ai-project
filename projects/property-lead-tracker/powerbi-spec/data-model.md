# Power BI Data Model — Lead Source Intelligence

**Status:** Reference specification. The live internal dashboard ships as the interactive web build (`ui-1-internal-dashboard.html`), which mirrors these five pages one-to-one. This document records how the same model is built in Power BI, so the data-modeling and DAX layer is fully reproducible for a client who runs on Microsoft BI.

All figures reconcile to the committed dataset (1,140 enquiries, 7 tenancies, RM9,060 spend, Dec 2025 to May 2026).

---

## 1. Source tables (Power Query)

Four CSVs load as-is. Power Query steps are minimal: set data types, then mark the fact and dimension roles.

| Query | Role | Grain | Rows |
|---|---|---|---|
| `Enquiries` | Fact | 1 row per enquiry | 1,140 |
| `Listings` | Dimension | 1 row per listing | 10 |
| `AdSpend` | Fact (cost) | month × campaign × segment | 30 |
| `PlatformCosts` | Fact (cost) | month × platform | 12 |

### Power Query type-setting (Enquiries)
- `datetime` → Date/Time
- `qualified`, `responded`, `after_hours`, `viewing_booked`, `viewing_attended` → True/False (the CSV stores `True`/`False` text; change type to Logical)
- `move_in_days`, `first_response_min` → Decimal Number (`first_response_min` has blanks for unanswered enquiries; keep as null, do not zero-fill, so median measures ignore them)
- `month` → Text (kept as `YYYY-MM` for a clean join to the cost tables)

### Derived columns added in Power Query
- `Listings[listed_date]`, `Listings[signed_date]` → Date
- `Listings[days_on_market]` = `signed_date` (or report-as-of date for active listings) − `listed_date`. Computed as a column because it is a per-listing attribute, not an aggregation.

---

## 2. Helper tables (created in the model)

### `DateDim` (calculated table)
```
DateDim =
ADDCOLUMNS(
    CALENDAR(DATE(2025,12,1), DATE(2026,5,31)),
    "Month",      FORMAT([Date], "YYYY-MM"),
    "MonthName",  FORMAT([Date], "MMM"),
    "MonthSort",  YEAR([Date])*100 + MONTH([Date]),
    "WeekStart",  [Date] - WEEKDAY([Date],2) + 1
)
```
Marked as the model Date table. `MonthName` sorted by `MonthSort` so the axis reads Dec → May.

### `SourceDim` (calculated table)
A clean source dimension so slicers and the cost join are stable:
```
SourceDim =
DATATABLE(
  "source", STRING, "source_label", STRING, "category", STRING,
  {
    {"referral",     "WhatsApp referral", "Referral"},
    {"propertyguru", "PropertyGuru",      "Platform"},
    {"google_ads",   "Google Ads",        "Search ad"},
    {"meta_ads",     "Meta Ads",          "Social ad"},
    {"mudah",        "Mudah.my",          "Platform"}
  }
)
```

### `ListingDaysByMonth` (calculated table — the allocation bridge)
The honest answer to "what did this listing cost to market this month" is an allocation, not a guess. Platform subscriptions are portfolio-level, so they are spread across listings by the share of days each listing was live that month.
```
ListingDaysByMonth =
VAR MonthsList = DISTINCT(DateDim[Month])
RETURN
GENERATE(
    Listings,
    VAR lst = Listings[listed_date]
    VAR sgn = COALESCE(Listings[signed_date], DATE(2026,5,31))
    RETURN
    ADDCOLUMNS(
        FILTER(MonthsList, TRUE()),
        "DaysListed",
            VAR mStart = DATE( VALUE(LEFT([Month],4)), VALUE(RIGHT([Month],2)), 1 )
            VAR mEnd   = EOMONTH(mStart, 0)
            VAR ovStart = MAX(mStart, lst)
            VAR ovEnd   = MIN(mEnd, sgn)
            RETURN MAX(0, DATEDIFF(ovStart, ovEnd, DAY) + 1)
    )
)
```
This yields `listing_id × month × days_listed`. A listing live the whole of a 31-day month contributes 31; a listing signed mid-month contributes only the days before signing.

---

## 3. Relationships (star schema)

```
                    ┌──────────────┐
                    │   DateDim    │  (Date, Month, MonthName, WeekStart)
                    └──────┬───────┘
                           │ 1   (Date → Enquiries[datetime] date part)
                           │  *
      ┌──────────────┐    ┌▼──────────────┐    ┌──────────────┐
      │  Listings    │1  *│   Enquiries   │* 1 │  SourceDim   │
      │ (listing dim)├────┤    (FACT)     ├────┤ (source dim) │
      └──────┬───────┘    └───────────────┘    └──────┬───────┘
             │ 1                                       │ 1
             │ *                                       │ *
      ┌──────▼────────────┐                    ┌───────▼──────┐
      │ ListingDaysByMonth│                    │ PlatformCosts│ (month, source, cost)
      │  (alloc. bridge)  │                    │   AdSpend    │ (month, source, seg, spend)
      └───────────────────┘                    └──────────────┘
```

| From | To | Cardinality | Direction | Active |
|---|---|---|---|---|
| `Listings[listing_id]` | `Enquiries[listing_id]` | 1 : * | Single | Yes |
| `SourceDim[source]` | `Enquiries[source]` | 1 : * | Single | Yes |
| `DateDim[Date]` | `Enquiries[datetime]` (date) | 1 : * | Single | Yes |
| `SourceDim[source]` | `PlatformCosts[source]` | 1 : * | Single | Yes |
| `SourceDim[source]` | `AdSpend[source]` | 1 : * | Single | Yes |
| `DateDim[Month]` | `PlatformCosts[month]` | 1 : * | Single | Yes |
| `DateDim[Month]` | `AdSpend[month]` | 1 : * | Single | Yes |
| `Listings[listing_id]` | `ListingDaysByMonth[listing_id]` | 1 : * | Single | Yes |
| `DateDim[Month]` | `ListingDaysByMonth[Month]` | 1 : * | Single | Yes |

Notes:
- Costs join to the model through `SourceDim` + `DateDim[Month]`, not directly to the fact, so a source-level cost is never double-counted across the many enquiry rows.
- `ListingDaysByMonth` is the only path that pushes a portfolio-level cost down to a single listing; it is used by the per-listing cost measures and by the owner report.
- Keep all relationships single-direction. The few cross-filter needs (cost-in-the-context-of-a-source) are handled in the measures with `CALCULATE`, which is more predictable than bi-directional filtering.

---

## 4. Cost allocation logic (stated openly)

| Cost type | Source | Monthly amount | Allocation rule |
|---|---|---|---|
| Subscription | PropertyGuru | RM450 | Spread across active listings by `days_listed` share that month |
| Subscription | Mudah.my | RM60 | Spread across active listings by `days_listed` share that month |
| Campaign | Google Ads | RM600 (3 campaigns) | Attributed to listings whose `segment` matches `target_segment`, by `days_listed` share within that segment |
| Campaign | Meta Ads | RM400 (2 campaigns) | Attributed to listings whose `segment` matches `target_segment`, by `days_listed` share within that segment |
| Referral | WhatsApp referral | RM0 | No media cost; goodwill cost noted but excluded |

Two levels of cost exist deliberately:
- **Source-level cost** (used for the headline cost-per-tenancy table) — the simple, unarguable total per channel.
- **Listing-level allocated cost** (used for listing performance and owner reports) — requires the bridge above and is always labelled as an allocation.

---

## 5. Reconciliation targets

The model is correct when these tie out:

| Check | Expected |
|---|---|
| Total enquiries | 1,140 |
| Total qualified | 359 (31.5%) |
| Viewings booked / attended | 192 / 149 |
| Tenancies signed | 7 |
| Total spend (6 mo) | RM9,060 |
| Cost per tenancy: Referral / PG / Google / Meta / Mudah | RM0 / RM1,350 / RM1,800 / RM2,400 / undefined |
| Unanswered rate office vs after-hours | 6.8% vs 20.2% |
| Monthly enquiry volume Dec→May | 202 / 292 / 299 / 172 / 111 / 64 |

See `measures.dax` for every measure and `pages.md` for the five-page layout.
