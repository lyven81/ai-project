"""Bookshelf web app — thin HTTP/SSE client to the orchestrator service.

Mirrors course-creator/app/main.py. Does NOT import ADK. Talks to the
orchestrator at AGENT_SERVER_URL via /run_sse, streams progress events
and the final brief back to the browser.
"""

import json
import logging
import os
import sys
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from httpx_sse import aconnect_sse

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google.genai import types as genai_types
from pydantic import BaseModel

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from urllib.parse import urlparse as _urlparse

from shared.authenticated_httpx import create_authenticated_client as _create_authed


def create_authenticated_client(remote_service_url: str, **kwargs):
    """Use auth for Cloud Run, plain httpx for localhost (dev mode)."""
    host = _urlparse(remote_service_url).hostname or ""
    if host in ("localhost", "127.0.0.1", "0.0.0.0"):
        return httpx.AsyncClient(follow_redirects=True, timeout=300.0)
    return _create_authed(remote_service_url, **kwargs)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_name = os.getenv("AGENT_NAME", None)
agent_server_url = os.getenv("AGENT_SERVER_URL", "http://localhost:8004").rstrip("/")

clients: Dict[str, httpx.AsyncClient] = {}


async def get_client(origin: str) -> httpx.AsyncClient:
    if origin not in clients:
        clients[origin] = create_authenticated_client(origin)
    return clients[origin]


async def create_session(origin: str, agent: str, user_id: str) -> Dict[str, Any]:
    client = await get_client(origin)
    url = f"{origin}/apps/{agent}/users/{user_id}/sessions"
    resp = await client.post(url, headers=[("Content-Type", "application/json")])
    resp.raise_for_status()
    return resp.json()


async def get_session(origin: str, agent: str, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    client = await get_client(origin)
    url = f"{origin}/apps/{agent}/users/{user_id}/sessions/{session_id}"
    resp = await client.get(url, headers=[("Content-Type", "application/json")])
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


async def list_agents(origin: str) -> List[str]:
    client = await get_client(origin)
    url = f"{origin}/list-apps"
    resp = await client.get(url, headers=[("Content-Type", "application/json")])
    resp.raise_for_status()
    agents = resp.json()
    return agents or ["agent"]


async def query_agent(
    origin: str, agent: str, user_id: str, message: str, session_id: str
) -> AsyncGenerator[Dict[str, Any], None]:
    client = await get_client(origin)
    request = {
        "appName": agent,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {"role": "user", "parts": [{"text": message}]},
        "streaming": False,
    }
    async with aconnect_sse(client, "POST", f"{origin}/run_sse", json=request) as event_source:
        if event_source.response.is_error:
            yield {
                "author": agent,
                "content": {"parts": [{"text": f"Error {event_source.response.text}"}]},
            }
        else:
            async for server_event in event_source.aiter_sse():
                yield server_event.json()


class ChatRequest(BaseModel):
    message: str
    user_id: str = "local"
    session_id: Optional[str] = None


@app.post("/api/chat_stream")
async def chat_stream(req: ChatRequest):
    """Stream the orchestrator's response as ndjson lines."""
    global agent_name
    if not agent_name:
        agent_name = (await list_agents(agent_server_url))[0]

    session = None
    if req.session_id:
        session = await get_session(agent_server_url, agent_name, req.user_id, req.session_id)
    if session is None:
        session = await create_session(agent_server_url, agent_name, req.user_id)

    events = query_agent(agent_server_url, agent_name, req.user_id, req.message, session["id"])

    async def event_generator():
        final_text = ""
        seen_authors: set[str] = set()
        async for event in events:
            author = event.get("author") or "unknown"
            if author == "researcher" and author not in seen_authors:
                yield json.dumps({"type": "progress", "text": "🔍 Researcher reading your sales data..."}) + "\n"
                seen_authors.add(author)
            elif author == "judge" and author not in seen_authors:
                yield json.dumps({"type": "progress", "text": "⚖️ Judge checking data quality..."}) + "\n"
                seen_authors.add(author)
            elif author == "content_builder" and author not in seen_authors:
                yield json.dumps({"type": "progress", "text": "✍️ Writing your decision brief..."}) + "\n"
                seen_authors.add(author)

            if "content" in event and event["content"]:
                try:
                    content = genai_types.Content.model_validate(event["content"])
                    for part in (content.parts or []):
                        if part.text and author == "content_builder":
                            final_text += part.text
                except Exception as exc:
                    logger.warning(f"Failed to parse event content: {exc}")

        yield json.dumps({"type": "result", "text": final_text.strip()}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
