# Fire Claim Examiner: Problem Statement

**Date:** 2026-07-29
**App name:** Fire Claim Examiner (locked 2026-07-29 at Step 3)
**Slug:** `fire-claim-examiner`
**Template base:** None. Self-authored build spec at `rag for claim adjuster.html` (v1.0, 12 sections) plus `proposed build.txt`, in place of a Pau AI template.
**Reference quality bar:** Bright Path Tuition
**Project folder:** `Documents\03_Portfolios\AI-Project\rag - fire insurance\` (retained rather than a new `{slug}\` folder, so the policy PDF, claim files and answer key stay together as one corpus)

---

## The Problem

A claims examiner at a Malaysian general insurer opens a fire claim and has to decide three things before touching the payment file: whether the policy responds at all, which clause or endorsement governs, and what the company should actually pay. They work from a 61 page policy document, the customer's schedule and endorsements pulled from an internal system, and their own memory of which endorsement beats which exclusion. The costly part is never finding a clause; it is knowing that a claim can hold exactly the right endorsement and still fail on that endorsement's own conditions, and that a squarely covered peril can still fail on a procedural condition.

What goes wrong is that the reasoning stops at the peril. A burst pipe with the water damage endorsement in place looks payable until someone checks that the shop lot had been empty for 48 days, and a textbook flood looks payable until someone checks the date the written claim arrived. Document assistants such as NotebookLM handle the lookup well and will quote the right clause with a citation, but they rank by similarity rather than by legal authority, so they cannot tell an examiner that an endorsement overrides the base exclusion it sits against, and they cannot compute an excess or apply average item by item to arrive at a figure the examiner can put on a file.

## Who It Is For

- Claims examiner or claims adjuster at a Malaysian general insurer, fire and property portfolio
- Two to five years in the seat, carrying roughly 15 to 30 open claims at any time
- Works from the policy wording, the customer schedule and endorsement list, and an internal claims system
- Decides covered, not covered, or escalate, then calculates a recommended payable
- Has no tool between the raw PDF and a senior colleague's memory
- Not an SME persona: this is regulated insurance work, and the standard SME framing does not apply to a Type C build

## Market Fit Verdict

**Upgrades existing**

Delta: authority precedence over competing clauses, condition testing against the facts of a specific claim, and a deterministic figure at the end. NotebookLM tells an examiner what the policy says; it does not tell them which of two competing clauses governs, whether the circumstances satisfy that clause's own conditions, or what to pay.

## Type and Readiness Fit (Type C, Career Path Builder)

| Metric | FDE wt | LLM wt | Lifetime (Jul-26) | 90-day (Jul-26) |
|---|---|---|---|---|
| 6 RAG Systems | 10 | 9 | 2 | 1 |
| 11 Evaluation | 4 | 8 | 2 | 3 |
| 5 Vector Databases | 4 | 5 | 1 | 0 |
| 12 Production AI | 6 | 9 | 2 | 2 |

The Jul-26 scorecards predate the Catering Knowledge Assistant (28 Jul), so RAG and Vector Databases are already higher than shown in the live 90-day window. The case for this build is not that RAG is untouched; it is that this is a different class of RAG. Catering was retrieval over eleven cooperating documents where the right answer is the most relevant passage. This corpus is layered by design, because endorsements are written to vary base clauses, and similarity ranking alone cannot say which is in force.

## Moat Check (Gate 1: PASS)

| Moat | What the commodity panel cannot do |
|---|---|
| 2. Determinism, no drift | Same governing clause every run. Similarity ranking surfaces Condition 6(b) and FP504 side by side with no concept that FP504 overrides |
| 6. Computed rigor | Excesses that resolve to the lesser of two figures, two different excesses in one claim, and average applied per Schedule item after an exclusion rather than before it |
| 1. Governed boundary | Routing premium, policy number and claim status out to the records system, and refusing where the Schedule is silent |

Guardrail: if the build collapses into sending retrieved chunks to a model and returning its answer, it has failed the gate mid-build. The precedence layer and the deterministic calculator are the build.

## Corpus and Evaluation Set

**Policy corpus (the only document the RAG indexes)**

- Source: `fire policy.pdf` (P/GTS/FIR/01-24/V1), 61 pages, ~247,000 characters
- Base policy Conditions 1 to 25
- Peril endorsements: FP501, FP502, FP503, FP504, FP505A-D, FP506A/B, FP507A/B, FP508A.01, FP508B, FP509, FP510, FP510D, FP511A/B, FP512A/B, FP513, FP514A/B
- Coverage clauses FC8xx and warranties FW7xx
- Note: the v1.0 spec overstates the corpus as a continuous FP501-FP513 range. The actual set is listed above and includes letter-suffixed codes the spec omits.

**Evaluation set**

- Six neutral claim records in `claim case\`, carrying no verdict and no hint
- Ground truth in `answer - claim determination key.html`, which must never be indexed
- Two approved, four declined, each failing for a different reason

| Claim | Loss | Expected | Payable (RM) |
|---|---|---|---|
| CLM-2022-08841 Bukit Mertajam fire | 28 Jul 2022 | Decline, outside policy period | 0 |
| CLM-2023-11207 Taiping burst pipe | 2 Dec 2023 | Decline, FP507B exclusion (a) and Special Condition 3 | 0 |
| CLM-2022-06033 Ipoh windstorm | 30 Jun 2022 | Approve | 49,950 |
| CLM-2021-05512 George Town burglary | 15 Jul 2021 | Decline, before inception, peril not insured, cash excluded | 0 |
| CLM-2023-12440 Kampar flood | 20 Dec 2023 | Decline, Condition 12 breached | 0 |
| CLM-2024-03187 Sungai Petani bakery fire | 14 Sep 2024 | Approve | 130,700 |

**Customer-specific data stays outside the corpus.** Endorsements held, sums insured and schedule terms are inputs supplied per claim, never indexed.

## Evaluation Axes

1. Correct clause retrieved
2. Correct clause ranked first
3. Correct endorsement overrides the base policy
4. Every answer cites its clause
5. Refuses when the policy is silent
6. Routes policy-record questions out to the records system
7. Overall determination correct
8. Recommended payable correct to the ringgit, with a per-item breakdown showing each excess, exclusion and average factor applied
