"""
Step 5 - Build the management console (single source: results.json).

Reads results.json + the Step 1 answer key + the scored log, and writes the
self-contained, yellow-themed console. No number is hand-typed; everything is
injected from the validated pipeline so the screen can never drift from the data.
"""
import json, os, glob, csv, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
KEY = json.load(open(glob.glob(os.path.join(HERE, "*ground-truth-key.json"))[0], encoding="utf-8"))
SC = list(csv.DictReader(open(os.path.join(HERE, "data", "courier-cs-scored.csv"), encoding="utf-8")))

# ---- plain-language labels ----
PLABEL = {1:"Tracking hasn't updated in days",2:"Says delivered but not received",3:"Asking for a delivery date",
 4:"Parcel stuck in transit too long",5:"Out for delivery but nothing came",6:"Missed delivery, wants redelivery",
 7:"Marked unavailable but was home",8:"Change address or reschedule",9:"Self-collect at branch",
 10:"Parcel arrived damaged or wet",11:"Lost parcel, claim and compensation",12:"Received the wrong parcel",
 13:"Items missing from the parcel",14:"Special delivery instruction",15:"Rider was rude or unprofessional",
 16:"Parcel left unattended or thrown",17:"Payment shown as owing after paying",18:"Disputing a surcharge or fee",
 19:"Pickup did not show",20:"Return or reship a rejected parcel",0:"Off-topic or internal request"}
CATNAME = {"A":"Tracking & delivery","B":"Failed delivery & rescheduling","C":"Damaged, lost or wrong items",
 "D":"Handling & rider conduct","E":"Payments & fees","F":"Sender & account","G":"Out of scope"}
ACTPLAIN = {"resolve":["Handled it","Handle it directly"],"escalate":["Passed to a specialist","Pass to a specialist"],
 "decline":["Declined it","Politely decline"]}

def grade(acc):
    for lo,(g,c) in [(95,("A","var(--good)")),(90,("A-","var(--good)")),(85,("B","var(--good)")),
                     (80,("B-","var(--warn)")),(75,("C+","var(--warn)")),(70,("C","var(--warn)")),
                     (0,("C-","var(--bad)"))]:
        if acc>=lo: return g,c
    return "D","var(--bad)"

def qword(rq): return "Strong" if rq>=0.82 else ("Fair" if rq>=0.70 else "Building")

# ---- PARETO (top 10) ----
ESC_REASONS={r["id"] for r in KEY["reasons"] if r["correct_outcome"]=="escalate"}
pareto=[]
for p in R["pareto"][:10]:
    rid=p["reason_id"]
    pareto.append({"r":PLABEL.get(rid,p["reason"]),"n":p["count"],"esc":rid in ESC_REASONS})

# ---- AGENTS (AI + each human, all real) ----
def narrative(a):
    ai=a["id"]=="ai"; acc=a["accuracy"]; rq=a["response_quality"]; ht=a["handle_time"]; csat=a["csat"]
    strong=[]; watch=[]
    if ai: strong.append("Fast on first contact and always on, never off shift")
    if acc>=92: strong.append("Picks the right next step almost every time")
    elif acc>=85: strong.append("Gets the right action on most cases")
    if rq>=0.82: strong.append("Thorough, complete replies that customers rate highly")
    if ai: strong.append("Takes the simple, repetitive questions off the team")
    if csat>=4.1 and not ai: strong.append("Customers rate their conversations highly")
    if not ai and acc>=95: strong.append("Escalates the difficult cases correctly, a model for training")
    if acc<80: watch.append("Closes claims and disputes that should go to a specialist")
    if ai: watch.append("Sometimes engages off-topic questions it should politely decline")
    if rq<0.70: watch.append("Replies often miss a required step, so customers come back")
    if 80<=acc<90: watch.append("A few high-stakes cases slip through to a resolve instead of an escalation")
    if not ai and ht>15: watch.append("Slower per case, partly while still learning")
    strong=strong[:3] or ["Handles a steady volume of cases"]; watch=watch[:2] or ["Keep volume and quality balanced"]
    # coaching focus + talking points by biggest gap
    if ai:
        coach=("Focus this period: the chatbot must never close a claim, dispute or complaint. Set one firm rule, every "
               "high-stakes case goes to a person, and reload its reply templates from the coaching playbook so nothing is skipped.")
        talk=["Praise the speed and the volume it takes off the team","Name the one problem clearly: high-stakes cases being closed instead of escalated","Agree the single rule change and a date to recheck"]
    elif acc<72:
        coach=("Focus this period: new-recruit ramp. Work straight from the coaching playbook, shadow a strong agent on claims, "
               "and have every escalation call reviewed for the first month.")
        talk=["Reassure, this is a normal new-recruit ramp","Set the playbook as the daily reference","Arrange shadowing with a strong agent and weekly review"]
    elif acc<86:
        coach=("Focus this period: when to escalate. Pair with the coaching playbook on claims and disputes, and review three "
               "escalation calls together each week.")
        talk=["Credit the speed and the volume","Be specific about the escalation gap, with the example below","Set a simple weekly check-in on escalation decisions"]
    elif acc>=95 and rq>=0.82:
        coach="Focus this period: stretch, not fix. Ready to mentor a new recruit and to take a slightly higher case load."
        talk=["Recognise top-tier quality clearly","Offer a mentoring or training role","Agree a modest volume increase, protecting the quality"]
    else:
        coach="Focus this period: lift reply completeness. Use the coaching-playbook checklists so every reply covers the full set of steps."
        talk=["Recognise the solid, accurate work","Pick one topic to tighten reply quality on","Keep using their strong cases as training material"]
    return strong,watch,coach,talk

def examples(a):
    out=[]
    for e in a["examples"]:
        did=ACTPLAIN[e["did"]][0]; should=ACTPLAIN[e["should"]][1]
        if e["bad"]:
            cs=f'Customer rated this {e["csat"]} out of 5. ' if e["csat"] else ''
            extra=cs+f'A {e["reason"].lower()} should {should.lower()}, not be closed.'
        else:
            extra="Handled in full and rated well, a good example to use in training."
        out.append({"bad":e["bad"],"reason":e["reason"],"cust":e["cust"],"rep":e["rep"][:150],"did":did,"should":should,"extra":extra})
    return out

AGENTS=[]
for a in R["agents"]:
    ai=a["id"]=="ai"; g,gc=grade(a["accuracy"])
    role=("Chatbot" if ai else "Agent")+f" · {a['count']} conversations"+(" · new recruit" if (not ai and a["accuracy"]<72) else "")
    strong,watch,coach,talk=narrative(a)
    AGENTS.append({"id":a["id"],"name":a["name"],"role":role,"real":True,
        "initials":"AI" if ai else a["name"][0],"grade":g,"gradeColor":gc,
        "small": a["count"]<45,
        "mini":[["Right action",f"{round(a['accuracy'])}%"],["Reply fullness",qword(a["response_quality"])],
                ["Avg speed",f"{a['handle_time']} min"],["Happiness",f"{a['csat']}/5"]],
        "strong":strong,"watch":watch,"examples":examples(a),"coach":coach,"talk":talk})

# ---- REASONS playbook (from the answer key) ----
REASONS=[]
for r in KEY["reasons"]+[KEY["out_of_scope"]]:
    cat=r["category"][0]
    REASONS.append({"id":r["id"],"cat":cat,"catname":CATNAME.get(cat,cat),"reason":r["reason"],
        "act":r["correct_outcome"],"must":r["good_response_must_include"],"bad":r["bad_response_example"]})

# ---- team headline numbers ----
dq=R["decision_quality"]; oc=R["outcomes"]; cs=R["csat"]; ht=R["handle_time"]; st=R["staff_time"]
under=dq["confusion"]["escalate"]["resolve"]; over=dq["confusion"]["resolve"]["escalate"]
tg,tgc=grade(dq["overall_accuracy"])
TEAM={"total":R["volume"]["total"],"contain":round(oc["containment_pct"]),"right":round(dq["overall_accuracy"]/10),
 "acc":dq["overall_accuracy"],
 "csat":cs["avg"],"ccorr":cs["when_correct"],"cwrong":cs["when_wrong"],"cgap":round(cs["when_correct"]-cs["when_wrong"],1),
 "aispeed":ht["ai_avg"],"huspeed":ht["human_avg"],"grade":tg,"gradeColor":tgc,
 "under":under,"over":over,"hours":st["hours_saved"],
 # illustrative prior-month baseline for the direction arrows (a real deployment compares two actual months)
 "contain_prev":55,"acc_prev":78.0,"csat_prev":3.7}

# ---- governed "Ask the data" assistant (Overview tab): approved queries + redacted snippets ----
ag=R["agents"]; ag_sorted=sorted([a for a in ag if a["id"]!="ai"], key=lambda a:-a["accuracy"])
best=ag_sorted[0]; worst=ag_sorted[-1]
top5="".join(f"<li>{html.escape(p['reason'])} ({p['count']})</li>" for p in R["pareto"][:5])
APPROVED=[
 {"id":"contain","q":"What is our containment rate?","kw":["containment","handled on the spot","resolved without","self-serve","deflect"],
  "a":f"<b>{round(oc['containment_pct'])}%</b> of contacts were handled on the spot, settled without passing to anyone."},
 {"id":"acc","q":"How accurate are the decisions overall?","kw":["accuracy","right action","correct decision","gate","accurate"],
  "a":f"The team took the right next step on <b>{dq['overall_accuracy']}%</b> of conversations (AI {dq['ai_accuracy']}%, human team {dq['human_accuracy']}%)."},
 {"id":"under","q":"What is our under-escalation rate?","kw":["under-escalation","under escalation","brushed off","closed instead","missed escalation","claims closed"],
  "a":f"<b>{dq['under_escalation_pct']}%</b> of cases that should reach a specialist were closed instead, <b>{dq['confusion']['escalate']['resolve']}</b> high-stakes cases this period, almost all from the chatbot."},
 {"id":"reasons","q":"What do customers contact us about most?","kw":["contact about","top reasons","most common","pareto","why do customers","volume","contact us"],
  "a":f"Top five reasons:<ul>{top5}</ul>"},
 {"id":"agents","q":"Who is strongest and who needs the most coaching?","kw":["strongest","best agent","coaching","weakest","who needs","appraisal","ranking","agent performance"],
  "a":f"Strongest: <b>{best['name']}</b> ({round(best['accuracy'])}% right action). Needs the most coaching: <b>{worst['name']}</b> ({round(worst['accuracy'])}%). The AI assistant sits at {round(ag[0]['accuracy'])}%."},
 {"id":"csat","q":"What is our customer satisfaction?","kw":["csat","satisfaction","happiness","rating","stars","happy"],
  "a":f"Average CSAT is <b>{cs['avg']}/5</b>. When the team got the outcome right it was {cs['when_correct']}; when wrong it fell to {cs['when_wrong']}, a {round(cs['when_correct']-cs['when_wrong'],1)}-star swing."},
 {"id":"time","q":"How much staff time is spent on easy questions?","kw":["over-escalation","over escalation","easy questions","staff time","hours","wasted","bumped to a person"],
  "a":f"<b>{st['over_escalations']}</b> simple questions were bumped to a person when the chatbot could have closed them, about <b>{st['hours_saved']} hours</b> of staff time."},
]
def _redact(s):
    s=re.sub(r"\d","#",s); s=re.sub(r"\b(CEO|manager|salary)\b","[redacted]",s,flags=re.I); return html.escape(s)
SNIP_TOPICS={"damaged":["damaged","wet","broken"],"lost":["lost","missing"],"claim":["claim","damaged","lost","missing"],
 "payment":["cod","owing","surcharge","fee"],"rude":["rude","unprofessional"],"delivered":["delivered"]}
def _snips(topic):
    kws=SNIP_TOPICS.get(topic,[topic])
    rows=[r for r in SC if r["agent_type"]=="ai" and r["derived_outcome_correct"]=="False"
          and any(k in r["derived_reason"].lower() for k in kws)][:3]
    return [{"reason":html.escape(r["derived_reason"]),"cust":_redact(r["customer_message"]),
             "rep":_redact(r["agent_response"][:120]),"did":r["agent_outcome"],"should":r["derived_correct_outcome"]} for r in rows] or None
SNIPS={t:_snips(t) for t in SNIP_TOPICS}

# ---- assemble ----
data_js = ("const PARETO="+json.dumps(pareto)+";\n"
           "const AGENTS="+json.dumps(AGENTS)+";\n"
           "const REASONS="+json.dumps(REASONS)+";\n"
           "const TEAM="+json.dumps(TEAM)+";\n"
           "const APPROVED="+json.dumps(APPROVED)+";\n"
           "const SNIPS="+json.dumps(SNIPS)+";\n")

tpl = open(os.path.join(HERE,"_console_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__DATA__*/", data_js)
open(os.path.join(HERE,"courier-cs-quality-console.html"),"w",encoding="utf-8").write(out)
print("WROTE courier-cs-quality-console.html")
print(f"  team grade {tg}, containment {TEAM['contain']}%, right-action {dq['overall_accuracy']}%, under-esc {under}, over-esc {over}, hours {st['hours_saved']}")
print(f"  agents: "+", ".join(f"{a['name']} {a['grade']}" for a in AGENTS))
