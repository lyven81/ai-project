"""
Step 6 - The governed assistant (Klinik Dr Fang governed-query discipline).

A self-contained, keyless page that answers a manager's questions about the support
data, but ONLY from a fixed menu of approved queries over the structured metrics
table. It returns the exact counted number, never free SQL, never a raw-record dump,
and it refuses anything off the menu. One governed "show me examples" tool returns a
few REDACTED conversation snippets. Single-source from results.json + the scored log.
"""
import json, csv, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
SC = list(csv.DictReader(open(os.path.join(HERE, "data", "courier-cs-scored.csv"), encoding="utf-8")))

dq=R["decision_quality"]; oc=R["outcomes"]; cs=R["csat"]; st=R["staff_time"]; ag=R["agents"]
top5=" ".join(f"<li>{html.escape(p['reason'])} ({p['count']})</li>" for p in R["pareto"][:5])
ag_sorted=sorted([a for a in ag if a["id"]!="ai"], key=lambda a:-a["accuracy"])
best=ag_sorted[0]; worst=ag_sorted[-1]

# ---- approved queries: keyword triggers -> exact answer ----
APPROVED=[
 {"id":"contain","q":"What is our containment rate?","kw":["containment","handled on the spot","resolved without","self-serve","deflect"],
  "a":f"<b>{round(oc['containment_pct'])}%</b> of contacts were handled on the spot, settled without passing to anyone."},
 {"id":"acc","q":"How accurate are the decisions overall?","kw":["accuracy","right action","correct decision","gate"],
  "a":f"The team took the right next step on <b>{dq['overall_accuracy']}%</b> of conversations (AI {dq['ai_accuracy']}%, human team {dq['human_accuracy']}%)."},
 {"id":"under","q":"What is our under-escalation rate?","kw":["under-escalation","under escalation","brushed off","closed instead","missed escalation","claims closed"],
  "a":f"<b>{dq['under_escalation_pct']}%</b> of cases that should reach a specialist were closed instead. That is <b>{dq['confusion']['escalate']['resolve']}</b> high-stakes cases this period, almost all from the chatbot."},
 {"id":"reasons","q":"What do customers contact us about most?","kw":["contact about","top reasons","most common","pareto","why do customers","volume"],
  "a":f"Top five reasons:<ul>{top5}</ul>"},
 {"id":"agents","q":"Who is strongest and who needs the most coaching?","kw":["strongest","best agent","coaching","weakest","who needs","appraisal","ranking","agent performance"],
  "a":f"Strongest: <b>{best['name']}</b> ({round(best['accuracy'])}% right action). Needs the most coaching: <b>{worst['name']}</b> ({round(worst['accuracy'])}%). The AI assistant sits at {round(ag[0]['accuracy'])}%."},
 {"id":"csat","q":"What is our customer satisfaction?","kw":["csat","satisfaction","happiness","rating","stars"],
  "a":f"Average CSAT is <b>{cs['avg']}/5</b>. When the team got the outcome right it was {cs['when_correct']}; when wrong it fell to {cs['when_wrong']}, a {round(cs['when_correct']-cs['when_wrong'],1)}-star swing."},
 {"id":"time","q":"How much staff time is spent on easy questions?","kw":["over-escalation","over escalation","easy questions","staff time","hours","wasted","bumped to a person"],
  "a":f"<b>{st['over_escalations']}</b> simple questions were bumped to a person when the chatbot could have closed them, about <b>{st['hours_saved']} hours</b> of staff time."},
]

# ---- redacted-snippet tool: topic -> a few redacted example rows ----
def redact(s):
    s=re.sub(r"\d","#",s)                       # numbers
    s=re.sub(r"\b(CEO|manager|salary)\b","[redacted]",s,flags=re.I)
    return html.escape(s)
SNIP_TOPICS={
 "damaged":["damaged","wet","broken"],"lost":["lost","missing"],"claim":["claim","damaged","lost","missing"],
 "payment":["cod","owing","surcharge","fee"],"rude":["rude","unprofessional"],"delivered":["delivered"]}
def snippets(topic):
    kws=SNIP_TOPICS.get(topic,[topic])
    rows=[r for r in SC if r["agent_type"]=="ai" and r["derived_outcome_correct"]=="False"
          and any(k in r["derived_reason"].lower() for k in kws)][:3]
    if not rows: return None
    return [{"reason":html.escape(r["derived_reason"]),"cust":redact(r["customer_message"]),
             "rep":redact(r["agent_response"][:120]),"did":r["agent_outcome"],"should":r["derived_correct_outcome"]} for r in rows]
SNIPS={t:snippets(t) for t in SNIP_TOPICS}

DATA=("const APPROVED="+json.dumps(APPROVED)+";\n"
      "const SNIPS="+json.dumps(SNIPS)+";\n")

tpl=open(os.path.join(HERE,"_assistant_template.html"),encoding="utf-8").read()
open(os.path.join(HERE,"courier-cs-assistant.html"),"w",encoding="utf-8").write(tpl.replace("/*__DATA__*/",DATA))
print("WROTE courier-cs-assistant.html")
print(f"  {len(APPROVED)} approved queries; redacted-snippet topics: "+", ".join(k for k,v in SNIPS.items() if v))
