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

## Why it is not plain RAG

An insurance corpus contradicts itself by design: an endorsement exists to
displace the clause it is written against. Similarity ranking returns the
exclusion and the extension side by side, both maximally relevant, with no notion
that one governs the other. The precedence layer is the point, and the calculator
never has a model in its path.
