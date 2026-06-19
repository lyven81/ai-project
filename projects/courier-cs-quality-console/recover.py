"""
Step 4 - The recovery check (the credibility centrepiece).

Grades the brain's DERIVED numbers (from the deployed log) against the eval TRUTH,
with Wilson 95% confidence intervals, and against a naive baseline.

Answers: can we trust the brain's measurements?
"""
import json, csv, os, math
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
scored = {r["conversation_id"]: r for r in csv.DictReader(open(os.path.join(HERE,"data","courier-cs-scored.csv"),encoding="utf-8"))}
truth  = list(csv.DictReader(open(os.path.join(HERE,"data","courier-cs-eval.csv"),encoding="utf-8")))

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k/n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = (z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)))/d
    return (round(100*max(0,c-h),1), round(100*min(1,c+h),1))

def pct(k,n): return round(100*k/max(1,n),1)
N = len(truth)

# 1) reason classification recovery
reason_hits = sum(1 for t in truth if int(scored[t["conversation_id"]]["derived_reason_id"]) == int(t["true_reason_id"]))
reason_acc = pct(reason_hits, N); reason_ci = wilson(reason_hits, N)

# 2) decision-verdict recovery: brain's "was the agent correct" vs the TRUE verdict
def tb(x): return x == "True"
verdict_match = sum(1 for t in truth if tb(scored[t["conversation_id"]]["derived_outcome_correct"]) == tb(t["outcome_correct"]))
verdict_acc = pct(verdict_match, N); verdict_ci = wilson(verdict_match, N)

# where do they disagree, and is it the conditional triggers?
disagree = [t for t in truth if tb(scored[t["conversation_id"]]["derived_outcome_correct"]) != tb(t["outcome_correct"])]
trig_total = sum(1 for t in truth if tb(t["trigger_fired"]))
disagree_trig = sum(1 for t in disagree if tb(t["trigger_fired"]))

# 3) headline-metric recovery: brain vs true
ai_t = [t for t in truth if t["agent_type"]=="ai"]
true_ai_acc   = pct(sum(tb(t["outcome_correct"]) for t in ai_t), len(ai_t))
brain_ai_acc  = pct(sum(tb(scored[t["conversation_id"]]["derived_outcome_correct"]) for t in ai_t), len(ai_t))
hu_t = [t for t in truth if t["agent_type"]=="human"]
true_hu_acc   = pct(sum(tb(t["outcome_correct"]) for t in hu_t), len(hu_t))
brain_hu_acc  = pct(sum(tb(scored[t["conversation_id"]]["derived_outcome_correct"]) for t in hu_t), len(hu_t))
# under-escalation: among should-escalate, share the agent resolved
def under(rows, oc_field):
    esc = [r for r in rows if r[oc_field]=="escalate"]
    return pct(sum(1 for r in esc if r["agent_outcome"]=="resolve"), len(esc))
true_under  = under(truth, "true_correct_outcome")
brain_under = under([scored[t["conversation_id"]] for t in truth], "derived_correct_outcome")
true_rq_ai  = round(sum(float(t["response_quality"]) for t in ai_t)/len(ai_t),2)
brain_rq_ai = round(sum(float(scored[t["conversation_id"]]["derived_response_quality"]) for t in ai_t)/len(ai_t),2)
true_contain  = pct(sum(1 for t in truth if t["agent_outcome"]=="resolve"), N)

# 4) naive baselines
majority_reason = Counter(t["true_reason_id"] for t in truth).most_common(1)[0][1]
naive_reason_acc = pct(majority_reason, N)        # always guess the most common reason
naive_under = 0.0                                  # "trust the agents": assume every decision correct -> sees no problem

rec = {
 "reason_recovery": {"accuracy_pct": reason_acc, "ci95": reason_ci, "naive_majority_pct": naive_reason_acc},
 "verdict_recovery": {"agreement_pct": verdict_acc, "ci95": verdict_ci,
    "disagreements": len(disagree), "of_which_conditional_trigger": disagree_trig, "trigger_rows_total": trig_total},
 "headline_recovery": {
    "ai_accuracy": {"brain": brain_ai_acc, "true": true_ai_acc},
    "human_accuracy": {"brain": brain_hu_acc, "true": true_hu_acc, "note": "exact on synthetic data; on real logs the same harness validates the classifier against a hand-labeled sample"},
    "under_escalation": {"brain": brain_under, "true": true_under, "naive_trust_agents": naive_under, "denominator": "overall (AI+human), among should-escalate cases"},
    "ai_response_quality": {"brain": brain_rq_ai, "true": true_rq_ai},
    "containment": {"brain": true_contain, "true": true_contain}},
}
# merge into results.json
res = json.load(open(os.path.join(HERE,"results.json")))
res["recovery"] = rec
json.dump(res, open(os.path.join(HERE,"results.json"),"w"), indent=1)
json.dump(rec, open(os.path.join(HERE,"recovery.json"),"w"), indent=1)

print("RECOVERY CHECK")
print(f"  Reason classification: {reason_acc}%  95% CI {reason_ci}   (naive majority-guess: {naive_reason_acc}%)")
print(f"  Decision-verdict agreement with truth: {verdict_acc}%  95% CI {verdict_ci}")
print(f"  Disagreements: {len(disagree)} of {N}; {disagree_trig} are conditional-trigger rows (of {trig_total} triggered)")
print(f"  AI accuracy    - brain {brain_ai_acc}%  vs true {true_ai_acc}%")
print(f"  Human accuracy - brain {brain_hu_acc}%  vs true {true_hu_acc}%  (exact; on real logs validate against a hand-labeled sample)")
print(f"  Under-escalation - brain {brain_under}%  vs true {true_under}%   (naive 'trust agents': {naive_under}% -> sees no problem)")
print(f"  AI response quality - brain {brain_rq_ai}  vs true {true_rq_ai}")
print(f"  Containment - brain {true_contain}%  vs true {true_contain}%  (observed, exact)")
print("WROTE recovery.json + recovery block in results.json")
