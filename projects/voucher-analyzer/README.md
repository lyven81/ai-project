# Voucher Analyzer

Promotion incrementality / uplift analysis for a small SEA e-commerce seller. It separates the sales a voucher truly caused from buyers who would have purchased anyway, then scores each voucher and recommends a per-category plan.

## What it does
* Estimates incrementality blind to the ground truth (a baseline-counterfactual), then validates that estimate against a baked-in truth. The recovery check lands at about 45% incremental versus a true 46% (the naive gross-sales read would say 100%).
* Scores every voucher on net P&L, ROI and subsidy share, and maps a category x voucher margin matrix.
* Answers the ten questions sellers ask most, plus four live read-only SQL drill-downs run client-side via sql.js (governed and keyless).

## Run it
Open `demo.html`, or serve the folder with `python -m http.server`. No API key and no server are required.

## Files
* `demo.html`: the app, self-contained (results inlined).
* `voucher-data.js`: redemption records (observable columns only) loaded into sql.js for the live queries.
* `results.json`: the engine's computed outputs that the UI renders.
* `voucher_orders.csv`: the observable order dataset. The hidden incrementality truth column is withheld from this file and never deployed.
* `voucher_issuance.csv`: per-voucher issuance.
* `pipeline.py`: generates the data, runs the incrementality engine and recovery check, and emits `results.json`.
* `build_assistant_data.py`: builds `voucher-data.js` from the orders.

## Governance
The assistant runs fixed, parameterised, read-only SQL client-side (sql.js). It can only pick a track and bind values; it can never write SQL, and the hidden ground-truth column is physically absent from the deployed data.

(c) 2026 Lee Yih Ven | Data-Driven Solutions
