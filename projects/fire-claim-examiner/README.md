# Fire Claim Examiner

Reads a lodged fire insurance claim against the policy wording and returns three
things: whether the policy responds, which clause governs, and what to pay, with
the working shown.

**Open `demo.html`** in any browser. It is self-contained: no server, no key, no
install.

## What is here

```
demo.html            the app, built on frozen gate-proven results
engine/              parser, calculator, adjudicator, retrieval
eval/                the two scoring harnesses
data/                policy chunks, clause library, held-out answer key
claim case/          six neutral claim records, no verdict and no hint
answer-key.html      the answer key, readable
```

## On the answer key

"Held out" means the **deciding code path never opens it**. Only `eval/run_eval.py`
and `build/freeze_results.py` read it; the adjudicator, calculator, parser and
retriever do not. It is published so the scores can be checked rather than taken
on trust.

## Reproducing the scores

The chunker needs the source policy PDF, which is a third-party document and is
not redistributed here. `data/chunks.json` is the built output, so the engine and
both harnesses run without it.

```bash
python eval/run_eval.py             # outcomes 6/6, figures 2/2 exact
python eval/run_retrieval_eval.py   # retrieval 4/4, overrides 2/2 both ways
```

The retrieval harness needs `qdrant-client` and `sentence-transformers`.

## How it decides

A policy is layered: a base wording, and the endorsements on the customer's
schedule that vary it. Retrieval indexes the policy as clause-level passages
carrying their authority, peril and excess formula, and a precedence stage
orders what it finds by which clause takes priority for that customer.

Six checks then run in a fixed order and the engine reports the first one that
stops the claim. The amount is computed by the calculator, which has no model
anywhere in its path.
