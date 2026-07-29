# Fire Claim Examiner

## What We Are Building

A tool that reads a lodged fire claim against the policy wording and returns a determination, the clause that governs it, and the recommended amount to pay, with the working shown.

## Who It Is For

A claims examiner or claims adjuster at a Malaysian general insurer, fire and property portfolio. Two to five years in the seat, carrying roughly 15 to 30 open claims at a time. They work from the policy wording, the customer schedule and endorsement list, and an internal claims system, and they decide covered, not covered, or escalate, then calculate a recommended payable.

## Domain

General insurance, fire and property claims adjudication, Malaysia.

## The Problem

A claims examiner at a Malaysian general insurer opens a fire claim and has to decide three things before touching the payment file: whether the policy responds at all, which clause or endorsement governs, and what the company should actually pay. They work from a 61 page policy document, the customer's schedule and endorsements pulled from an internal system, and their own memory of which endorsement beats which exclusion. The costly part is never finding a clause; it is knowing that a claim can hold exactly the right endorsement and still fail on that endorsement's own conditions, and that a squarely covered peril can still fail on a procedural condition.

What goes wrong is that the reasoning stops at the peril. A burst pipe with the water damage endorsement in place looks payable until someone checks that the shop lot had been empty for 48 days, and a textbook flood looks payable until someone checks the date the written claim arrived. Document assistants such as NotebookLM handle the lookup well and will quote the right clause with a citation, but they rank by similarity rather than by legal authority, so they cannot tell an examiner that an endorsement overrides the base exclusion it sits against, and they cannot compute an excess or apply average item by item to arrive at a figure the examiner can put on a file.

## Core Features

1. **Claim adjudication** (AI). Takes a claim record plus the endorsement list and returns covered, not covered, or escalate, with the governing clause and the reasoning chain.
2. **Authority-ranked retrieval** (standard logic over AI retrieval). Ranks retrieved clauses by legal precedence, override beats primary beats secondary, not by similarity score.
3. **Deterministic payable calculator** (standard). Computes the recommended amount item by item: exclusions first, then average per Schedule item, then the applicable excess, with printed working.
4. **Condition testing** (AI). Tests the claim circumstance against the governing clause's own conditions and the base policy conditions: period, occupancy, notice, interest, average.
5. **Evaluation harness** (standard). Runs all six claims against the answer key and scores the eight axes separately.

## What Makes It Different

Every alternative tells an examiner what the policy says; this tells them which of two contradicting clauses governs, whether the facts of this claim satisfy that clause's own conditions, and what to pay, to the ringgit, with the working shown.

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| AI model | Gemini 2.5 Flash primary (BYO key), Claude as second provider behind one interface | LLM APIs is FDE Crit 9 and explicitly multi-provider; never build single-provider |
| Embeddings and rerank | Sentence-transformers embeddings, cross-encoder reranker | Clause-level retrieval needs rerank; similarity alone surfaces the wrong authority |
| Vector database | Qdrant with metadata filtering | A real vector DB is required for depth 3 on metrics 5 and 6; the sql.js governed pattern does not score |
| Backend | FastAPI | Required, and a deliberate departure from the static default. Qdrant, the reranker and the calculator cannot run in the browser, and Production AI (metric 12, LLM weight 9) is a target |
| Calculator | Plain Python, no model in the path | Determinism is the moat. A figure an examiner puts on a file cannot come from a token sampler |
| Deployment | GCP Cloud Run, containerised | Type C default stack; advances Production AI and Build Portfolio |

## Screens and User Flow

**Claim Desk.** Lists the six claims and accepts a pasted record. Shows the parsed claim as a structured card: policy period, loss date, endorsements held, sums insured by item, items claimed. The examiner confirms or corrects the endorsement list before running.

**Determination.** The verdict banner, the governing clause with its quoted text, the reasoning chain as numbered steps, and the payable breakdown table showing each item, the clause applied, the exclusion or average factor, and the running total.

**Under the Hood.** For the question just asked: the chunks retrieved, their authority levels, which one won and why it outranked the others, the reranker scores, and the retrieval time.

**Evaluation.** All six claims scored against the key across the eight axes, with the two payables shown as expected against actual.

```
[Claim Desk] → select claim, confirm endorsements → [Determination]
     → open any step → [Under the Hood] → back
     → run full set → [Evaluation]
```

## UI Style

Desktop-first, dense and document-like, closer to a case file than a chat window: an examiner works at a desk with the policy and the claim open side by side, needs the clause text visible next to the verdict rather than scrolled away in a conversation, and has to be able to copy a reasoning chain and a payable breakdown straight onto a file.

## Demo Scenario

Aida is a claims examiner at a general insurer in Alor Setar. A bakery fire file lands on her desk: Sungai Petani, RM 168,200 claimed, and the customer system shows one endorsement she has not dealt with before, FP508A.01.

1. She opens Claim Desk, picks CLM-2024-03187, and confirms the endorsement list pulled from the customer record.
2. The tool checks the policy period first and clears it, then identifies fire as attaching under the base insuring clause with no endorsement required, and flags that FP508A.01 is engaged by the cause.
3. On the Determination screen the verdict is covered, and the payable breakdown splits the claim three ways. The spiral dough mixer is struck out at RM 18,500, with FP508A.01 quoted. The oven and proofer stay in, and the tool shows her the proviso in the same clause that keeps them in.
4. Condition 20 is applied to Item 2 alone at 0.75, because the valuation puts contents at RM 200,000 against a RM 150,000 sum insured. Items 1 and 3 are left whole. Recommended payable: RM 130,700, with the RM 37,500 reduction reconciled as RM 18,500 excluded plus RM 19,000 average.
5. She opens Under the Hood to see why FP508A.01 outranked FP508B in the retrieval, copies the breakdown onto the file, and moves to the payment authority.

## Evaluation Set and Ground Truth

Six neutral claim records in `claim case\`, no verdict and no hint. Ground truth in `answer - claim determination key.html`, which must never be indexed.

| Claim | Loss | Expected | Payable (RM) |
|---|---|---|---|
| CLM-2022-08841 Bukit Mertajam fire | 28 Jul 2022 | Decline, outside policy period | 0 |
| CLM-2023-11207 Taiping burst pipe | 2 Dec 2023 | Decline, FP507B exclusion (a) and Special Condition 3 | 0 |
| CLM-2022-06033 Ipoh windstorm | 30 Jun 2022 | Approve | 49,950 |
| CLM-2021-05512 George Town burglary | 15 Jul 2021 | Decline, before inception, peril not insured, cash excluded | 0 |
| CLM-2023-12440 Kampar flood | 20 Dec 2023 | Decline, Condition 12 breached | 0 |
| CLM-2024-03187 Sungai Petani bakery fire | 14 Sep 2024 | Approve | 130,700 |

## Eval Gate (before any UI)

| Axis | Target |
|---|---|
| Determination correct | 6 of 6 |
| Governing clause ranked first | 5 of 6 minimum |
| Recommended payable exact to the ringgit | 2 of 2 |
| Every answer carries a clause citation | 100% |
| Refuses where the policy is silent | 100% of probes |
| Routes record questions out | 100% of probes |
