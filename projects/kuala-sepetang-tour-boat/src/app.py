"""
The live app: FastAPI serving the departure board and the streaming chat.

Three endpoints and one static page.

  GET  /api/board?start=&days=   the five-day board, straight from the engine
                                 no key needed, this is the whole product for
                                 anyone who just wants to look
  GET  /api/replies              the customer messages the assistant has drafted
  POST /api/chat                 the multi-turn loop, streamed as SSE
  GET  /                         the page

Nothing here recomputes weather. The board endpoint calls the same brain the
gates were run against, so what the screen shows is what was proven.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

import agent
import brain as B
import config as C
import forecast as F
import rebooking as R
import tools as T

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
REPLIES = ROOT / "data" / "replies"

app = FastAPI(title="Kuala Sepetang Tour Boat", version="1.0")


# ---------------------------------------------------------------------------

def build_board(start: date, ndays: int) -> dict:
    bookings = R.load_bookings(start)
    raw = F.get_days(start, ndays)          # one request for the whole board
    plan = R.plan(raw, bookings)
    board = R.build_board(raw, bookings)
    by_party = {r["party"]["id"]: r for r in plan["results"]}

    days = []
    for day in raw:
        c = B.compare_slots(day)
        gmax = 0
        slots = []
        for s in C.SLOTS:
            v = next(x for x in c["slots"] if x["slot"] == s["id"])
            w = F.slice_window(day, s["start"], s["end"])
            cell = board[(c["date"], s["id"])]
            gmax = max(gmax, v["comfort"]["max_gust_kmh"])
            slots.append({
                "id": v["slot"], "start": s["start"], "end": s["end"],
                "rating": v["rating"], "adjusted": v["rating_adjusted"],
                "shape": v["shape"]["shape"], "detail": v["shape"]["detail"],
                "shape_reliable": v["shape_reliable"], "shape_caveat": v["shape_caveat"],
                "contingency": v["shape"]["contingency"],
                "buckets": [round(r or 0, 2) for r in (w.get("rain") or [])],
                "gust": v["comfort"]["max_gust_kmh"],
                "mmph": v["comfort"]["rain_mm_per_hour"],
                "prob": v["comfort"]["max_rain_probability_pct"],
                "vis": round((v["comfort"]["min_visibility_m"] or 0) / 1000, 1),
                "hazard": {"stop": v["hazard"]["stop"], "reasons": v["hazard"]["reasons"],
                           "watch": v["hazard"]["watch"]},
                "approach": v["approach"]["note"],
                "seats": cell["taken"], "cap": cell["cap"], "free": cell["free"],
                "parties": [{"id": p["id"], "name": p["name"], "size": p["size"],
                             "activity": p["activity"], "plan": by_party.get(p["id"])}
                            for p in cell["parties"]],
                "acts": [{"n": a["name"], "r": a["rating"], "notes": a["notes"]}
                         for a in B.activities_for_slot(day, s["id"])[:3]],
            })
        days.append({
            "date": c["date"], "lead": c["lead_days"], "summary": c["summary"],
            "conf": c["confidence"], "sunrise": c["sunrise"][11:],
            "sunset": c["sunset"][11:], "moon": c["moon"], "gmax": gmax, "slots": slots,
        })
    return {"days": days, "plan": plan,
            "measured": {"confidence_measured": C.CONFIDENCE_MEASURED,
                         "source": getattr(C, "MEASUREMENT_SOURCE", None)}}


# The board is free to serve but not free to fetch: Open-Meteo's open tier is
# 10,000 calls a day and the cache does not survive an instance recycling. A
# plain per-address cap keeps one impatient visitor from spending the quota.
_HITS: dict[str, list[float]] = {}
RATE_PER_MINUTE = 20


def _rate_limit(request: Request) -> None:
    import time
    who = (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
           or (request.client.host if request.client else "unknown"))
    now = time.time()
    recent = [t for t in _HITS.get(who, []) if now - t < 60]
    if len(recent) >= RATE_PER_MINUTE:
        raise HTTPException(429, "Too many requests. Wait a minute and try again.")
    recent.append(now)
    _HITS[who] = recent
    if len(_HITS) > 5000:
        _HITS.clear()


@app.get("/api/board")
def api_board(request: Request, start: str | None = None, days: int = 5):
    _rate_limit(request)
    try:
        d = F.parse_date(start) if start else date.today()
        return build_board(d, max(1, min(days, 10)))
    except F.ForecastError as e:
        raise HTTPException(400, str(e))


@app.get("/api/replies")
def api_replies(session: str = "demo"):
    """The customer messages the assistant has drafted, newest first.

    There is no server-side template here on purpose. A reply is written by the
    assistant for one customer and one situation; a generated one would be a
    form letter, which is the thing the operator can already write faster than
    they can edit."""
    folder = REPLIES / T._safe_session(session)
    folder.mkdir(parents=True, exist_ok=True)
    files = sorted(
        (f for f in folder.iterdir() if f.is_file() and not f.name.startswith(".")),
        key=lambda f: f.stat().st_mtime, reverse=True,
    )
    out = [{"file": f.name, "updated": int(f.stat().st_mtime),
            "content": f.read_text(encoding="utf-8", errors="replace")} for f in files[:20]]
    return {"count": len(out), "latest": out[0] if out else None, "replies": out}


class Turn(BaseModel):
    messages: list
    # Bring your own key. Used for this request and never stored: not written
    # to disk, not logged, not echoed back. The board works without one.
    api_key: str = ""
    session: str = "demo"


@app.post("/api/chat")
def api_chat(request: Request, turn: Turn):
    """Server-sent events. Each line is one event from the loop, so the page
    can show tool chips as they fire rather than after the answer lands."""
    _rate_limit(request)

    def gen():
        try:
            for ev in agent.stream(turn.messages, turn.api_key, turn.session):
                yield "data: " + json.dumps(ev) + "\n\n"
        except Exception as exc:                        # noqa: BLE001
            safe = {"type": "error", "detail": agent._redact(exc)[:300]}
            yield "data: " + json.dumps(safe) + "\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


@app.get("/api/health")
def health():
    return {"ok": True, "location": C.LOCATION["name"],
            "slots": len(C.SLOTS), "activities": len(C.ACTIVITIES),
            "confidence_measured": C.CONFIDENCE_MEASURED,
            "auth": "server key, visitor key preferred when supplied",
            "board_needs_key": False,
            "chat_needs_key": not bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
            "key_persisted": False}


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
