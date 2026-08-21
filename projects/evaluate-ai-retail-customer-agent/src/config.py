"""
Shared configuration: keys, models, and the frozen policy set.

Keys are read from where they already live on this machine. Nothing secret is
copied into the project folder, so no .env needs to be gitignored here.
"""

import hashlib
import io
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PROMPTS = ROOT / "prompts"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

# --- models -----------------------------------------------------------------
# The answering model is deliberately a small, cheap one: it is standing in for
# what an SME would actually deploy on a customer-service front line, and it is
# the behaviour under test. Using a frontier model here would answer nearly
# everything correctly and leave nothing to measure.
ANSWER_MODEL = "claude-haiku-4-5"
ANSWER_TEMPERATURE = 0  # deterministic answers, so a V1/V2 gap is not the dice

# The graders are the instrument, so they are the strong models. Two providers,
# because a single judge marking one model's work is a weak instrument and
# self-preference bias is real when the judge and the answerer share a family.
GRADER_CLAUDE = "claude-opus-5"  # temperature is not a parameter on this model
GRADER_GEMINI = "gemini-2.5-flash"

def _key(*names: str) -> str:
    """Read a key from the environment, falling back to a .env file.

    Looked up in order: the process environment, a .env beside the project, then
    ~/.env. Nothing secret is stored in this repository and no machine-specific
    path is hardcoded, so the code runs unchanged on someone else's machine.
    """
    for n in names:
        v = os.environ.get(n)
        if v:
            return v.strip()

    from dotenv import dotenv_values

    for path in (ROOT / ".env", Path.home() / ".env"):
        if path.exists():
            vals = dotenv_values(path)
            for n in names:
                if vals.get(n):
                    return vals[n].strip()

    raise RuntimeError(
        f"No API key found. Set one of {', '.join(names)} in the environment, "
        f"or put it in a .env file beside the project or at {Path.home() / '.env'}."
    )


def anthropic_key() -> str:
    return _key("ANTHROPIC_API_KEY")


def gemini_key() -> str:
    return _key("GEMINI_API_KEY", "GOOGLE_API_KEY")


# --- the frozen policy set --------------------------------------------------


def load_json(name: str):
    return json.load(io.open(DATA / name, encoding="utf-8"))


def policy_hash() -> str:
    """SHA-256 of the raw policy file.

    Logged into every results file. If two runs carry different hashes, the
    comparison between them is void: something other than the prompt moved.
    """
    raw = io.open(DATA / "happymart-policies.json", "rb").read()
    return hashlib.sha256(raw).hexdigest()[:16]


def policies_text() -> str:
    """The policy set rendered for a prompt. Identical for every prompt version."""
    doc = load_json("happymart-policies.json")
    lines = []
    for p in doc["policies"]:
        lines.append(f"- {p['rule']}")
    return "\n".join(lines)


STORE_NAME = "HappyMart"


def grader_context() -> str:
    """The policies as the GRADER sees them, plus the store's identity.

    The answering prompt names the store in its opening line, so using the name
    is authorised. The grader was given the eleven rules only, and on the first
    run it flagged three otherwise-correct answers for naming the store. That is
    a false positive in the instrument, not a fault in the answer.

    Used for grading only. The answering prompt is untouched, so the frozen
    responses remain valid and the policy hash is unchanged. The addition is
    symmetric: it applies to both arms and to both judges, and it removes flags
    from V1 rather than V2, so it reduces the measured improvement.
    """
    return (f"The store is called {STORE_NAME}. Referring to the store by name is "
            f"part of the assistant's role and is not a claim requiring policy "
            f"support. Everything else below is the complete policy set.\n\n"
            + policies_text())


def prompt_template(version: str) -> str:
    return io.open(PROMPTS / f"prompt_{version}.txt", encoding="utf-8").read()


# --- run safety -------------------------------------------------------------


def archive_existing(name: str):
    """Move an existing results file aside instead of overwriting it.

    A degraded re-run (rate limits, spent credits) must never silently replace a
    clean earlier result. Learned the hard way on 2026-08-21.
    """
    target = RESULTS / name
    if not target.exists():
        return
    import datetime
    import shutil

    archive = RESULTS / "archive"
    archive.mkdir(exist_ok=True)
    stamp = datetime.datetime.fromtimestamp(target.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
    shutil.move(str(target), str(archive / f"{target.stem}_{stamp}{target.suffix}"))
    print(f"archived previous {name} -> results/archive/{target.stem}_{stamp}{target.suffix}")


def preflight(providers=("anthropic", "gemini")) -> bool:
    """One cheap call per provider before spending a full run.

    Credit exhaustion and quota limits look like grader disagreement in the
    output if you let a run proceed into them. Fail fast and say which provider
    is down and why.
    """
    ok = True
    if "anthropic" in providers:
        ok = _preflight_anthropic() and ok
    if "gemini" in providers:
        ok = _preflight_gemini() and ok
    return ok


def _preflight_anthropic() -> bool:
    try:
        import anthropic

        anthropic.Anthropic(api_key=anthropic_key()).messages.create(
            model=ANSWER_MODEL, max_tokens=4,
            messages=[{"role": "user", "content": "hi"}])
        print("preflight anthropic: OK")
    except Exception as e:
        msg = str(e)
        why = ("credit balance exhausted" if "credit balance" in msg
               else "rate limited" if "429" in msg else msg[:140])
        print(f"preflight anthropic: FAIL ({why})")
        return False
    return True


def _preflight_gemini() -> bool:
    try:
        from google import genai

        # Keep a reference: an inline client is collected mid-call and the SDK
        # then reports "client has been closed" instead of the real error.
        gclient = genai.Client(api_key=gemini_key())
        gclient.models.generate_content(model=GRADER_GEMINI, contents="hi")
        print("preflight gemini: OK")
    except Exception as e:
        msg = str(e)
        why = ("free-tier quota exhausted" if "RESOURCE_EXHAUSTED" in msg else msg[:140])
        print(f"preflight gemini: FAIL ({why})")
        return False
    return True
