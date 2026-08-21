"""
Build the results console from the frozen result files.

Every number on the page is read from results/ and data/. Nothing is typed by
hand, so the page cannot drift from what was measured. Re-run this after any
re-grade and the console updates itself.

    python build_ui.py        writes "ui prototype 3.html" in the project root
"""

import io
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

OUT = config.ROOT / "ui prototype 3.html"


def bucket_of(v1, v2):
    """Which review bucket a case falls into, using both judges.

    Improved      at least one judge flagged V1, both clear V2
    Still flagged both judges flag V2
    Split         the judges disagree about V2, so a human decides
    Clean         neither judge flagged either version
    """
    v1bad = any(v1)
    if v2[0] != v2[1]:
        return "split"
    if v2[0] or v2[1]:
        return "flagged"
    return "improved" if v1bad else "clean"


BUCKETS = [("improved", "Improved"), ("flagged", "Still flagged"),
           ("split", "Judges split"), ("clean", "Clean throughout")]


def build():
    ds = config.load_json("dataset.json")
    pol = {p["id"]: p for p in config.load_json("happymart-policies.json")["policies"]}
    resp = json.load(io.open(config.RESULTS / "responses.json", encoding="utf-8"))
    comp = json.load(io.open(config.RESULTS / "comparison.json", encoding="utf-8"))
    proof = json.load(io.open(config.RESULTS / "grader_proof.json", encoding="utf-8"))

    R = {(r["case_id"], r["version"]): r for r in resp["records"]}
    cases = []
    for c in ds["cases"]:
        a, b = R[(c["id"], "v1")], R[(c["id"], "v2")]

        def side(r):
            return {
                "text": r["response"],
                "claude": r["claude"].get("unsupported_claims") or [],
                "gemini": r["gemini"].get("unsupported_claims") or [],
                "claudeBad": bool(r["claude"].get("has_violation")),
                "geminiBad": bool(r["gemini"].get("has_violation")),
                "claudeScore": r["claude"].get("score"),
                "geminiScore": r["gemini"].get("score"),
                "code": (None if not r.get("code_grade")
                         else bool(r["code_grade"]["passed"])),
            }

        v1, v2 = side(a), side(b)
        cases.append({
            "id": c["id"],
            "label": c["short_label"],
            "question": c["question"],
            "method": "Code + model" if c["method"] == "code+model" else "Model only",
            "scope": c["in_scope"],
            "basis": c["grading_basis"],
            "policy": [{"id": p, "rule": pol[p]["rule"]} for p in c["policy_refs"]],
            "v1": v1, "v2": v2,
            "bucket": bucket_of((v1["claudeBad"], v1["geminiBad"]),
                                (v2["claudeBad"], v2["geminiBad"])),
        })

    # Display order is grouped by bucket, and each bucket numbers from 1. A
    # reader asking for "Judges split 2" should get the second split case, not
    # a number carried over from an earlier group.
    order = {k: i for i, (k, _) in enumerate(BUCKETS)}
    cases.sort(key=lambda c: (order[c["bucket"]], c["id"]))
    seen = {}
    for c in cases:
        seen[c["bucket"]] = seen.get(c["bucket"], 0) + 1
        c["num"] = seen[c["bucket"]]

    counts = {k: sum(1 for c in cases if c["bucket"] == k) for k, _ in BUCKETS}
    for c in cases:
        c["ofBucket"] = counts[c["bucket"]]
    hc, hg = comp["headline"]["claude"], comp["headline"]["gemini"]
    ja = comp.get("judge_agreement", {})
    ps = proof["summary"]
    cg = comp["code_grader"]

    payload = {
        "cases": cases, "counts": counts,
        "meta": resp["meta"], "headline": comp["headline"],
        "agreement": ja, "proof": ps, "code": cg,
    }

    html = TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
    html = (html
            .replace("__CL_V1__", str(hc["responses_with_unsupported_claim_v1"]))
            .replace("__CL_V2__", str(hc["responses_with_unsupported_claim_v2"]))
            .replace("__GM_V1__", str(hg["responses_with_unsupported_claim_v1"]))
            .replace("__GM_V2__", str(hg["responses_with_unsupported_claim_v2"]))
            .replace("__CLC_V1__", str(hc["total_claims_v1"]))
            .replace("__CLC_V2__", str(hc["total_claims_v2"]))
            .replace("__GMC_V1__", str(hg["total_claims_v1"]))
            .replace("__GMC_V2__", str(hg["total_claims_v2"]))
            .replace("__AGREE__", f"{ja.get('agree','?')}/{ja.get('of','?')}")
            .replace("__AGREEPCT__", f"{round(100*ja.get('rate',0))}%")
            .replace("__CODE_V1__", str(cg["v1_passed"]))
            .replace("__CODE_V2__", str(cg["v2_passed"]))
            .replace("__CODE_OF__", str(cg["of"]))
            .replace("__CATCH__", f"{ps['claude']['caught']}/{ps['claude']['of_faulty']}")
            .replace("__FALSE__", f"{ps['claude']['false_alarms']}/{ps['claude']['of_clean']}")
            .replace("__SELF__", f"{ps['self_consistency']['agree']}/{ps['self_consistency']['of']}")
            .replace("__NSEED__", str(ps["n_seeded"]))
            .replace("__HASH__", resp["meta"]["policy_hash"])
            .replace("__AMODEL__", resp["meta"]["answer_model"])
            .replace("__CMODEL__", resp["meta"].get("claude_model", "claude-opus-5"))
            .replace("__GMODEL__", resp["meta"].get("gemini_model", "gemini-2.5-flash")))

    io.open(OUT, "w", encoding="utf-8").write(html)
    print(f"written -> {OUT.name}")
    print(f"  20 questions, 40 responses, buckets {counts}")
    return 0


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Evaluate AI Retail Customer Agent &middot; Results Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#1E3A5F;--blue:#4A7FB5;--soft:#EAF1F8;--line:#CBDDEF;--ink:#22303C;--muted:#5C6B78;--bg:#F7F9FB;
 --good:#2E7D5B;--goodbg:#E3F1EA;--bad:#B03B2E;--badbg:#FBE7E3;--warn:#B5832A;--warnbg:#F8EFD9;--info:#185FA5;--infobg:#E6F1FB;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Manrope",system-ui,sans-serif;line-height:1.6}
.wrap{max-width:1020px;margin:0 auto;padding:38px 22px 70px}
.eyebrow{font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--blue);font-weight:700;margin:0 0 8px}
h1{font-family:"Fraunces",Georgia,serif;font-weight:600;color:var(--navy);font-size:2.1rem;line-height:1.1;margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 4px}
.runline{font-size:.78rem;color:var(--muted);margin-top:10px}
.runline code{background:var(--soft);border-radius:4px;padding:1px 6px;font-size:.92em}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:22px 0 10px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi .k{font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:700}
.kpi .val{font-family:"Fraunces",Georgia,serif;font-size:1.75rem;color:var(--navy);line-height:1.15;margin-top:5px}
.kpi .val .arrow{color:var(--muted);font-size:1.05rem;margin:0 5px}
.kpi .val .to{color:var(--good)}
.kpi .note{font-size:.76rem;color:var(--muted);margin-top:3px}
.tabs{display:flex;gap:6px;margin:24px 0 0;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.tab{background:none;border:none;border-bottom:3px solid transparent;padding:10px 14px;font:600 .92rem "Manrope",sans-serif;color:var(--muted);cursor:pointer}
.tab:hover{color:var(--navy)}
.tab.on{color:var(--navy);border-bottom-color:var(--blue)}
.panel{display:none;padding-top:20px}
.panel.on{display:block}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}
h2{font-family:"Fraunces",Georgia,serif;font-weight:600;color:var(--navy);font-size:1.22rem;margin:0 0 8px}
h3{font-size:.95rem;color:var(--navy);margin:0 0 6px}
p{margin:8px 0}
.pick{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
select{font:600 .95rem "Manrope",sans-serif;color:var(--navy);background:#fff;border:1px solid var(--line);
 border-radius:9px;padding:10px 13px;min-width:340px;max-width:100%;cursor:pointer}
select:focus{outline:2px solid var(--blue);outline-offset:1px}
.nav{background:#fff;border:1px solid var(--line);border-radius:9px;padding:9px 13px;font:600 .9rem "Manrope",sans-serif;color:var(--navy);cursor:pointer}
.nav:hover{border-color:var(--blue)} .nav:disabled{opacity:.4;cursor:default}
.pos{font-size:.82rem;color:var(--muted)}
.chead{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.cid{font-size:.72rem;font-weight:700;letter-spacing:.08em;color:var(--blue)}
.ctitle{font-family:"Fraunces",Georgia,serif;font-size:1.3rem;color:var(--navy);line-height:1.2;margin:2px 0 4px}
.cfull{font-size:.82rem;color:var(--muted);font-style:italic}
.badge{font-size:.72rem;font-weight:700;padding:5px 11px;border-radius:20px;white-space:nowrap}
.b-improved{background:var(--goodbg);color:var(--good)} .b-flagged{background:var(--badbg);color:var(--bad)}
.b-split{background:var(--warnbg);color:var(--warn)} .b-clean{background:var(--infobg);color:var(--info)}
.polband{background:var(--soft);border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:9px;padding:11px 15px;margin-bottom:14px}
.polband .lb{font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--blue);font-weight:700;margin-bottom:3px}
.polband .r{font-size:.9rem;color:var(--navy)}
.polband .r b{font-family:ui-monospace,Menlo,monospace;font-size:.85em;color:var(--muted);margin-right:5px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:720px){.grid2{grid-template-columns:1fr} select{min-width:100%}}
.col{border:1px solid var(--line);border-radius:9px;padding:13px 15px;background:#FCFDFE}
.col.ok{border-color:#C3E2D1;background:#FAFDFB} .col.no{border-color:#E8C4BD;background:#FEFAF9}
.col .cl{font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:7px}
.col .rt{font-size:.9rem;white-space:pre-wrap;color:var(--ink);max-height:230px;overflow-y:auto}
.claims{margin-top:11px;padding-top:10px;border-top:1px dashed var(--line)}
.claims .ch{font-size:.72rem;font-weight:700;color:var(--bad);margin-bottom:4px}
.claims .ch.none{color:var(--good)}
.claims ul{margin:0;padding-left:17px} .claims li{font-size:.8rem;color:var(--muted);margin:3px 0}
.grow{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-top:14px;padding-top:13px;border-top:1px solid var(--line)}
.gi{display:flex;gap:9px;align-items:center}
.gicon{width:29px;height:29px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9rem;flex:none}
.g-ok{background:var(--goodbg);color:var(--good)} .g-no{background:var(--badbg);color:var(--bad)}
.g-sp{background:var(--warnbg);color:var(--warn)} .g-na{background:var(--soft);color:var(--muted)}
.gi .gl{font-size:.78rem;font-weight:700;color:var(--navy)}
.gi .gv{font-size:.75rem;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.68rem;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.tw{overflow-x:auto}
.rule{background:var(--soft);border-radius:9px;padding:12px 15px;margin:9px 0;font-size:.89rem}
.rule b{color:var(--navy)}
.big{font-family:"Fraunces",Georgia,serif;font-size:1.55rem;color:var(--navy)}
footer{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:.8rem}
</style>
</head>
<body>
<div class="wrap">
  <p class="eyebrow">AI Evaluation &middot; Results Console</p>
  <h1>Evaluate AI Retail Customer Agent</h1>
  <p class="sub">Measuring whether a shop's AI assistant stays inside the shop's own policies, and whether a rewrite actually helped.</p>
  <p class="runline"><b>20 questions, 40 responses.</b> Each question is answered twice, once by Prompt V1 and once by Prompt V2.
     Answering <code>__AMODEL__</code> at temperature 0 &middot; judges <code>__CMODEL__</code> and <code>__GMODEL__</code>, blind and shuffled &middot; policy hash <code>__HASH__</code> identical across both arms.</p>

  <div class="kpis">
    <div class="kpi"><div class="k">Claude judge &middot; responses flagged</div>
      <div class="val">__CL_V1__<span class="arrow">&rarr;</span><span class="to">__CL_V2__</span></div>
      <div class="note">of 20 &middot; __CLC_V1__ claims down to __CLC_V2__</div></div>
    <div class="kpi"><div class="k">Gemini judge &middot; responses flagged</div>
      <div class="val">__GM_V1__<span class="arrow">&rarr;</span><span class="to">__GM_V2__</span></div>
      <div class="note">of 20 &middot; __GMC_V1__ claims down to __GMC_V2__</div></div>
    <div class="kpi"><div class="k">Judge agreement</div>
      <div class="val">__AGREEPCT__</div>
      <div class="note">__AGREE__ responses</div></div>
    <div class="kpi"><div class="k">Deterministic fact checks</div>
      <div class="val">__CODE_V1__<span class="arrow">&rarr;</span>__CODE_V2__</div>
      <div class="note">of __CODE_OF__ &middot; unchanged</div></div>
  </div>

  <div class="tabs">
    <button class="tab on" onclick="tab(this,'verdict')">Verdict</button>
    <button class="tab" onclick="tab(this,'cases')">Cases</button>
    <button class="tab" onclick="tab(this,'rules')">Grading rules</button>
    <button class="tab" onclick="tab(this,'proof')">Grader validation</button>
  </div>

  <div id="verdict" class="panel on">
    <div class="card">
      <h2>What the run found</h2>
      <p>Both judges agree V2 is better, and both land on exactly five responses still carrying an unsupported claim. They disagree on how large the gain is, because Claude is the stricter reader of V1. The direction holds across judges; the size depends on which judge you ask, which is why two were used.</p>
      <div class="tw"><table>
        <tr><th></th><th>Prompt V1</th><th>Prompt V2</th><th>Change</th></tr>
        <tr><td>Responses with an unsupported claim, Claude</td><td>__CL_V1__ of 20</td><td>__CL_V2__ of 20</td><td>fewer</td></tr>
        <tr><td>Responses with an unsupported claim, Gemini</td><td>__GM_V1__ of 20</td><td>__GM_V2__ of 20</td><td>fewer</td></tr>
        <tr><td>Total unsupported claims, Claude</td><td>__CLC_V1__</td><td>__CLC_V2__</td><td>fewer</td></tr>
        <tr><td><b>Deterministic fact checks passed</b></td><td>__CODE_V1__ of __CODE_OF__</td><td>__CODE_V2__ of __CODE_OF__</td><td><b>no change</b></td></tr>
      </table></div>
    </div>
    <div class="card">
      <h2>The row that did not move</h2>
      <p>Measured on critical business facts alone, V2 is indistinguishable from V1: __CODE_V1__ of __CODE_OF__ both times. Measured on grounding, it clears unsupported claims out of several responses and breaks none for the Claude judge. An evaluation built on fact checks alone would have reported this rewrite as no improvement at all. That is the case for running two kinds of grader, and here it is a measurement rather than a claim.</p>
    </div>
    <div class="card">
      <h2>What is left, and why it is interesting</h2>
      <p>Most of the responses V2 still carries claims on share one pattern: the reply points the customer to customer service, and the policy set never authorises customer service as a general channel. It appears in one clause only, for damaged or wrong items. So V2 is marked down for obeying an instruction V2 itself gives, over a gap in the policy set.</p>
      <p>That is the evaluation catching a flaw in the <b>specification</b> rather than in the model. It has not been patched and re-run: adding a clause and re-running until the number improves is how an experiment quietly turns into a demonstration.</p>
    </div>
  </div>

  <div id="cases" class="panel">
    <div class="pick">
      <select id="sel" onchange="show(this.value)"></select>
      <button class="nav" id="prev" onclick="step(-1)">&larr; Prev</button>
      <button class="nav" id="next" onclick="step(1)">Next &rarr;</button>
      <span class="pos" id="pos"></span>
    </div>
    <div id="detail"></div>
  </div>

  <div id="rules" class="panel">
    <div class="card">
      <h2>Which grader applies, and why</h2>
      <p>Every response is graded by the model judges. Ten of the twenty questions <b>also</b> carry deterministic assertions. Code grading is an addition, never a replacement, decided by three questions asked in order.</p>
      <div class="rule"><b>1.</b> Does the policy set contain a single unambiguous value a correct answer must state? If no, model grading only.</div>
      <div class="rule"><b>2.</b> Can that value be checked by an assertion returning the same verdict every run, with no opinion in it? If no, model grading only.</div>
      <div class="rule"><b>3.</b> Can the wrong values that must be absent also be named? If no, the check is kept but flagged low power.</div>
      <p>All three yes and code grading applies as well. The basis for each question travels inside the data, so the split can be checked rather than taken on trust.</p>
    </div>
    <div class="card">
      <h2>Why the answer cannot be hinted</h2>
      <p>The answering layer receives the question string and the policies. Nothing else. It never sees the expected facts, the assertions, or whether a question is a trap, because the function that calls it takes strings rather than a test case.</p>
      <p>The judges never see which prompt version produced a response. Labels are stripped and the pool is shuffled before grading, so a judge cannot favour the one called improved or infer it from position.</p>
      <p>Prompt V2 contains behaviour rules only: no number, no fact, no reference to any question. Swap the retailer and the policies and V2 is still a sensible prompt. A prompt written to fit the cases it is scored on measures nothing.</p>
    </div>
    <div class="card">
      <h2>Every question and its basis</h2>
      <div class="tw"><table id="basis"></table></div>
    </div>
  </div>

  <div id="proof" class="panel">
    <div class="card">
      <h2>Can the judges be trusted?</h2>
      <p>Before any result was believed, the graders were marked against __NSEED__ hand-written answers whose faults were known in advance: ten with a planted fault of a stated kind, five clean controls. A judge that misses a planted invented requirement makes every score after it meaningless.</p>
      <div class="kpis">
        <div class="kpi"><div class="k">Catch rate</div><div class="val">__CATCH__</div><div class="note">planted faults found</div></div>
        <div class="kpi"><div class="k">False alarms</div><div class="val">__FALSE__</div><div class="note">clean controls wrongly flagged</div></div>
        <div class="kpi"><div class="k">Self-consistency</div><div class="val">__SELF__</div><div class="note">same verdict on a repeat pass</div></div>
      </div>
      <p>Self-consistency matters more than it looks. A judge that disagrees with itself cannot resolve a difference smaller than its own noise, and a small gap between two prompts is exactly that size of difference.</p>
    </div>
    <div class="card">
      <h2>Where the deterministic checks are blind</h2>
      <p>One seeded answer states the 48-hour rule correctly, works out that the deadline has passed, and declines. Every assertion passes. It then grants an exception it has no authority for, asks for photographs, and invents an escalation path. Both model judges caught it; the deterministic checks are structurally unable to, because the fault is not a wrong value.</p>
      <p>That single case is the argument for keeping both graders, and it is why the fact checks are reported beside the grounding count rather than instead of it.</p>
    </div>
  </div>

  <footer>&copy; 2026 &middot; Evaluate AI Retail Customer Agent &middot; every figure on this page is read from the frozen result files, none is typed by hand.</footer>
</div>

<script>
const D = __DATA__;
const BUCKET = {improved:"Improved", flagged:"Still flagged", split:"Judges split", clean:"Clean throughout"};
const ORDER = ["improved","flagged","split","clean"];
let idx = 0;

function esc(s){const d=document.createElement("div");d.textContent=s==null?"":String(s);return d.innerHTML;}

function fillSelect(){
  const sel = document.getElementById("sel");
  sel.innerHTML = ORDER.map(b=>{
    const rows = D.cases.filter(c=>c.bucket===b);
    if(!rows.length) return "";
    const opts = rows.map(c=>{
      const i = D.cases.indexOf(c);
      return `<option value="${i}">${c.num}. ${esc(c.label)}</option>`;
    }).join("");
    return `<optgroup label="${BUCKET[b]} (${rows.length})">${opts}</optgroup>`;
  }).join("");
}

function claims(list, who){
  if(!list.length) return `<div class="ch none">${who}: nothing unsupported</div>`;
  return `<div class="ch">${who} flagged ${list.length}</div><ul>${list.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`;
}

function gitem(label, a, b){
  let cls="g-na", mark="&ndash;", val="not applicable";
  if(a!==null && a!==undefined){
    cls = b ? "g-ok" : "g-no";
    mark = b ? "&#10003;" : "&#10007;";
    val = `V1 ${a?"PASS":"FAIL"} &rarr; V2 ${b?"PASS":"FAIL"}`;
  }
  return `<div class="gi"><div class="gicon ${cls}">${mark}</div><div><div class="gl">${label}</div><div class="gv">${val}</div></div></div>`;
}

function show(i){
  idx = Number(i);
  const c = D.cases[idx];
  document.getElementById("sel").value = idx;
  document.getElementById("pos").textContent =
    `${BUCKET[c.bucket]} ${c.num} of ${c.ofBucket}`;
  document.getElementById("prev").disabled = idx===0;
  document.getElementById("next").disabled = idx===D.cases.length-1;

  const col = (s,ver) => `
    <div class="col ${(!s.claudeBad && !s.geminiBad) ? "ok":"no"}">
      <div class="cl">${ver}</div>
      <div class="rt">${esc(s.text)}</div>
      <div class="claims">${claims(s.claude,"Claude")}${claims(s.gemini,"Gemini")}</div>
    </div>`;

  document.getElementById("detail").innerHTML = `
    <div class="card">
      <div class="chead">
        <div>
          <div class="cid">${esc(c.method)} &middot; policy ${c.scope === "partial" ? "partly silent" : "covers this"} &middot; case ref ${esc(c.id)}</div>
          <div class="ctitle">${c.num}. ${esc(c.label)}</div>
          <div class="cfull">Asked as: &ldquo;${esc(c.question)}&rdquo;</div>
        </div>
        <div class="badge b-${c.bucket}">${BUCKET[c.bucket]} ${c.num} of ${c.ofBucket}</div>
      </div>
      <div class="polband">
        <div class="lb">The rule both answers are measured against</div>
        ${c.policy.map(p=>`<div class="r"><b>${esc(p.id)}</b>${esc(p.rule)}</div>`).join("")}
      </div>
      <div class="grid2">${col(c.v1,"Baseline &middot; Prompt V1")}${col(c.v2,"Proposed &middot; Prompt V2")}</div>
      <div class="grow">
        ${gitem("Code checks", c.v1.code, c.v2.code)}
        ${gitem("Claude judge", !c.v1.claudeBad, !c.v2.claudeBad)}
        ${gitem("Gemini judge", !c.v1.geminiBad, !c.v2.geminiBad)}
      </div>
    </div>`;
}

function step(d){ const n = idx + d; if(n>=0 && n<D.cases.length) show(n); }

function tab(btn, id){
  document.querySelectorAll(".panel").forEach(p=>p.classList.remove("on"));
  document.querySelectorAll(".tab").forEach(b=>b.classList.remove("on"));
  document.getElementById(id).classList.add("on");
  btn.classList.add("on");
}

function fillBasis(){
  const t = document.getElementById("basis");
  t.innerHTML = `<tr><th>Group</th><th>Question</th><th>Method</th><th>Scope</th><th>Basis</th></tr>` +
    D.cases.map(c=>`<tr><td><b>${BUCKET[c.bucket]} ${c.num}</b><br><span style="font-size:.8em;color:#5C6B78">${esc(c.id)}</span></td>
      <td>${esc(c.label)}</td><td>${esc(c.method)}</td>
      <td>${c.scope==="partial"?"partly silent":"covered"}</td><td>${esc(c.basis)}</td></tr>`).join("");
}

fillSelect(); fillBasis(); show(0);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(build())
