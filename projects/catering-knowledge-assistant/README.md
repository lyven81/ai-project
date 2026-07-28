# Catering Knowledge Assistant

A retrieval pipeline over a real document corpus: ingest, chunk, embed, store,
retrieve, rerank, cite. Answers are grounded in the source documents and carry
citations, and questions that the documents cannot answer are refused rather
than guessed.

The domain is a weekday meal delivery service, 好吃厨房 Tasty Kitchen, operating
in Shah Alam and Kota Kemuning. The menus are real, transcribed from four
weekly menu sheets. The business identity and contact details are fictional.

## Architecture

```
corpus/*.md ──> chunker ──> gemini-embedding-001 ──> Qdrant collection
                                                          │
question ──> router ──┬──> vector search (payload filters)─┘
                      │           │
                      │           ▼
                      │    cross-encoder rerank
                      │           │
                      │           ▼
                      │    relevance floor ──> authority precedence
                      │           │
                      │           ▼
                      │    gemini-2.5-flash-lite ──> answer + doc_id citations
                      │
                      └──> governed SQLite tools ──> gemini-2.5-flash-lite ──> answer
```

Two answer paths, chosen by a router:

- **Corpus path** for knowledge questions (policies, menus, terms, dietary
  scope). Dense retrieval over the document corpus.
- **Tool path** for record questions (a subscriber's balance, a cycle end date,
  tomorrow's cooking count). These are arithmetic over structured data, which
  vector similarity answers badly, so they run against fixed parameterised
  SQL instead.

## Stack

| Stage | Choice |
|---|---|
| Embeddings | `gemini-embedding-001`, 768 dimensions via MRL truncation, L2 normalised |
| Vector store | Qdrant, server mode when available, local embedded otherwise |
| Retrieval | Cosine top-12, optional payload filters on `doc_type`, `category`, `authority`, `doc_id` |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2`, local, CPU, no API cost |
| Ranking rule | Authority precedence above a relevance floor, override > primary > secondary |
| Generation | `gemini-2.5-flash-lite` |
| Routing | `gemini-2.5-flash-lite` with a constrained JSON schema |

`text-embedding-004`, named in the original outline, is no longer served on the
Gemini API and was replaced with `gemini-embedding-001`.

Generation runs on `gemini-2.5-flash-lite`. Measured on 28 July 2026, the free
tier caps **both** `flash` and `flash-lite` at 20 `generate_content` requests
per day, per model. The 48 question end to end set costs two calls each (route
plus generate), so 96 calls against a 20/day ceiling: it cannot be scored in a
single day without paid quota. `rag.evaluate end2end` therefore resumes from
saved results and tops them up across days, and marks any incomplete set
`partial` so it can never be read as a finished run. Pointing `ROUTER_MODEL` at
a different model doubles the daily throughput, since the cap is per model.

## The corpus

Eleven documents, 128 chunks. Every document carries frontmatter metadata
(`doc_id`, `doc_type`, `category`, `authority`, dates) that survives into the
vector store payload.

| Document | Type | Authority |
|---|---|---|
| `menu_week_1` to `menu_week_4` | menu | primary |
| `addons_and_soups` | menu | primary |
| `delivery_policy` | policy | primary |
| `subscription_guide` | policy | primary |
| `payment_and_refund_policy` | policy | primary |
| `business_info` | reference | primary |
| `holiday_notice_2026` | notice | **override** |
| `faq` | faq | **secondary** |

Chunking is per document type, because one strategy does not fit all of it:

- **Menus**: one chunk per meal, each repeating its own date, day, service and
  both prices. A fixed-window splitter would orphan a dish from its date and
  make the answer uncitable.
- **FAQ**: one chunk per question and answer pair. Most answers close with an
  explicit pointer to the document that binds ("See delivery_policy."), which is
  lifted out of the prose into a `restates` field on the chunk. 35 of the 47 FAQ
  chunks name a binding parent, and that pointer is what lets the retriever pull
  the policy in beside the restatement instead of inferring the relationship.
- **Policies and notices**: one chunk per section, the natural unit of a rule.

## Deliberate hard cases

The corpus was written to contain retrieval problems that a keyword lookup or a
single-stage retriever gets wrong.

1. **Authority conflict.** The FAQ restates the policies and is tagged
   `secondary`. Grounding an answer on it instead of the binding policy is a
   real correctness risk.
2. **Override.** `holiday_notice_2026` contradicts the standing delivery
   schedule for two dates. Answering "do you deliver on 31 August" correctly
   requires the notice to outrank the general policy.
3. **Plan-conditional pricing.** The same Thursday claypot chicken is RM18 for
   a daily customer and RM15 for a monthly subscriber. There is no single
   correct price.
4. **Grounded refusals.** No halal certification, no beef, no vegetarian plan,
   no delivery outside two areas. Each needs a cited no, not an improvised one.

## Results

Retrieval evaluation over 37 labelled corpus questions, 23 of them tagged with
a required authoritative source:

| Metric | Vector only | + reranker | + authority precedence |
|---|---|---|---|
| Hit rate @4 | 100.0% | 100.0% | 100.0% |
| Precision @4 | 95.9% | 90.5% | 87.2% |
| MRR | 0.986 | 0.973 | 0.973 |
| Authority precedence @1 | 13.0% | 13.0% | **100.0%** |

Recall over the 12 candidate pool is 100%, so every gold document reaches the
reranker and no failure is a recall failure. Precedence fixes 20 questions and
breaks none.

**The finding that drove the design.** A plain cross-encoder put the FAQ first
on 20 of the 23 authority-sensitive questions. FAQ chunks are short and
question-shaped, so they match query phrasing more closely than the policy that
actually binds.

The first fix added a constant to the rerank score for higher-authority chunks.
That reached 69.6% and then stalled, and the reason is structural rather than a
matter of tuning: cross-encoder scores are unbounded, spanning roughly -11 to
+10, so any fixed bonus loses to a large enough margin. The sweep was asymptotic
(13.0% at no bonus, 43.5%, 69.6%, 82.6%), which is the signature of the wrong
mechanism. A bonus large enough to guarantee precedence would have stopped being
a prior and become a hard filter.

So authority became an **ordering rule instead of a score**. Among chunks that
clear a relevance floor, ranking is by authority first and similarity second;
below the floor, similarity alone. Nothing is discarded, which matters: a hard
filter that kept only the override would answer "do you deliver on 3 September"
from a holiday notice that says nothing about that date, having thrown away the
standing policy. Two changes complete it:

- **The relevance floor** replaces both bonus constants with one interpretable
  number, swept to 2.0. Unlike the bonus it has a real optimum, because the two
  failure modes sit on opposite sides. Too low and a weakly matching override
  outranks the policy that answers; too high and the rule stops firing.
- **Binding-parent promotion** uses the `restates` pointer the FAQ already
  carries. When a restatement outranks its parent so decisively that the parent
  never reaches the pool at all ("Is there a weekly plan?" retrieves three FAQ
  chunks and no `subscription_guide`), the parent is fetched by `doc_id` and
  placed above it.

Precision and MRR both improve under the new rule rather than degrading, because
ordering by authority no longer costs the gold FAQ its place in the context.

**Caveat on the floor.** 100% is reached at a single swept value with 95.7% on
either side, over 23 labelled questions, so the exact floor is fitted to this
set. The shape of the curve is the durable result, not the decimal.

### Counter-test: precedence must reorder, not evict

Demoting the FAQ must not push it out of the context, because it carries the
plain-language phrasing that makes an answer readable. The originally intended
counter-test, questions where the FAQ is the correct rank-1 source, has no
instance in this corpus: the FAQ restates a policy on every question and is
never a sole gold document. Retention is the version this corpus supports.

**Gold FAQ retained in context: 94.4% (34 of 36).** Both exceptions are the
holiday-override questions ("Do you deliver on 31 August 2026?", "Are you open
on Malaysia Day?"), where the notice supplies seven chunks and fills the final
four. That is the correct outcome rather than a regression: on those two
questions the general FAQ schedule is precisely the answer that must not be
given. The test is kept as a live check because the failure it guards against,
a precedence rule that empties the context instead of reordering it, would not
show up in hit rate or precedence.

### End to end evaluation: measured, not yet complete

`rag/evaluate.py` scores six things the retrieval metrics cannot see: route
accuracy, tool selection, citation accuracy, answer correctness, forbidden
content, and refusal correctness. Two notes on its honesty:

- **Refusal is scored in both directions.** It was previously checked only on
  questions expected to refuse, which made over-refusal invisible: an assistant
  that refused all 48 would have scored 100%. Refusing an answerable question
  loses an order and answering an unanswerable one gives a customer wrong
  information, so the two are counted and reported separately.
- **The set is not yet fully scored.** At 96 calls against the free tier's
  20/day per model, it accumulates over several days. `eval_results.json` marks
  an incomplete sweep `partial` with the count actually scored, so the numbers
  are never presentable as more than they are. Until it completes, this project
  reports retrieval and drift results and makes no end to end claim.

### Drift test: what the authority rule is actually worth

Authority precedence is a ranking statistic, and on a clean corpus a wrong
ranking often still produces a right answer, because the FAQ and the policy
agree. That makes the metric hard to justify on its own.

`rag/drift.py` creates the disagreement deliberately. Four FAQ entries that
restate a policy are rewritten to contradict it, embedded into a throwaway
collection, and asked back. The corpus on disk is never modified.

| | Binding document ranked first |
|---|---|
| No authority rule | 0 / 4 |
| Authority precedence | **4 / 4** |

Without the rule every one of the four answers from the stale FAQ: a 9:00pm
cut-off instead of 5:00pm, refunds offered where the policy refuses them, cash
accepted where the policy is bank transfer only, and delivery promised to an
area outside the service coverage. This is the failure the tag exists to
prevent, and it is why precedence is measured separately from answer
correctness: today the FAQ agrees with the policy, and the point of the rule is
that it keeps working on the day it stops.

## The operational database

`tasty_kitchen.db` holds 60 customers, 20 monthly subscription cycles and 570
delivered meal lines, generated deterministically by `build_database.py`.

Monthly cycles are 20 weekday meals from each subscriber's own start date, and
a public holiday inside a cycle extends it by one service day rather than
consuming a meal. With staggered starts and two holidays in the window, the 20
subscriptions end on 14 different dates, so "when does my cycle end" has no
single answer.

The tools exposed to the model are fixed parameterised queries. The model picks
a tool and supplies arguments; it never writes SQL, never sees the schema and
cannot list tables or dump records.

## Running it

```bash
pip install google-genai qdrant-client python-frontmatter sentence-transformers

# GEMINI_API_KEY in the environment or in ~/.env

python build_database.py        # build the operational database
python -m rag.chunker           # corpus -> chunks.json
python -m rag.index             # embed and build the Qdrant collection
python -m rag.retriever         # retrieval demo, shows rerank effects
python -m rag.tools             # database tool demo
python -m rag.assistant         # end to end question demo
python -m rag.evaluate all      # retrieval and end to end evaluation
python -m rag.drift --baseline  # drift test, with and without the authority rule
```

Optional, for a real Qdrant server with working payload indexes:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

The pipeline detects the server automatically and falls back to local embedded
mode when it is not running.

Embeddings are cached in `.embed_cache.json`, so re-running the index costs no
API quota. Both the embedding and generation calls are rate limited per model
to stay inside the Gemini free tier.

## Files

| Path | Purpose |
|---|---|
| `corpus/` | 11 source documents with frontmatter metadata |
| `rag/chunker.py` | Ingest and chunk, per document type |
| `rag/index.py` | Embed and build the Qdrant collection |
| `rag/retriever.py` | Vector search, payload filters, rerank, authority prior |
| `rag/tools.py` | Governed fixed-query database tools |
| `rag/assistant.py` | Router, grounded generation, citations, refusal |
| `rag/evaluate.py` | Retrieval and end to end evaluation |
| `rag/eval_set.json` | 48 labelled questions |
| `rag/drift.py` | Drift test: does the policy still win when the FAQ goes stale |
| `rag/drift_set.json` | 4 FAQ entries rewritten to contradict their policy |
| `rag/sweep_floor.py` | Sweeps the relevance floor that sets the operating point |
| `build_database.py` | Deterministic operational database generator |

© 2026
