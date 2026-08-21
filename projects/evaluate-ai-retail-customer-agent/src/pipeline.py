"""
The answering layer and the two graders.

Isolation is enforced by the function signatures, not by remembering to be
careful:

  run_prompt(question, version)  takes two strings. It cannot see a test case,
                                 so it cannot see expected_facts, assertions,
                                 in_scope, or anything else from the answer key.

  model_grade(response, question) takes two strings. It cannot see which prompt
                                 version produced the response, so it cannot
                                 favour "the improved one".

The code grader is the only function that touches a case object, and it runs
after the response already exists.
"""

import json
import re
import threading
import time

import config

# The Gemini free tier caps requests per minute. A burst of concurrent grader
# calls returns 429 RESOURCE_EXHAUSTED, which would otherwise be recorded as a
# missing verdict and silently deflate that judge's measured catch rate. Pace
# the calls instead, so a rate limit never masquerades as a judgement.
GEMINI_MIN_INTERVAL = 7.0
_gemini_lock = threading.Lock()
_gemini_last = [0.0]


def _gemini_pace():
    with _gemini_lock:
        wait = GEMINI_MIN_INTERVAL - (time.time() - _gemini_last[0])
        if wait > 0:
            time.sleep(wait)
        _gemini_last[0] = time.time()

# --- layer 2: answering -----------------------------------------------------


def run_prompt(question: str, version: str) -> str:
    """Answer one customer question. Sees the question and the policies. Nothing else."""
    assert isinstance(question, str), "run_prompt takes the question string, never a case object"
    assert version in ("v1", "v2")

    import anthropic

    client = anthropic.Anthropic(api_key=config.anthropic_key())
    prompt = config.prompt_template(version).format(
        policies=config.policies_text(), question=question
    )
    for attempt in range(3):
        try:
            r = client.messages.create(
                model=config.ANSWER_MODEL,
                max_tokens=1000,
                temperature=config.ANSWER_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(b.text for b in r.content if b.type == "text").strip()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


# --- layer 3a: the model grader ---------------------------------------------

GRADER_PROMPT = """You are auditing a customer service response for an online store.

The policy set below is the ONLY source of truth. Anything the response states that is not supported by these policies is an unsupported claim, even if it sounds reasonable or is common practice in retail.

Store policies:
{policies}

Customer question:
{question}

Assistant response:
{response}

Judge the response on four things:
- accuracy: are the facts it states consistent with the policies
- relevance: does it answer the question that was asked
- grounding: is every claim traceable to the policies
- helpfulness: is it clear and usable for the customer

List every unsupported claim separately, quoting or closely paraphrasing it.

A response that states a correct fact and then adds a requirement, step, condition or offer the policies do not contain IS unsupported. The correct part does not excuse the added part.

If the policies are silent on what the customer asked, a response that says so is correct. A response that asserts an answer anyway is unsupported, including a confident "no" that the policies never state."""

_FIELDS = {
    "grounded": ("boolean", "true only if every claim in the response is supported by the policies"),
    "unsupported_claims": ("array", "each claim in the response that the policies do not support"),
    "answers_the_question": ("boolean", "true if it addresses what was actually asked"),
    "accuracy": ("integer", "1 to 10"),
    "relevance": ("integer", "1 to 10"),
    "grounding": ("integer", "1 to 10"),
    "helpfulness": ("integer", "1 to 10"),
    "score": ("integer", "overall quality, 1 to 10"),
    "reasoning": ("string", "two sentences at most"),
}
_ORDER = list(_FIELDS)

_CLAUDE_SCHEMA = {
    "type": "object",
    "properties": {
        k: ({"type": "array", "items": {"type": "string"}, "description": d}
            if t == "array" else {"type": t, "description": d})
        for k, (t, d) in _FIELDS.items()
    },
    "required": _ORDER,
    "additionalProperties": False,
}

_GEMINI_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        k: ({"type": "ARRAY", "items": {"type": "STRING"}, "description": d}
            if t == "array" else {"type": t.upper(), "description": d})
        for k, (t, d) in _FIELDS.items()
    },
    "required": _ORDER,
    "propertyOrdering": _ORDER,
}


def _grade_claude(prompt_text: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=config.anthropic_key())
    r = client.messages.create(
        model=config.GRADER_CLAUDE,
        max_tokens=2000,
        tools=[{"name": "record_grade", "description": "Record the grade.",
                "input_schema": _CLAUDE_SCHEMA}],
        tool_choice={"type": "tool", "name": "record_grade"},
        messages=[{"role": "user", "content": prompt_text}],
    )
    return [b for b in r.content if b.type == "tool_use"][0].input


def _grade_gemini(prompt_text: str) -> dict:
    from google import genai
    from google.genai import types

    _gemini_pace()
    client = genai.Client(api_key=config.gemini_key())
    r = client.models.generate_content(
        model=config.GRADER_GEMINI,
        contents=prompt_text,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=_GEMINI_SCHEMA,
        ),
    )
    return json.loads(r.text)


def model_grade(response: str, question: str, provider: str) -> dict:
    """Grade one response. Blind: no version label, no case object, no answer key."""
    assert isinstance(response, str) and isinstance(question, str)
    text = GRADER_PROMPT.format(
        policies=config.grader_context(), question=question, response=response
    )
    fn = _grade_claude if provider == "claude" else _grade_gemini
    for attempt in range(5):
        try:
            g = fn(text)
            g["has_violation"] = (not g.get("grounded", True)) or bool(g.get("unsupported_claims"))
            g["provider"] = provider
            return g
        except Exception as e:
            if attempt == 4:
                # A verdict of None means "no verdict", never "no violation".
                # It is excluded from catch rate rather than counted as a miss.
                return {"provider": provider, "error": f"{type(e).__name__}: {e}",
                        "has_violation": None}
            # A per-minute quota needs a longer wait than a transient blip.
            rate_limited = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
            time.sleep((25 if rate_limited else 3) * (attempt + 1))


# --- layer 3b: the deterministic grader -------------------------------------


def code_grade(response: str, case: dict):
    """Run the case's assertions. No model, no opinion, same verdict every run."""
    if not case.get("assertions"):
        return None
    checks = []
    for a in case["assertions"]:
        hits = [p for p in a["patterns"] if re.search(p, response, re.IGNORECASE)]
        if a["type"] == "must_contain_any":
            ok = bool(hits)
        elif a["type"] == "must_not_contain_any":
            ok = not hits
        elif a["type"] == "must_contain_all":
            ok = len(hits) == len(a["patterns"])
        else:
            raise ValueError(f"unknown assertion type {a['type']}")
        checks.append({"label": a["label"], "type": a["type"], "passed": ok, "matched": hits})
    return {"passed": all(c["passed"] for c in checks),
            "power": case.get("power"), "checks": checks}
