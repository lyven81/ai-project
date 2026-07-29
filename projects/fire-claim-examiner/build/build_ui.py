"""
Build the self-contained UI (Tree, Layer 4).

Inlines the stylesheet, the frozen results and the script into one index.html
that runs by double-click with no server and no key. The screens are built on
gate-proven numbers, so the interface cannot break a validated answer.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"

CSS = (APP / "static" / "app.css").read_text(encoding="utf-8")
JS = (APP / "static" / "app.js").read_text(encoding="utf-8")
DATA = json.loads((APP / "data" / "frozen_results.json").read_text(encoding="utf-8"))

BODY = """
<div class="app-container">

  <div class="tabs-container">
    <div style="padding:18px 24px 0">
      <h1 style="font-size:19px;color:#1e3a5f;margin:0">Fire Claim Examiner</h1>
      <p style="color:#666;font-size:12.5px;margin:4px 0 14px">
        Reads a lodged claim against the policy wording: what the policy says,
        which clause governs, and what to pay.</p>
    </div>
    <button class="tab-button active" onclick="switchTab('coverage', this)">Claim Desk</button>
    <button class="tab-button" onclick="switchTab('evaluation', this)">Evaluation</button>
  </div>

  <div class="content-area">

    <!-- ------------------------------------------------ claim desk -->
    <div class="tab-content active" id="coverage">

      <div class="section">
        <h2>Select a lodged claim</h2>
        <p class="help-text" style="margin-bottom:12px">
          Six claim records. Endorsements held and sums insured come from the
          claim file, not from the policy: check them against your customer
          system before relying on a determination.</p>
        <div class="claim-picker" id="picker"></div>
      </div>

      <div class="loading-state" id="loading-state" style="display:none">
        <div class="spinner"></div>
        <div>Reading the claim against the policy...</div>
      </div>

      <div class="results-section" id="results-section" style="display:none">

        <div class="decision-card" id="decision-card">
          <div class="decision-icon" id="decision-icon">✓</div>
          <div class="decision-text" id="decision-text">COVERED</div>
          <div class="decision-subtext" id="decision-subtext"></div>
        </div>

        <div class="facts" id="facts"></div>

        <div class="numbers-grid">
          <div class="number-box">
            <div class="number-label">Excess applied</div>
            <div class="number-value" id="deductible-value">nil</div>
            <div class="number-note" id="deductible-formula"></div>
          </div>
          <div class="number-box positive">
            <div class="number-label">Recommended payable</div>
            <div class="number-value" id="payable-value">nil</div>
            <div class="number-note" id="payable-note"></div>
          </div>
        </div>

        <div class="clause-section">
          <div class="clause-title">Governing authority</div>
          <div class="clause-name" id="clause-name"></div>
          <div class="clause-quote" id="clause-quote"></div>
        </div>

        <div class="section">
          <h2>How the claim was decided</h2>
          <p class="help-text">Every claim runs the same ordered chain, and the
            determination is always the <b>first gate that fails</b>. Order is not
            cosmetic: a gate placed later cannot undo a wrong answer produced by
            one placed earlier.</p>
          <div id="chain"></div>
        </div>

        <div id="quantum"></div>
        <div id="also"></div>

        <div class="section">
          <h2>Why</h2>
          <p class="help-text">The checks in the order the engine applied them.
            Period first, then whether the peril is insured, then notice, then
            the endorsement and its own conditions.</p>
          <ol class="grounds" id="grounds"></ol>
          <div id="flags"></div>
        </div>

        <div class="section">
          <h2>Item by item</h2>
          <p class="help-text">Each item claimed, the clause that admits or
            excludes it, and any average applied to its Schedule item.</p>
          <div id="breakdown"></div>
        </div>

        <div class="collapsible" onclick="toggleCollapsible(this)">
          <span>Show the calculator working</span>
          <span class="collapsible-arrow">&#9660;</span>
        </div>
        <div class="collapsible-content">
          <p class="help-text" style="margin:10px 0 0">Every step the calculator
            took, in order: exclusions first, then condition of average per
            Schedule item, then the excess per endorsement group. This is the
            audit trail behind the payable figure.</p>
          <pre class="work" id="working"></pre>
        </div>

        <button class="button" id="copy-btn" onclick="copyFile()"
                style="margin-top:16px">Copy reasoning and breakdown</button>
      </div>
    </div>

    <!-- ------------------------------------------------ evaluation -->
    <div class="tab-content" id="evaluation">
      <div class="section">
        <h2>Evaluation <span id="gate-badge"></span></h2>
        <p class="help-text">
          Every claim scored against a held-out answer key the engine never
          sees. The gate is determination 6/6, payable 2/2 exact to the ringgit,
          and governing clause ranked first on at least 5 of 6. Below that, no
          screen gets built on the engine.</p>
        <div class="metric-grid" id="eval-metrics"></div>
      </div>

      <div class="section">
        <h2>Claims</h2>
        <p class="help-text">Click any claim for the clauses applied or breached,
          the coverage position, and the limit of liability, each quoted from the
          policy.</p>
        <table class="bd">
          <thead><tr>
            <th>Claim</th><th>Expected</th><th>Returned</th>
            <th class="n">Expected payable</th><th class="n">Returned</th>
            <th>Governing clause</th>
          </tr></thead>
          <tbody id="eval-rows"></tbody>
        </table>
      </div>

      <div class="section">
        <h2>What is not yet measured</h2>
        <p class="help-text">Stated so the four passing axes are not read as the
          whole picture.</p>
        <ul id="not-measured" style="font-size:13.5px;margin-left:20px"></ul>
      </div>
    </div>

  </div>
</div>

<div id="modal" onclick="closeModal(event)">
  <div id="modal-panel">
    <div id="modal-head">
      <h3 id="modal-title"></h3>
      <button id="modal-x" onclick="closeModal(event)">&times;</button>
    </div>
    <div id="modal-body"></div>
  </div>
</div>
"""


def main():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fire Claim Examiner</title>
<style>
{CSS}
</style>
</head>
<body>
{BODY}
<script>
const DATA = {json.dumps(DATA, default=str)};
</script>
<script>
{JS}
</script>
</body>
</html>
"""
    out = ROOT / "app" / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"built {out}  ({len(html):,} bytes, self-contained)")


if __name__ == "__main__":
    main()
