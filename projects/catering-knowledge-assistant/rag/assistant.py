"""
Stages 6 and 7 of the pipeline: route, generate, cite.

Routing decides whether a question is answered from the document corpus
(knowledge: policies, menus, terms) or from the database (records: balances,
cycle dates, delivery counts). Sending a record question to vector search
produces a fluent wrong answer, which is the failure mode this layer exists to
prevent.

Generation is grounded: the model sees only the retrieved chunks or the tool
result, is told to answer from them alone, and must cite the doc_id it used.
When retrieval returns nothing above the relevance floor, the assistant
refuses rather than guessing.
"""

import json
import re
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from .config import GEN_MODEL, ROUTER_MODEL, BUSINESS_NAME, load_api_key
from .ratelimit import with_retry
from .retriever import retrieve, build_filter
from .tools import TOOL_SPECS, call_tool, SIM_TODAY

_client = None


def client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=load_api_key())
    return _client


ROUTER_PROMPT = f"""You route customer and staff questions for {BUSINESS_NAME},
a weekday meal delivery service.

Choose ONE route.

Route "corpus" for general knowledge questions answered by published documents:
policies, delivery areas and times, subscription terms, payment and refunds,
prices in general, what is on the menu, dietary questions, contact details.

Route "tool" ONLY when the question needs a specific record or a calculation
over stored data. Available tools:
{json.dumps(TOOL_SPECS, indent=2)}

Today's date is {SIM_TODAY.isoformat()}.

Rules:
- A question about a named customer's balance, cycle or plan is "tool".
- A question about how many meals to cook on a date is "tool".
- "What is served on <specific date>" is "tool", because dates resolve through
  the rotation. "What is on the menu this week" in general is "corpus".
- "Which dishes contain <protein>" is "tool".
- Anything about rules, terms, policy, areas, times or prices is "corpus".
- If unsure, choose "corpus".

Return JSON only."""

ROUTER_SCHEMA = {
    "type": "object",
    "properties": {
        "route": {"type": "string", "enum": ["corpus", "tool"]},
        "tool_name": {"type": "string"},
        "tool_args": {"type": "object",
                      "properties": {
                          "customer": {"type": "string"},
                          "order_date": {"type": "string"},
                          "service": {"type": "string"},
                          "protein": {"type": "string"},
                      }},
        "reason": {"type": "string"},
    },
    "required": ["route", "reason"],
}

ANSWER_PROMPT = f"""You are the knowledge assistant for {BUSINESS_NAME}, a
weekday meal delivery service in Shah Alam and Kota Kemuning, Malaysia.

Answer ONLY from the SOURCES below. Do not use outside knowledge and do not
invent details such as prices, dates, areas or phone numbers.

Rules:
- If the sources do not contain the answer, say you do not have that
  information and suggest contacting the business. Do not guess.
- If sources disagree, prefer a source marked authority=override, then
  authority=primary, then authority=secondary. A holiday notice overrides the
  normal schedule.
- Prices can differ by plan. If the question does not say which plan, give both
  the daily and the monthly price and explain the difference briefly.
- Be direct and concise. Two to five sentences unless a list is clearer.
- Do not use em dashes.
- End with a line "SOURCES: " followed by the doc_id values you actually used,
  comma separated.

Today's date is {SIM_TODAY.isoformat()}."""


@dataclass
class Answer:
    question: str
    route: str
    text: str
    citations: list = field(default_factory=list)
    chunk_ids: list = field(default_factory=list)
    doc_ids: list = field(default_factory=list)
    tool_name: str = ""
    tool_result: dict = field(default_factory=dict)
    refused: bool = False
    router_reason: str = ""


def route(question):
    resp = with_retry(lambda: client().models.generate_content(
        model=ROUTER_MODEL,
        contents=f"Question: {question}",
        config=types.GenerateContentConfig(
            system_instruction=ROUTER_PROMPT,
            response_mime_type="application/json",
            response_schema=ROUTER_SCHEMA,
            temperature=0,
        ),
    ), ROUTER_MODEL)
    try:
        return json.loads(resp.text)
    except Exception:
        return {"route": "corpus", "reason": "router parse failure, defaulted"}


def _format_sources(hits):
    blocks = []
    for h in hits:
        blocks.append(
            f"[doc_id: {h.doc_id} | chunk: {h.chunk_id} | "
            f"authority: {h.authority}]\n{h.text}")
    return "\n\n---\n\n".join(blocks)


def _extract_citations(text):
    m = re.search(r"SOURCES:\s*(.+?)\s*$", text, re.S | re.I)
    if not m:
        return text.strip(), []
    cited = [c.strip() for c in re.split(r"[,\n]", m.group(1)) if c.strip()]
    body = text[:m.start()].strip()
    return body, cited


def answer_from_corpus(question, k_final=4, qfilter=None):
    hits = retrieve(question, k_final=k_final, qfilter=qfilter)
    if not hits:
        return Answer(
            question=question, route="corpus",
            text=("I do not have that information in our published documents. "
                  "Please contact us on 012-345 6789, 9am to 5pm on weekdays."),
            refused=True)

    resp = with_retry(lambda: client().models.generate_content(
        model=GEN_MODEL,
        contents=f"SOURCES:\n\n{_format_sources(hits)}\n\nQUESTION: {question}",
        config=types.GenerateContentConfig(
            system_instruction=ANSWER_PROMPT, temperature=0.1),
    ), GEN_MODEL)
    body, cited = _extract_citations(resp.text or "")
    refused = bool(re.search(
        r"do not have that information|don't have that information", body, re.I))
    return Answer(question=question, route="corpus", text=body,
                  citations=cited,
                  chunk_ids=[h.chunk_id for h in hits],
                  doc_ids=sorted({h.doc_id for h in hits}),
                  refused=refused)


def answer_from_tool(question, tool_name, tool_args):
    try:
        result = call_tool(tool_name, tool_args or {})
    except (LookupError, ValueError, TypeError, KeyError) as e:
        return Answer(question=question, route="tool", tool_name=tool_name,
                      text=f"I could not look that up. {e}", refused=True)

    resp = with_retry(lambda: client().models.generate_content(
        model=GEN_MODEL,
        contents=(f"TOOL RESULT from {tool_name}:\n"
                  f"{json.dumps(result, ensure_ascii=False, indent=2)}\n\n"
                  f"QUESTION: {question}"),
        config=types.GenerateContentConfig(
            system_instruction=ANSWER_PROMPT, temperature=0.1),
    ), GEN_MODEL)
    body, _ = _extract_citations(resp.text or "")
    # The source on the tool route is known deterministically, so it is set
    # here rather than trusted from the model's SOURCES line.
    return Answer(question=question, route="tool", text=body,
                  citations=[f"database:{tool_name}"],
                  tool_name=tool_name, tool_result=result,
                  doc_ids=[f"database:{tool_name}"])


def ask(question, verbose=False):
    decision = route(question)
    if decision.get("route") == "tool" and decision.get("tool_name"):
        a = answer_from_tool(question, decision["tool_name"],
                             decision.get("tool_args") or {})
    else:
        a = answer_from_corpus(question)
    a.router_reason = decision.get("reason", "")
    if verbose:
        print(f"[route: {a.route}"
              + (f" -> {a.tool_name}" if a.tool_name else "")
              + f"] {a.router_reason}")
    return a


def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    questions = [
        "Do you deliver to Puchong?",
        "Do you deliver on 31 August?",
        "How much is the claypot chicken on Thursday?",
        "Do you have halal food?",
        "Can I pause my subscription?",
        "How much is brown rice?",
        "What is served on 1 September 2026?",
        "Which dishes have beef?",
        "How many meals does Kok W.K. have left?",
        "How many meals do we need to cook on 27 August?",
        "What is your bank account number?",
    ]
    for q in questions:
        a = ask(q)
        print("=" * 74)
        print(f"Q: {q}")
        print(f"   route: {a.route}" + (f" -> {a.tool_name}" if a.tool_name else "")
              + (f"   [REFUSED]" if a.refused else ""))
        print(f"A: {a.text}")
        print(f"   cited: {', '.join(a.citations) if a.citations else '(none)'}")
        print()


if __name__ == "__main__":
    main()
