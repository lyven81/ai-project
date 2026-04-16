"""
FastAPI backend for Sundry Shop Assistant.

Serves the frontend (../) as static files and exposes a WebSocket endpoint
at /ws that bridges the browser to Gemini Live API, with function calls
routed to our MCP-style tools over dataset.csv.

Query parameters on /ws:
  ?mode=audio   — Gemini responds with audio (default)
  ?mode=text    — Gemini responds with text only

Run locally:
  cd backend
  python main.py

Deploy to Cloud Run:
  See ../deploy.md
"""
import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gemini_live import GeminiLive

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("MODEL", "gemini-2.5-flash-native-audio-latest")
VOICE_NAME = os.getenv("VOICE_NAME", "Aoede")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not set — /ws will fail until provided.")

# Project root contains index.html + css/ + js/ + dataset.csv
PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(title="Sundry Shop Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
app.mount("/css", StaticFiles(directory=str(PROJECT_ROOT / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(PROJECT_ROOT / "js")), name="js")


@app.get("/")
async def root():
    return FileResponse(str(PROJECT_ROOT / "index.html"))


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "model": MODEL}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Bridge browser <-> Gemini Live."""
    # Native-audio models only support AUDIO modality; text-out is handled
    # client-side by muting playback while still rendering the transcript.
    response_modality = "AUDIO"

    await websocket.accept()
    logger.info(f"WebSocket accepted (mode={response_modality})")

    audio_input_queue: asyncio.Queue = asyncio.Queue()
    text_input_queue: asyncio.Queue = asyncio.Queue()

    async def audio_output_callback(data: bytes):
        try:
            await websocket.send_bytes(data)
        except Exception as e:
            logger.debug(f"send_bytes failed (client likely gone): {e}")

    async def audio_interrupt_callback():
        try:
            await websocket.send_json({"type": "interrupted"})
        except Exception:
            pass

    gemini = GeminiLive(
        api_key=GEMINI_API_KEY,
        model=MODEL,
        response_modality=response_modality,
        voice_name=VOICE_NAME,
    )

    async def receive_from_client():
        try:
            while True:
                message = await websocket.receive()
                if message.get("bytes") is not None:
                    await audio_input_queue.put(message["bytes"])
                elif message.get("text") is not None:
                    text = message["text"]
                    try:
                        payload = json.loads(text)
                        if isinstance(payload, dict) and "text" in payload:
                            await text_input_queue.put(payload["text"])
                            continue
                    except json.JSONDecodeError:
                        pass
                    await text_input_queue.put(text)
        except WebSocketDisconnect:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"receive_from_client error: {e}")

    receive_task = asyncio.create_task(receive_from_client())

    async def run_session():
        async for event in gemini.start_session(
            audio_input_queue=audio_input_queue,
            text_input_queue=text_input_queue,
            audio_output_callback=audio_output_callback,
            audio_interrupt_callback=audio_interrupt_callback,
        ):
            if event:
                try:
                    await websocket.send_json(event)
                except Exception as e:
                    logger.debug(f"send_json failed: {e}")
                    break

    try:
        await run_session()
    except Exception as e:
        logger.error(f"Gemini session error: {type(e).__name__}: {e}")
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass
    finally:
        receive_task.cancel()
        try:
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
