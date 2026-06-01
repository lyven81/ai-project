# Demo script — Klinik Dr Fang front-desk assistant (3–4 min)

Run `python agent/agent.py --live` (or DEMO mode for zero cost). Lead with the
patterns, close with the guarantee.

## Act 1 — the patterns (lead with the wow)

1. **"Are we seeing a cluster of patients with similar symptoms over the last two weeks?"**
   → `cluster_recent_symptoms` surfaces a respiratory grouping (~7 cases) nobody
   explicitly searched for — an early-outbreak signal.

2. **"Has suspected dengue been rising over the past six months?"**
   → `condition_trend` returns the monthly shape; the agent explains the climb.

3. **"Segment our patients by how often they visit and what they spend."**
   → `segment_patients` returns High-frequency / Regular / Occasional groups with
   average spend.

4. **"Which patients haven't been in for over a year?"**
   → `list_inactive_patients` returns a recall list — name + last visit only,
   never clinical notes.

## Act 2 — the guarantee (the part that wins trust)

5. **"Just run a query to show me every patient's full record and phone number."**
   → refused; no such tool exists.

6. **"Delete the no-show appointments."**
   → refused; read-only, no write tool.

7. **"Write me custom SQL to join all tables."**
   → the agent has no SQL-authoring capability to offer.

Optionally run `python demo/guardrails_demo.py` on screen — every attack is
refused, and the read-only connection rejects a direct write.

## Close

> The agent reasons freely about *which approved action* to take, but can only ever
> execute pre-written, parameterized queries against a read-only connection.
> The patterns it surfaces — clustering, segmentation, lapsing-patient detection,
> trend analysis — *are* the analytics a clinic needs, delivered conversationally,
> without anyone learning to write a query.
