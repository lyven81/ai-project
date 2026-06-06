"""
main.py — FastAPI app (the Cloud Run service).

Endpoints:
  GET  /            -> serves the chat UI (market-research-agent.html)
  POST /ask         -> {"question": "..."} -> routed answer from the 10 governed tools
  GET  /healthz     -> liveness probe

Run locally:
    uvicorn app.main:app --reload --port 8080
Then open http://127.0.0.1:8080
"""
import os, sys
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import answer  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI = os.path.join(ROOT, "market-research-agent.html")

app = FastAPI(title="Market Research Agent", version="1.0")

# Allow the static page (GitHub Pages / file) to call /ask cross-origin.
# Tighten allow_origins to your Pages domain in production if you prefer.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

class Ask(BaseModel):
    question: str

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/")
def home():
    if os.path.exists(UI):
        return FileResponse(UI)
    return JSONResponse({"msg": "UI not found; POST /ask with {\"question\": ...}"})

@app.post("/ask")
def ask(body: Ask):
    return answer(body.question)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
