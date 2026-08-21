"""
The multi-turn loop, streaming, with two providers.

This is the course pattern from the lecture notes, applied:

  send the message list with the schemas
  append the WHOLE content list, tool_use blocks included
  run every requested tool
  return one tool_result per request, ids matched
  repeat until stop_reason stops being "tool_use"

Two things this build adds over the notes.

Streaming. A chat interface means the assistant message has to be rebuilt into
plain dicts before it goes back into history, because streamed blocks are not
reusable as they arrive.

Bring your own key. The visitor supplies a Claude key with each request. It is
used for that request and never written down: not to disk, not to a log, not
into an error message. Nothing on the server holds it between calls, which is
also why the operator is not paying for a stranger's tokens.

The departure board needs no key at all. Only the chat does.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

import config as C
import forecast as F
import tools as T

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Keys: environment, then a project .env, then the home .env. Nothing
# machine-specific ships and nothing secret sits inside the project folder.
# ---------------------------------------------------------------------------

def _redact(text: str) -> str:
    """Never let a key fragment ride out in an error message."""
    out = []
    for word in str(text).split():
        out.append("[redacted]" if word.startswith("sk-ant") or len(word) > 60 else word)
    return " ".join(out)


_SYSTEM_BODY = f"""You are the scheduling assistant for a one-boat tour operator at the \
Kuala Sepetang jetty in Perak, Malaysia.

The boat runs six fixed two-hour departures a day: 09:00, 11:00, 13:00, 15:00, \
17:00 and 19:00. Twelve seats. One hull, so a lost departure is a lost fare and \
there is no second boat to fall back on.

How to work:

- Always call a tool before answering anything about conditions, a departure, or \
a booking. Never answer weather from memory.
- get_boat_conditions is the only source of forecast data. Web search is for what \
it cannot supply: public holidays, school breaks, official advisories, jetty or \
road closures, festival dates that drive demand.
- Pass a date and a time for one departure, a date alone for the whole day, a date \
and an end_date to look across several days. You do not have to turn a customer's \
time into a departure yourself: pass what they asked for, and when the reply \
carries time_resolved, quote the departure time it names rather than the time the \
customer said.
- When a departure cannot run and has passengers, the reply carries a relocation. \
Read it rather than working one out. It has already checked the seats and refuses \
any departure that cannot take the whole party.
- A party moves together or not at all. Only raise a split when the relocation \
says whole_party is false, and then offer it rather than book it.

The reply the operator sends:

- Whenever the operator asks what to tell a customer, or a booked party is \
affected by a change, DRAFT THE MESSAGE and save it with the text editor. Do not \
stop at advice about what to say. Pass the file name on its own with no folder \
in front of it, in the form reply_YYYY-MM-DD_who.md, for example \
reply_2026-08-23_tan_family.md. The editor writes to one folder and supplies the \
rest of the path itself. Then tell the operator it is saved and ready to send.
- The draft is written to the CUSTOMER, not to the operator. Different reader, \
different language. No ratings, no thresholds, no millimetres, no gust figures, \
no confidence tiers, no jargon. "Showers on and off with a gusty wind" is what a \
tourist can use; "0.25 mm/h, gusts 30 km/h, marginal" is not.
- Say what is happening, why it affects their trip, what you are offering \
instead, and what happens if that does not suit them. Warm, short, apologetic \
where an apology is owed, and never grovelling.
- Never tell a customer a trip is safe, and never promise weather. Say what you \
expect and say you will check again closer to the time.
- Write it as plain text a person can paste into WhatsApp. No headings, no bold, \
no bullet characters, no markdown. Sign off as Kuala Sepetang Tour Boat, so the \
operator does not have to add it.
- The operator sends it. You draft it. Nothing goes out on its own.

How to speak:

- Plain English, short sentences. The reader is a boat operator at a jetty, often \
on a phone, often in a hurry.
- Lead with the decision, then the reason. Quote the actual numbers.
- Say "workable" or "not workable against your thresholds". Never say a departure \
is safe. {C.DISCLAIMER}
- When a tool says rain timing is not reliable at that lead time, say so rather \
than describing timing you cannot back up.
- Never invent a seat count, a booking or a slot. If a tool did not return it, \
say you do not have it.
- Never use a dash as punctuation. No em-dash, no en-dash. Use a comma, a colon,
a semicolon, brackets, or split into two sentences."""


def system_prompt() -> str:
    """
    The system prompt, with today's date stamped on the front.

    Built per request rather than at import. The server can stay up for days,
    and a date baked in at startup is a date that goes quietly wrong at
    midnight, which is the exact failure this step exists to close.

    The date is here AND in a tool on purpose. The prompt stops the model
    reaching for a remembered date on an easy question; the tool is what it
    checks against on a hard one, and what it can call again mid-conversation.
    """
    today = T.datetime.now(T.MYT).date()
    horizon = today + T.timedelta(days=F.MAX_LEAD_DAYS)
    return (
        f"Today is {today.strftime('%A %d %B %Y')} ({today.isoformat()}) at the "
        f"jetty, timezone {C.LOCATION['timezone']}. The forecast reaches "
        f"{horizon.isoformat()}.\n\n"
        f"Work every relative date out from that. When a question says today, "
        f"tonight, tomorrow, this Sunday, the weekend or in three days, call "
        f"get_current_datetime and read the exact date out of its `upcoming` map "
        f"rather than counting it yourself. State the date you settled on in your "
        f"reply, so the operator can catch it if it is wrong. A date earlier than "
        f"today is history and cannot be used to plan a departure.\n\n"
        + _SYSTEM_BODY
    )


# ---------------------------------------------------------------------------
# Tool execution, shared by both providers
# ---------------------------------------------------------------------------

def run_tools(blocks: list[dict], session: str = "demo") -> list[dict]:
    """One tool_result per tool_use block. Errors come back as results with
    is_error set, never as exceptions, so the model can correct itself."""
    out = []
    for b in blocks:
        try:
            result = T.run_tool(b["name"], b["input"], session)
            out.append({
                "type": "tool_result", "tool_use_id": b["id"],
                "content": json.dumps(result, default=str), "is_error": False,
            })
        except Exception as exc:                       # noqa: BLE001
            out.append({
                "type": "tool_result", "tool_use_id": b["id"],
                "content": f"Error: {exc}", "is_error": True,
            })
    return out


def _rebuild(message) -> list[dict]:
    """Streamed blocks are not reusable as they arrive, so copy them into plain
    dicts before they go back into history."""
    content = []
    for block in message.content:
        if block.type == "text":
            content.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            content.append({"type": "tool_use", "id": block.id,
                            "name": block.name, "input": block.input})
        elif block.type == "server_tool_use":
            content.append({"type": "server_tool_use", "id": block.id,
                            "name": block.name, "input": block.input})
        elif block.type == "web_search_tool_result":
            content.append({"type": "web_search_tool_result",
                            "tool_use_id": block.tool_use_id,
                            "content": block.content})
    return content


# ---------------------------------------------------------------------------
# Claude, streaming
# ---------------------------------------------------------------------------

MAX_ROUNDS = 8


def stream_claude(messages: list[dict], api_key: str, session: str = "demo",
                  model: str = "claude-sonnet-4-5"):
    """Yields events for the UI, and mutates `messages` into the full history."""
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)

    for _ in range(MAX_ROUNDS):
        with client.messages.stream(
            model=model, max_tokens=2000, system=system_prompt(),
            messages=messages, tools=T.ALL_SCHEMAS,
        ) as stream:
            for chunk in stream:
                if chunk.type == "text":
                    yield {"type": "text", "text": chunk.text}
                elif chunk.type == "content_block_start":
                    cb = chunk.content_block
                    if cb.type in ("tool_use", "server_tool_use"):
                        yield {"type": "tool", "name": cb.name}
            final = stream.get_final_message()

            # What it actually asked for, not just which tool. A name alone
            # cannot tell you whether it looked up the right date.
            for b in final.content:
                if b.type in ("tool_use", "server_tool_use"):
                    yield {"type": "tool_input", "name": b.name, "input": b.input}

        messages.append({"role": "assistant", "content": _rebuild(final)})

        if final.stop_reason != "tool_use":
            yield {"type": "done", "stop_reason": final.stop_reason}
            return

        requests = [b for b in messages[-1]["content"] if b["type"] == "tool_use"]
        results = run_tools(requests, session)
        for r in results:
            if r["is_error"]:
                yield {"type": "tool_error", "detail": r["content"][:180]}
        messages.append({"role": "user", "content": results})

    yield {"type": "done", "stop_reason": "max_rounds",
           "note": f"Stopped after {MAX_ROUNDS} rounds of tool calls."}


def stream(messages: list[dict], api_key: str, session: str = "demo"):
    """
    A visitor's own key if they gave one, the server's key otherwise.

    The visitor's key is preferred rather than merely allowed. Someone who
    brings their own spends their own tokens, which is the right default for
    anyone technical enough to have a key. Everyone else gets to use the thing
    without being asked for credentials, and the demo is worth more open than
    it is thrifty.

    Neither key is ever written down: not to disk, not to a log, not into an
    error message. The rate limit on the endpoint is what keeps the server key
    from being anyone's free API.
    """
    key = (api_key or "").strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        yield {"type": "needs_key",
               "detail": "The assistant is not configured with a key on this "
                         "server. Add your own Anthropic API key below to use it. "
                         "The departure board works without one."}
        yield {"type": "done", "stop_reason": "no_key"}
        return
    try:
        yield from stream_claude(messages, key, session)
    except Exception as exc:                            # noqa: BLE001
        yield {"type": "error", "detail": _redact(exc)[:300]}
        yield {"type": "done", "stop_reason": "error"}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or (
        "Plan Monday 24 August. I have twelve booked at 15:00. "
        "If that cannot run, where do they go?"
    )
    print(f"> {q}\n")
    import os
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        for line in open(Path.home() / ".env", encoding="utf-8"):
            if line.startswith("ANTHROPIC_API_KEY="):
                key = line.split("=", 1)[1].strip()
    msgs = [{"role": "user", "content": q}]
    for ev in stream(msgs, key):
        if ev["type"] == "text":
            print(ev["text"], end="", flush=True)
        elif ev["type"] == "tool":
            print(f"\n  [tool: {ev['name']}]", flush=True)
        elif ev["type"] == "tool_error":
            print(f"\n  [tool error: {ev['detail']}]", flush=True)
        elif ev["type"] == "provider_fallback":
            print(f"\n  [{ev['detail']}]", flush=True)
        elif ev["type"] == "done":
            print(f"\n\n[done: {ev['stop_reason']}]")
