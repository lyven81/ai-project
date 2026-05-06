"""Bookshelf Orchestrator agent — wires Researcher → Judge (loop) → Content Builder.

Same pattern as Course Creator's orchestrator. The LoopAgent retries
research up to 3 times if the Judge fails. EscalationChecker breaks the
loop on Judge pass.
"""

import os
import json
import sys
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext

# Path setup so authenticated_httpx import works whether started from project
# root or from this directory.
sys.path.insert(0, os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import httpx as _httpx
from urllib.parse import urlparse as _urlparse

from shared.authenticated_httpx import create_authenticated_client as _create_authed


def create_authenticated_client(remote_service_url: str, **kwargs):
    """Use auth for Cloud Run, plain httpx for localhost (dev mode)."""
    host = _urlparse(remote_service_url).hostname or ""
    if host in ("localhost", "127.0.0.1", "0.0.0.0"):
        return _httpx.AsyncClient(follow_redirects=True, timeout=300.0)
    return _create_authed(remote_service_url, **kwargs)


def create_save_output_callback(key: str):
    """Saves the agent's final response into session state under `key`."""
    def callback(callback_context: CallbackContext, **kwargs) -> None:
        ctx = callback_context
        for event in reversed(ctx.session.events):
            if event.author == ctx.agent_name and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    if key == "judge_feedback" and text.strip().startswith("{"):
                        try:
                            ctx.state[key] = json.loads(text)
                        except json.JSONDecodeError:
                            ctx.state[key] = text
                    else:
                        ctx.state[key] = text
                    print(f"[{ctx.agent_name}] Saved output to state['{key}']")
                    return
    return callback


# --- Remote agents ---

researcher_url = os.environ.get(
    "RESEARCHER_AGENT_CARD_URL",
    "http://localhost:8001/a2a/agent/.well-known/agent-card.json",
)
researcher = RemoteA2aAgent(
    name="researcher",
    agent_card=researcher_url,
    description="Reads bookshelf sales data and computes structured metrics.",
    after_agent_callback=create_save_output_callback("research_findings"),
    httpx_client=create_authenticated_client(researcher_url),
)

judge_url = os.environ.get(
    "JUDGE_AGENT_CARD_URL",
    "http://localhost:8002/a2a/agent/.well-known/agent-card.json",
)
judge = RemoteA2aAgent(
    name="judge",
    agent_card=judge_url,
    description="Validates research findings for quality.",
    after_agent_callback=create_save_output_callback("judge_feedback"),
    httpx_client=create_authenticated_client(judge_url),
)

content_builder_url = os.environ.get(
    "CONTENT_BUILDER_AGENT_CARD_URL",
    "http://localhost:8003/a2a/agent/.well-known/agent-card.json",
)
content_builder = RemoteA2aAgent(
    name="content_builder",
    agent_card=content_builder_url,
    description="Writes the final decision brief from research findings.",
    httpx_client=create_authenticated_client(content_builder_url),
)


# --- Escalation checker ---

class EscalationChecker(BaseAgent):
    """Breaks the LoopAgent when the Judge returns status='pass'."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        feedback = ctx.session.state.get("judge_feedback")
        print(f"[EscalationChecker] Feedback: {feedback}")

        is_pass = False
        if isinstance(feedback, dict) and feedback.get("status") == "pass":
            is_pass = True
        elif isinstance(feedback, str) and '"status": "pass"' in feedback:
            is_pass = True

        if is_pass:
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)


escalation_checker = EscalationChecker(name="escalation_checker")


# --- Pipeline ---

research_loop = LoopAgent(
    name="research_loop",
    description="Iteratively researches and judges until quality standards are met.",
    sub_agents=[researcher, judge, escalation_checker],
    max_iterations=3,
)

root_agent = SequentialAgent(
    name="bookshelf_pipeline",
    description="Bookshelf decision-support pipeline: research → judge (loop) → write brief.",
    sub_agents=[research_loop, content_builder],
)
