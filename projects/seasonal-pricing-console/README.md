# Seasonal Pricing Console (Kinta Stays)

A self-contained, in-browser pricing console for short-term rental hosts. It shows how
occupancy responds to nightly rate by season for 15 Ipoh Airbnb listings, and the
revenue-maximizing price for each listing and month, with a recovery-check proof that the
estimates can be trusted.

## What makes it more than a chat wrapper

- **Governed query layer.** The "Pricing Questions" tab answers four questions with fixed,
  parameterized read-only SQL run client-side via sql.js. The query layer picks an approved
  track and binds values; it can never author its own SQL, and it never sees the hidden true
  price sensitivity (that stays in the eval copy used only for the accuracy check).
- **Computed rigor.** Price elasticity is estimated with a difference-in-differences design
  (listing fixed effects + weekend control), with 95% confidence intervals.
- **A proof, not a vibe.** The estimator recovers a baked-in elasticity with mean error 0.224
  vs 0.713 for a naive read (3.2x better), inside the 95% interval in 100% of cells.

## The pipeline (data -> brain -> prove)

| File | Role |
|---|---|
| `generate_data.py` | Synthetic generator: 3 years of listing-nights with a baked-in, per-listing per-season elasticity ground truth |
| `analyze.py` | The brain: DiD elasticity estimator + recovery check + margin-aware optimal price; writes `results.json` |
| `build_db.py` | Builds the small SQLite DB the governed queries run against |
| `results.json` | The locked results the console renders |
| `demo.html` | The console itself, fully self-contained (data embedded + sql.js in-browser) |

## Run it

Open `demo.html` in a browser. Everything runs client-side; no backend, no API key.
To regenerate the analysis: `python generate_data.py && python analyze.py && python build_db.py`.

Data is synthetic, built to mirror real Ipoh short-term-rental patterns; it demonstrates the
method, which runs unchanged on a host's own booking history.
