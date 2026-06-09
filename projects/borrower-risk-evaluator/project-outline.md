# Borrower Risk Evaluator

## What We Are Building

A browser-based classification system that sorts real loan borrowers into default / no-default with a confidence score, routes them auto-approve / auto-flag / send-to-human, and proves its accuracy live against the known repayment outcomes. A BYO-key Gemini classifier plus a measured evaluation scorecard.

## Who It Is For

Credit / risk officer at a small lender (cooperative, microfinance arm, or licensed credit company), 2 to 8 people, a few hundred to a few thousand applications a month, working in spreadsheets with no in-house data science. Also serves as a portfolio piece demonstrating evaluation rigour.

## Domain

Lending / credit-risk classification, with a portfolio focus on AI evaluation (measuring model output against ground truth).

## The Problem

A credit officer can't carefully review every application, so they either rush (and approve defaults that cost real money) or over-review (and waste days on safe applicants), with no defensible way to state how accurate their triage is. The market sells black-box credit scores never measured on the lender's own book, or heavyweight ML platforms with no per-record human-in-the-loop workflow. The missing piece, which this build adds, is a QC scorecard that proves accuracy against the known outcomes.

## Core Features

1. Evaluation scorecard vs ground truth (the headline): accuracy, precision, recall, F1, confusion matrix, accuracy-at-high-confidence, each with a 95% confidence interval.
2. Per-borrower triage verdict from a BYO-key Gemini classifier: typed {status, confidence, reason}.
3. Tunable safety dial: confidence-threshold slider re-splits auto-pass / escalate and redraws the accuracy-vs-coverage tradeoff live.
4. Plain-language "why" + decision trace per borrower, plus a tick/cross showing whether each verdict matched the real outcome.
5. Triage summary headline: "X% auto-cleared = X% less manual review", with a by-loan-type breakdown.
6. Portfolio-to-production guide: how the demo scales to a 10k+ system.

## What Makes It Different

It proves its accuracy on the lender's own labelled history and lets the officer dial the auto-pass threshold while watching precision, recall, and manual-review volume trade off in real time. Measured triage, not a black-box score. It closes the founder's biggest AI-engineering gap: evaluation rigour. Improves on the Bookshelf reference, whose Judge reports a confidence that is never checked against any ground truth.

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| AI Model | Google Gemini (gemini-2.5-flash), BYO-key, structured JSON output | Bookshelf's typed-verdict brain; measurable, miscalibration is the point of the eval |
| Frontend | Single self-contained HTML + vanilla JS + inline SVG charts | Runs on GitHub Pages and file://, no build step |
| Backend | None | Classification runs client-side against the user's key |
| Database | None; real borrowers shipped as data/borrowers.js (script src, no fetch/CORS) | Self-contained, works offline and on Pages |
| Deployment | GitHub Pages via lyven81/ai-project | Portfolio target |
| Build tool (offline, keyless) | Python + pandas (prep_data.py) | Cleans dataset.csv, samples 150 real borrowers into the JS asset |

## Screens and User Flow

1. Evaluation scorecard: run panel (key + sample size + run), then accuracy/precision/recall/F1 with CIs, confusion matrix, baseline note, tradeoff chart.
2. Triage console: by-loan-type breakdown, summary band, three lanes (auto-approve / auto-flag / review queue) with per-borrower cards.
3. Portfolio to production: what transfers, what changes, the eval-on-a-sample insight, a production architecture.

Flow: `paste key -> run evaluation -> scorecard populates -> drag safety dial -> watch tradeoff -> open triage -> work the review queue`

## UI Style

Desktop-first tabbed dashboard, navy/gold, Space Grotesk + Inter + JetBrains Mono. Sober and chart-led, suited to a credit officer who needs a calm, auditable surface.

## Demo Scenario

Mei Ling, a credit officer at a 5-person lender, has a batch of applications. She runs the evaluation, sees 78% auto-cleared, distrusts it, opens the scorecard and finds 94% accuracy on the cleared pile, drags the safety dial stricter to lift recall on real defaults, then works only the uncertain review queue. She has a scorecard to show her boss why the auto-cleared pile is safe.
