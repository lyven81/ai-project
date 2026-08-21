# Kuala Sepetang Tour Boat: Problem Statement

**Date:** 2026-08-21
**Template base:** none. This build comes from the Anthropic tool-use course (`Documents/04_Learning/Tool use with Claude/`), not from a Pau AI template.
**Measured against:** `benchmark.html`, 10 weighted criteria
**Reference quality bar:** Bright Path Tuition

---

## What This Is

A **multi-turn AI assistant** for a tour boat operator, not a chatbot with tools attached.

The assistant holds a conversation with either the operator or a customer, keeps context across turns, and orchestrates three complementary tools to complete one workflow end to end:

> understand the request, retain context, retrieve live conditions, search current public information when needed, turn the findings into a useful customer response, communicate uncertainty, and leave the final operational safety decision with the operator.

## The Problem

A tour-boat operator at the Kuala Sepetang jetty in Perak runs one boat and six fixed departures a day, at 09:00, 11:00, 13:00, 15:00, 17:00 and 19:00, each lasting two hours. Bookings arrive by WhatsApp and as walk-ins at the jetty, and the day's list is kept in a notebook or a chat thread. Every morning the operator decides which departures to run by checking a phone weather app and looking at the sky.

With one boat there is no way to recover a bad call: a cancelled departure is a lost fare, and a departure that turns wet at the far end leaves twelve passengers a long way from the jetty and ends in a refund conversation. The phone app reports the day rather than the two-hour window, so it cannot say whether the rain arrives at the start of a trip, when a short delay fixes it, or at the end, when the return leg is the exposed part. It also gives no basis for answering the question that decides whether advance bookings can be taken at all: how many days ahead is a specific slot worth promising.

A customer asking "is 4 PM on Sunday any good?" is asking the same question in a different voice, and today the operator answers it from memory and a glance at the sky.

## Who It Is For

- Single-boat owner-operator at the Kuala Sepetang jetty, Perak
- One hull, roughly 10 to 12 seats
- Six fixed two-hour departures daily: 09:00, 11:00, 13:00, 15:00, 17:00, 19:00
- Bookings by WhatsApp plus walk-ins; day list kept on paper or in chat
- Weekends and school holidays carry the week; the evening firefly run is the reliable earner
- Currently decides go or no-go from a consumer weather app and direct observation

The assistant serves **both sides of that WhatsApp thread**: the operator deciding whether to run, and the customer asking whether to book.

## The Three Tools

| Tool | Who supplies it | What it is for |
|---|---|---|
| **Live Boat Conditions** | Built here | Genuine current and forecast weather and marine data for the tour location: rain, thunderstorms, wind, gusts, visibility. Takes a date and a time, returns the reading for that departure window. |
| **Web Search** | Built in, runs server-side | What the weather tools cannot supply: public holidays, school breaks, official advisories, jetty or road closures, attractions, opening hours, festival dates that drive demand. |
| **Text Edit** | Schema built in, implementation built here | Turning raw findings into clear, customer-friendly replies, recommendations and explanations, and keeping them as a working document the operator does not lose. |

A fourth tool, **current date and time**, is a prerequisite rather than a feature. Lecture note 02 names it as problem one: the model may know the date but not the time, and it does not reckon forward reliably. Without it, "this Sunday" is a guess, and a guessed date is the one error that corrupts every answer built on top of it.

## Boundaries the Outline Draws

- **Weather and marine conditions** answer whether conditions are appropriate for operating. **Tide and water level** answer whether a particular route is navigable. These are different questions, and this build answers the first only.
- **Booking horizon is roughly 7 days.** Longer-range forecasts are stated as less certain rather than quoted as fact.
- **Conditions get checked again** 1 to 2 days before departure, and on the day itself. A booking taken a week out is provisional by construction.
- **The assistant supports the safety decision. It never makes it.** No output states that a departure is safe.

## Data

- **Source:** Open-Meteo Forecast API, free non-commercial tier, no API key
- **Location:** Kuala Sepetang, Perak, approximately 4.84 N 100.63 E (confirm against the jetty rather than the town centre)
- **Timezone:** pinned to `Asia/Kuala_Lumpur`; the API defaults to GMT, and an eight-hour error would move every departure without looking broken
- **Hourly variables:** `precipitation_probability`, `precipitation`, `rain`, `wind_speed_10m`, `wind_gusts_10m`, `cloud_cover`, `visibility`, `weather_code`, `temperature_2m`
- **Daily variables:** `sunrise`, `sunset`, `precipitation_sum`, `wind_gusts_10m_max`
- **Verified present at this location:** `minutely_15`, so a two-hour window carries 8 buckets rather than 2. `visibility` and `cape` both return non-null.
- **Forecast skill by lead time:** measured from the Open-Meteo Historical Forecast API (what was predicted at the time) scored against the Historical Weather API (what actually happened), so the confidence tiers are measured rather than asserted.

## Operator-Owned Configuration

Thresholds belong to the operator, not to the model. They live in one editable config file: gust, rain and probability bands for Good, Marginal and Poor, split open water versus sheltered river.

Starting values are placeholders and are wrong until the operator corrects them. Nothing in that file is a safety standard.

## How Success Is Measured

Ten weighted criteria, scored in `benchmark.html`. The heaviest three:

| # | Criterion | Weight |
|---|---|---|
| 1 | Live data accuracy | 18% |
| 2 | Correct tool selection | 14% |
| 3 | Safety decision support | 14% |
| 4 | Multi-turn context | 12% |
| 5 | Booking forecast usefulness | 10% |
| 6 | Tool integration | 9% |
| 7 | Customer response quality | 7% |
| 8 | Failure handling | 6% |
| 9 | Operator usefulness | 6% |
| 10 | Speed and usability | 4% |

Bands: 90 to 100 production-quality prototype; 75 to 89 strong working prototype; 60 to 74 functional proof of concept; below 60 technical demo.

**A build is not measured by whether all three tools execute.** That part is easy. The benchmark is whether this conversation completes:

> "A family of five wants a mangrove tour this Sunday around 4 PM. Is that a good time? What should I tell them?"

understanding the request, retaining context, retrieving live conditions, searching when necessary, turning the findings into a useful customer response, communicating uncertainty, and leaving the safety call with the operator.

## Requirements That Are Easy To Get Wrong

Four requirements carry more weight than their size suggests. Each one is cheap to build and expensive to omit.

| Requirement | Why it matters | Criteria |
|---|---|---|
| **The assistant knows today's date, and says it.** A current date and time tool, plus today's date and weekday in the system prompt. | "This Sunday" is a calculation, not a recall. A date reckoned from training data is right often enough to look fine and wrong often enough to be dangerous. | 1, 4 |
| **A past date never returns as a forecast.** The forecast layer refuses a date already gone, or labels the payload as history in a way the reply must repeat. | Archive data reads exactly like forecast data. A silent fallback turns a wrong date into a confident, plausible, wrong answer with nothing to reveal it. | 1, 8 |
| **The text editor is aimed at the customer reply.** "What should I tell them?" returns a sendable message by default, not an internal note. | The outline defines this tool as being for customer-friendly replies, recommendations and explanations. A schedule file is a different product. | 7 |
| **The tool count stays near four.** Live conditions, web search, text edit, date and time. | Every additional tool that also touches weather is another chance for the model to pick the wrong one, and tool selection carries 14 points. | 2 |

## Out of Scope

Each of these answers a real question, but not one the outline asks:

- **Seat allocation and reallocation.** Which passengers move to which departure, party splits, refunds. The outline never mentions bookings, seats or refunds.
- **Combined-trip phase scoring.** Rating one departure as two halves with separate thresholds.
- **Moon illumination and the twelve-activity fit table.** Cloud thickness and moonlight describe how pretty an evening is. Neither decides whether a boat sails.

- **Tide.** Matters for the wildlife trips. Open-Meteo does not carry it, and approximating it would be worse than omitting it.
- **Radar nowcasting.** Open-Meteo current conditions are model output, not radar. The operator's own eyes beat it for a shower already visible.
- **Marine wave forecasts.** Deferred, pending a check on whether they are localised enough for the actual river and estuary routes.
- **Sighting probability.** The system rates operating conditions. Dolphins and eagles depend on tide, season and luck.

## Positioning

Decision support for tour scheduling. The system reports conditions against the operator's own thresholds and never says a departure is safe. The operator on the water owns the go or no-go call.
