# Bright Path Tuition Centre — Project Outline

## What we are building
An AI management assistant for a premium small-class tuition centre that answers natural-language questions about child mastery, specialist quality, and secondary readiness — and proposes 2-line fixes for every gap it finds.

## Who it is for
The **centre manager / owner** of a Malaysian premium small-class tuition centre (max 10 children per class). Not parents, not tutors, not the Treasury department. Pure management view.

## Domain
Education SME — specifically, the **premium end** of the Malaysian primary tuition market, post-UPSR.

## The problem

Malaysia permanently abolished UPSR and PT3. Assessment has shifted to Classroom Assessment (PBD) + UASA, with Year 4 becoming the MOE's new core-subject mastery anchor in 2026. This policy shift has left tuition centres with a problem: the old "drill to pass the big exam" business model is dead, and managers now need to evaluate their centre, their specialist tutors, and every individual child on a much richer set of signals — core mastery, school PBD results, and holistic development dimensions. Spreadsheets cannot keep up, and no off-the-shelf education software is built for the post-UPSR world.

A **premium small-class centre** is uniquely positioned to thrive in this world — small classes make it possible to actually know every child, spot gaps early, and intervene case by case. But the manager needs a tool that matches that positioning. This app is that tool.

## Core features

1. **Natural-language chat** — manager types a question, gets an answer grounded in the live database.
2. **Year 4 anchor report** — who has mastered the core subjects vs who has gaps in the MOE-focus year.
3. **Secondary readiness view (P5 & P6)** — critical-escalation detection for any P5/P6 child whose current score is below their Year 4 baseline.
4. **Specialist quality audit** — compare tutors by improvement, retention, and holistic development outcomes.
5. **Class space availability** — which classes have room for 2–3 more children, which are at the 10-cap.
6. **Gap → 2-line fix recommendations** — every problem surfaced comes with a specific intervention proposal.
7. **PBD dimension tracker** — holistic development signal across 6 dimensions (mastery, critical thinking, participation, discipline, collaboration, creativity).
8. **Centre snapshot** — Monday-morning overview of the whole centre in one view.

## What makes it different

- **Policy-aware.** Every design decision is built around the post-UPSR PBD + UASA reality. Competitors still built for UPSR look obsolete the moment you compare.
- **Level philosophy enforced in the schema.** Year 4 is the anchor year (flagged in every class); P5 and P6 are "build forward, never backward" years with critical-escalation rules built in.
- **Premium small-class DNA.** The 1 : 9 tutor-to-child ratio and 10-child cap are features, not bugs. The app reinforces this in its language ("children" not "students", "specialists" not "tutors").
- **Gap → Fix format.** No dashboard card ends at "here is a problem." Every surfaced gap comes with a 2-line proposed intervention referencing a specific specialist or class.

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| LLM | Gemini 2.0 Flash | Fast, cheap, strong SQL generation |
| Backend | FastAPI | Async, simple, matches the template |
| Database | SQLite (dev) / AlloyDB (prod) | 7 relational tables |
| Frontend | Static HTML + CSS | No build step, served by FastAPI |
| Container | Dockerfile | Standard Cloud Run pattern |
| Deploy | Google Cloud Run | Template already configured for port 8080 |

## Schema and scale

- **7 tables:** students, tutors, classes, enrolments, attendance, assessments, development_notes
- **22 tutors** (2 preschool, 10 P1–P3 subject specialists, 10 P4–P6 subject specialists)
- **63 classes** (3 preschool, 30 P1–P3, 30 P4–P6) — each capped at 10 children
- **185 children** (P4-weighted, reflecting the new MOE anchor)
- **553 enrolments** (children take avg 2.5 subjects)
- **1,423 assessments** (2 monthly test cycles + school PBD captures)
- **370 development notes** (6 PBD dimensions, monthly per child)

## Seeded demo stories (9)

Hard-coded in `seed_generator.py` so the demo is never empty:

1. Year 4 anchor gaps — 5 P4 children, split between two Math specialists for comparison
2. P5 CRITICAL escalation — 2 children who entered P5 with unresolved Year 4 gaps
3. P6 URGENT secondary risk — 1 child with a Year 4 Science gap, 5 months to Form 1
4. P6 secondary-ready celebration — 4 children fully ready across all 5 subjects
5. Top improvers — 5 children who jumped 15+ marks
6. Underperforming specialist — Teacher Zara (P4–P6 English), coaching case
7. PBD divergence — 3 children whose centre tests are strong but school PBD is weak
8. Holistic development concerns — specific children flagged on critical thinking / mastery
9. Class fill-rate variance — natural mix of at-cap, mid, and underfilled classes

## User flow

1. Manager opens the app → sees the centre snapshot quick action.
2. Clicks "Year 4 anchor report" → agent runs SQL, returns list of P4 children at risk + fix recommendations.
3. Asks "which P6 children are not secondary-ready?" → agent returns Aisyah's case with CRITICAL flag and proposed intervention.
4. Asks "compare Teacher Daniel and Teacher Alicia on P4 Math" → agent returns side-by-side improvement stats.
5. Asks "which classes have seats available?" → agent returns fill-rate list.

## Policy context

Ministry of Education has permanently abolished UPSR and Pentaksiran Tingkatan 3 (PT3). Education Minister Fadhlina Sidek confirmed the shift away from high-stakes testing toward holistic education. Assessment is now based on:

- **Pentaksiran Bilik Darjah (PBD)** — ongoing classroom-based assessment
- **Ujian Akhir Sesi Akademik (UASA)** — end-of-session academic test
- **Year 4 core-subject measures** — new assessment framework rolling out in 2026

This app embraces that reality instead of fighting it.

## Out of scope (for v1)

- Payments and invoicing (separate Treasury project)
- Parent portal (future phase — requires auth and per-student scoping)
- Tutor cost / profitability analytics (depends on payments data)
- Mandarin UI (English only, since this is a GitHub portfolio piece)
- Real centre data (all seed data is synthetic and deterministic via `random.seed(42)`)
