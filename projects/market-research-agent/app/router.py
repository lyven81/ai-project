"""
router.py — maps a free-text question to ONE of the 10 approved query ids.

Deterministic keyword routing (zero cost, no model call) covers the known questions.
For genuinely open phrasings you can swap in a cheap-model classifier; the hook is
documented in route_with_llm() but disabled by default to keep cost at zero.
"""
import re

ROUTES = [
    (1,  ["foot traffic","busiest","time of day","daypart","when","evening","supper","night","footfall"]),
    (2,  ["resident","profile","target customer","demographic","who lives","population","age","chinese"]),
    (3,  ["underserved","gap","few shops","opportunity","white space","traffic but few"]),
    (4,  ["how many","saturated","saturation","crowded","competitors in"]),
    (5,  ["price range","how much","charge","pricing","cost","a bowl"]),
    (6,  ["price point","price gap","no competitor","unoccupied","positioning price"]),
    (7,  ["revenue","expect","forecast","projection","how much can i make","sales next"]),
    (8,  ["sells best","bestseller","best seller","growing","declining","dessert","menu","product"]),
    (9,  ["complain","complaint","review","dislike","unhappy","bad about","too sweet"]),
    (10, ["should i launch","should i open","go or no","worth it","good idea","launch in"]),
]

def route(text: str):
    t = text.lower()
    best, score = None, 0
    for qid, kws in ROUTES:
        s = sum(len(k.split()) for k in kws if k in t)
        if s > score:
            score, best = s, qid
    return best if score > 0 else None

def route_with_llm(text: str):
    """Optional cheap-model fallback. Disabled by default (returns keyword route).
    To enable: call Gemini Flash / Claude Haiku with the 10 titles and ask for the id.
    """
    return route(text)
