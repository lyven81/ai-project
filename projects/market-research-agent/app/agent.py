"""
agent.py — orchestration: route a question -> run the approved query -> phrase the answer.

This is the no-ADK equivalent of the codelab's LlmAgent. The "agent" never writes SQL
and never calls Maps live; it only selects one of the 10 governed tools in queries.py,
then turns the returned rows into a short business answer.
"""
import queries as Q
from router import route

# known Klang Valley areas -> zip, for light parameter extraction
AREA_ZIP = {
    "ss2": "47300", "petaling jaya": "47300", "cheras": "56000", "kepong": "52100",
    "setapak": "53000", "pudu": "55100", "old klang road": "58100",
    "bangsar": "59100", "shah alam": "40000", "seksyen 13": "40000",
}

def _zip_from(text, default):
    t = text.lower()
    for name, z in AREA_ZIP.items():
        if name in t:
            return z, name.title()
    return default, None

def answer(question: str) -> dict:
    qid = route(question)
    if qid is None:
        return {"id": None, "cost": "out_of_scope",
                "answer": ("That sits outside the 10 questions I am set up to answer for "
                           "this pack, so I will not guess at it. I can help with foot "
                           "traffic, resident profile, saturation, pricing and price gaps, "
                           "revenue and bestsellers, competitor complaints, and a final "
                           "go / no-go on an area.")}
    fn, title, src, cost = Q.REGISTRY[qid]

    # light, whitelisted parameter extraction for the area-specific queries
    if qid == 4:
        z, _ = _zip_from(question, Q.SS2); data = Q.q4_saturation(zip_code=z)
    elif qid == 10:
        z, _ = _zip_from(question, Q.KEPONG); data = Q.q10_launch_decision(zip_code=z)
    else:
        data = fn()

    return {"id": qid, "title": title, "source": src, "cost": cost,
            "data": data, "answer": phrase(qid, data)}

# ---- templated phrasing (turns rows into a sentence; no model needed) ----
def phrase(qid, d):
    if qid == 1:
        top = d[0]
        return (f"{top['neighborhood']} has the strongest pull, peaking in the "
                f"{top['time_of_day']} (score {top['foot_traffic_score']}). Tong shui is "
                f"an evening business here, so staff and stock for the supper rush.")
    if qid == 2:
        a, b = d[0], d[1]
        return (f"{a['neighborhood']} fits best (score {a['fit_score']}), then "
                f"{b['neighborhood']} ({b['fit_score']}): both are large, Chinese-dense "
                f"({a['chinese_population_pct']}% / {b['chinese_population_pct']}%) family areas.")
    if qid == 3:
        t = d[0]
        return (f"{t['neighborhood']} is the standout opportunity: strong evening traffic "
                f"({t['evening_traffic']}) with only {t['shop_count']} tong shui shops mapped, "
                f"the best demand-to-competition ratio in the pack.")
    if qid == 4:
        r = d[0]
        verdict = "well served" if r["shop_count"] >= 10 else "still open"
        return (f"{r['shop_count']} tong shui shops are mapped here (avg rating "
                f"{r['avg_rating']}). That reads as {verdict}.")
    if qid == 5:
        r = d[0]
        return (f"Competitors run from RM{r['low']} to RM{r['high']}, averaging "
                f"RM{r['avg']} across {r['n']} priced items. Most volume sits near the average.")
    if qid == 6:
        return (f"The RM{d['gap_low']:.2f} to RM{d['gap_high']:.2f} band is thinly served "
                f"({d['gap_count']} competitors). Room for a quality, less-sweet bowl there.")
    if qid == 7:
        return (f"Projecting the recent trend forward gives about RM{d['projection']:,.0f} "
                f"for the next {d['weeks_ahead']} weeks (recent weekly average "
                f"RM{d['recent_weekly_avg']:,.0f}). Straight-line, before seasonal swing.")
    if qid == 8:
        top = d[0]
        decl = sorted(d, key=lambda r: r["growth_pct"])[0]
        return (f"{top['product_type'].title()} leads on revenue (RM{top['total_rev']:,.0f}, "
                f"{top['growth_pct']:+.1f}%). {decl['product_type'].title()} is slipping "
                f"({decl['growth_pct']:+.1f}%). Lead with the growth items.")
    if qid == 9:
        names = ", ".join(f"{r['theme']} ({r['mentions']})" for r in d)
        return (f"Top competitor complaints: {names}. Each is a concrete thing to design "
                f"around: a controlled recipe, a fast supper queue, and a seating/parking plan.")
    if qid == 10:
        a = d["area"]; sat = d["saturation"]; prod = d["top_product"]
        comp = d["top_complaint"]; gap = d["price_gap"]
        return (f"{a['neighborhood']}: evening traffic {d['evening_traffic']}, Chinese-dense "
                f"({a['chinese_population_pct']}%), and only {sat['shop_count']} shops mapped "
                f"(low competition). The opening that fits the data: enter the open "
                f"RM{gap['gap_low']:.2f}-{gap['gap_high']:.2f} band, lead with "
                f"{prod['product_type']}, and win on the top complaint "
                f"('{comp['theme']}') with a controlled, consistent recipe.")
    return "No phrasing available."

if __name__ == "__main__":
    for qn in ["which area is busiest and when?",
               "is ss2 saturated?",
               "should i launch in kepong?",
               "what do customers complain about?",
               "what is the meaning of life?"]:
        r = answer(qn)
        print(f"\nQ: {qn}\n -> [Q{r['id']} · {r.get('cost')}] {r['answer']}")
