"""
Step 3 - The measurement brain (courier CS quality management layer).

Reads ONLY the deployed log (no truth columns) + the Step 1 answer key.
For each conversation it:
  1. classifies the contact reason from the message text (keyword signatures),
  2. looks up the correct outcome for that reason and scores the agent's gate decision,
  3. scores the response against the reason's good-response checklist.
Then it aggregates the management metrics into results.json and writes a scored log.

The brain never reads the truth columns. Step 4 grades these derived values
against the eval truth.
"""

import json, csv, os, glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = json.load(open(glob.glob(os.path.join(HERE, "*ground-truth-key.json"))[0], encoding="utf-8"))
REASONS = {r["id"]: r for r in KEY["reasons"]}; REASONS[0] = KEY["out_of_scope"]
log = list(csv.DictReader(open(os.path.join(HERE, "data", "courier-cs-log.csv"), encoding="utf-8")))

# --- reason classifier: keyword signatures (genuine, imperfect, derives from text alone) ---
SIG = {
 0:["ceo","salary","branch manager","home address"],
 1:["hasn't updated","no update","not updated","update on my shipment"],
 2:["delivered but","never received","nothing arrived","says delivered"],
 3:["when will","estimated delivery","delivery date"],
 4:["stuck","customs","sorting hub","held at"],
 5:["out for delivery"],
 6:["missed the delivery","redeliver","no one was home, can you"],
 7:["was home all day","recipient unavailable","never left"],
 8:["change my delivery address","change my address","reschedule the delivery"],
 9:["collect at your branch","self-collect","collect at the hub","branch instead"],
 10:["broken","damaged","wet"],
 11:["lost","missing for weeks","file a claim","compensation"],
 12:["wrong parcel","someone else's parcel","not mine"],
 13:["items are missing","items are gone","half the items"],
 14:["guardhouse","neighbour","leave my parcel"],
 15:["rude","attitude","unprofessional"],
 16:["threw","left outside","not handed"],
 17:["cod","overcharged","already paid","owing"],
 18:["surcharge","remote area","weight fee","extra"],
 19:["pickup","pick up","no rider showed"],
 20:["return a parcel","rejected","reship"],
}

def classify(msg):
    m = msg.lower()
    best, score = 0, 0
    for rid, kws in SIG.items():
        s = sum(1 for k in kws if k in m)
        if s > score:
            best, score = rid, s
    return best  # falls back to 0 (out of scope) if nothing matches

def score_response(resp, reason_id):
    items = REASONS[reason_id]["good_response_must_include"]
    if not items: return 0.0
    covered = sum(1 for it in items if it.split("(")[0].strip().lower()[:18] in resp.lower())
    return round(covered/len(items), 2)

# --- derive per-conversation, write scored log ---
scored = []
for r in log:
    rid = classify(r["customer_message"])
    correct_oc = REASONS[rid]["correct_outcome"]          # brain uses the primary outcome (cannot see hidden triggers)
    oc_correct = (r["agent_outcome"] == correct_oc)
    q = score_response(r["agent_response"], rid)
    s = dict(r)
    s.update(derived_reason_id=rid, derived_reason=REASONS[rid]["reason"],
             derived_category=REASONS[rid]["category"],
             derived_correct_outcome=correct_oc, derived_outcome_correct=oc_correct,
             derived_response_quality=q)
    scored.append(s)

with open(os.path.join(HERE,"data","courier-cs-scored.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=list(scored[0].keys())); w.writeheader(); w.writerows(scored)

# --- aggregate metrics ---
def pct(n,d): return round(100*n/max(1,d),1)
ai=[r for r in scored if r["agent_type"]=="ai"]; hu=[r for r in scored if r["agent_type"]=="human"]
N=len(scored)

containment=pct(sum(r["agent_outcome"]=="resolve" for r in scored),N)
escalation =pct(sum(r["agent_outcome"]=="escalate" for r in scored),N)
decline    =pct(sum(r["agent_outcome"]=="decline" for r in scored),N)

def acc(sub): return pct(sum(r["derived_outcome_correct"] for r in sub),len(sub))
# confusion: derived-correct-outcome (rows) vs agent_outcome (cols)
classes=["resolve","escalate","decline"]
conf={t:{p:0 for p in classes} for t in classes}
for r in scored: conf[r["derived_correct_outcome"]][r["agent_outcome"]]+=1
esc_rows=[r for r in scored if r["derived_correct_outcome"]=="escalate"]
res_rows=[r for r in scored if r["derived_correct_outcome"]=="resolve"]
under_esc=pct(sum(r["agent_outcome"]=="resolve" for r in esc_rows),len(esc_rows))
over_esc =pct(sum(r["agent_outcome"]=="escalate" for r in res_rows),len(res_rows))

csat=[int(r["csat"]) for r in scored if r["csat"]!=""]
csat_correct=[int(r["csat"]) for r in scored if r["csat"]!="" and r["derived_outcome_correct"]]
csat_wrong=[int(r["csat"]) for r in scored if r["csat"]!="" and not r["derived_outcome_correct"]]
def avg(x): return round(sum(x)/max(1,len(x)),2)

# pareto over derived reasons
pc=Counter(r["derived_reason_id"] for r in scored)
pareto=[]
for rid,c in pc.most_common():
    sub=[r for r in scored if r["derived_reason_id"]==rid]
    pareto.append({"reason_id":rid,"reason":REASONS[rid]["reason"],"count":c,"pct":pct(c,N),
                   "escalated_share":pct(sum(x["agent_outcome"]=="escalate" for x in sub),len(sub))})

# root cause: where AI under-escalated (resolved a should-escalate)
ue=[r for r in ai if r["derived_correct_outcome"]=="escalate" and r["agent_outcome"]=="resolve"]
top_ue=Counter(r["derived_reason"] for r in ue).most_common(5)
top_esc=Counter(r["derived_reason"] for r in scored if r["agent_outcome"]=="escalate").most_common(5)

by_channel=[]
for ch in ["website","whatsapp","app"]:
    sub=[r for r in ai if r["channel"]==ch]
    by_channel.append({"channel":ch,"count":len([r for r in scored if r['channel']==ch]),"ai_accuracy":acc(sub)})

results={
 "meta":{"title":"Courier CS Quality - measured metrics","source":"courier-cs-log.csv (deployed, no truth)","conversations":N},
 "volume":{"total":N,"ai":len(ai),"human":len(hu)},
 "outcomes":{"containment_pct":containment,"escalation_pct":escalation,"decline_pct":decline},
 "decision_quality":{"overall_accuracy":acc(scored),"ai_accuracy":acc(ai),"human_accuracy":acc(hu),
   "under_escalation_pct":under_esc,"over_escalation_pct":over_esc,"confusion":conf},
 "response_quality":{"overall_avg":avg([r["derived_response_quality"] for r in scored]),
   "ai_avg":avg([r["derived_response_quality"] for r in ai]),"human_avg":avg([r["derived_response_quality"] for r in hu])},
 "csat":{"avg":avg(csat),"n":len(csat),"when_correct":avg(csat_correct),"when_wrong":avg(csat_wrong)},
 "handle_time":{"ai_avg":round(sum(float(r["handle_time_min"]) for r in ai)/len(ai),1),
   "human_avg":round(sum(float(r["handle_time_min"]) for r in hu)/len(hu),1)},
 "pareto":pareto,
 "root_cause":{"top_under_escalation":top_ue,"top_escalation_reasons":top_esc},
 "by_channel":by_channel,
}
# ---- per-agent block (Option B): the AI + each individual human agent ----
def agent_block(sub, aid, aname):
    n=len(sub)
    cs=[int(x["csat"]) for x in sub if x["csat"]!=""]
    bad=[x for x in sub if not x["derived_outcome_correct"]]
    good=[x for x in sub if x["derived_outcome_correct"] and float(x["derived_response_quality"])>=0.8]
    def ex(x,isbad): return {"bad":isbad,"reason":x["derived_reason"],"cust":x["customer_message"],
        "rep":x["agent_response"],"did":x["agent_outcome"],"should":x["derived_correct_outcome"],"csat":x["csat"]}
    examples=[]
    if bad: examples.append(ex(bad[0],True))
    if good: examples.append(ex(good[0],False))
    return {"id":aid,"name":aname,"count":n,
        "accuracy":acc(sub),
        "response_quality":avg([x["derived_response_quality"] for x in sub]),
        "handle_time":round(sum(float(x["handle_time_min"]) for x in sub)/n,1),
        "csat":avg(cs),
        "top_reasons":Counter(x["derived_reason"] for x in sub).most_common(3),
        "examples":examples}
agents=[agent_block(ai,"ai","AI assistant")]
hum_ids={}
for x in scored:
    if x["agent_type"]=="human": hum_ids[x["agent_id"]]=x["agent_name"]
for aid,aname in sorted(hum_ids.items(), key=lambda kv: -len([x for x in scored if x["agent_id"]==kv[0]])):
    agents.append(agent_block([x for x in scored if x["agent_id"]==aid], aid, aname))
results["agents"]=agents
results["csat"]["ai"]=avg([int(x["csat"]) for x in ai if x["csat"]!=""])
results["csat"]["human"]=avg([int(x["csat"]) for x in hu if x["csat"]!=""])
oe=[x for x in scored if x["derived_correct_outcome"]=="resolve" and x["agent_outcome"]=="escalate"]
results["staff_time"]={"over_escalations":len(oe),"hours_saved":round(len(oe)*results["handle_time"]["human_avg"]/60)}

json.dump(results, open(os.path.join(HERE,"results.json"),"w"), indent=1)

# --- print a readable summary ---
print(f"Measured from the deployed log ({N} conversations, brain derived everything):")
print(f"  Containment {containment}%  Escalation {escalation}%  Decline {decline}%")
print(f"  Decision accuracy: overall {acc(scored)}%  (AI {acc(ai)}%  human {acc(hu)}%)")
print(f"  Under-escalation {under_esc}%  Over-escalation {over_esc}%")
print(f"  Response quality: AI {results['response_quality']['ai_avg']}  human {results['response_quality']['human_avg']}")
print(f"  CSAT {avg(csat)} (correct {avg(csat_correct)} / wrong {avg(csat_wrong)})")
print(f"  Handle time: AI {results['handle_time']['ai_avg']}m  human {results['handle_time']['human_avg']}m")
print("  Top under-escalation reasons (AI resolved a should-escalate):")
for name,c in top_ue: print(f"     {c:>3}  {name}")
print("WROTE results.json + data/courier-cs-scored.csv")
