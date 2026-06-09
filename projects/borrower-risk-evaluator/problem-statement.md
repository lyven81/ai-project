# Borrower Risk Evaluator — Problem Statement

**Date:** 2026-06-09
**Template base:** Graft build (not single-template). Sources: Bookshelf (typed verdict + deterministic escalation gate), Hoo Tim (browser-side BYO-key demo shell with visible decision trace), new-by-hand (QC scorecard against a labelled hold-out set).
**Reference quality bar:** Bright Path Tuition

---

## The Problem

A credit officer at a small lender (a 2-to-8 person cooperative, microfinance arm, or licensed credit company) processes a few hundred to a few thousand loan applications a month, today by eyeballing each one in a spreadsheet against a mental checklist. They approve the obvious-good and obvious-bad by gut and spend most of the week stuck on the murky middle. They hold a CSV of past loans with the actual repayment outcome attached, but no way to turn that history into a measured, trustworthy triage rule.

Because they can't carefully review every application, they either rush (and approve defaults that cost real money) or over-review (and waste days on safe applicants), with no defensible way to state how accurate their triage actually is. The market either sells a black-box credit score that is never measured on the lender's own book, or a heavyweight ML platform with no per-record human-in-the-loop workflow; the founder's own past AI builds, like most demos, report a confidence number that is never checked against ground truth. The missing piece, and the thing this build adds, is a QC scorecard that proves accuracy against the known repayment outcomes.

## Who It Is For

- Credit / risk officer at a small Malaysian lender, cooperative, microfinance arm, or licensed credit company
- Volume: a few hundred to a few thousand loan applications a month
- Team size: 2 to 8 people; no in-house data science
- Current tools: Excel / Google Sheets, gut-feel cutoffs, a historical loan export with repayment outcomes
- Fits because the use case hits all five "rigorous classification earns its keep" circumstances: high volume, real cost of error, a rare-but-costly class (defaults), can't fully trust the machine, and an auditor will demand proof

## Market Fit Verdict

**Upgrades existing**

Delta: a QC scorecard measured on the lender's own labelled hold-out set (precision, recall, and accuracy-at-high-confidence), bolted onto a per-record auto-pass / escalate triage with a visible decision trace and a plain-language reason. No reachable solution for this persona combines measured-on-your-own-book accuracy + a tunable escalation dial + a human-in-the-loop workflow.

## Dataset

- Source: `C:\Users\Lenovo\Documents\03_Portfolios\AI-Project\classification and eva\dataset.csv`
- Row count: 32,586 rows × 13 columns (4 unlabelled rows dropped → 32,582 usable)
- Class balance: NO DEFAULT 25,742 (~79%) / DEFAULT 6,840 (~21%) — usefully imbalanced (makes precision/recall the honest metric, not raw accuracy)
- Label column: `Current_loan_status` (DEFAULT / NO DEFAULT) — this is the answer key that makes measured accuracy possible
- Cleaning decisions (from the verified decisions brief):
  - `historical_default` — 64% null → keep null as its own "unknown" category (missing-ness may be signal)
  - `loan_int_rate` — ~10% null → impute median by `loan_grade`
  - `employment_duration` — ~3% null → impute median
  - `Current_loan_status` — 4 null → drop rows (no label = unusable)
  - `customer_id` / `loan_amnt` — 3 / 1 null → drop (trivial)
- Loan types (all 6 kept, none too thin): EDUCATION 6,454, MEDICAL 6,072, VENTURE 5,718, PERSONAL 5,523, DEBTCONSOLIDATION 5,213, HOMEIMPROVEMENT 3,606
- No Malaysian localization remap required (generic lending features)
