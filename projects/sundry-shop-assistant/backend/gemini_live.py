"""
Gemini Live API wrapper for Sundry Shop Assistant.

Adapted from the official gemini-live-genai-python-sdk reference. Key changes:
  - Santai BM system instruction loaded from ../system-prompt.txt
  - Tools wired via tool_bridge (our MCP-style tools over dataset.csv)
  - Voice config uses a voice that handles Malay reasonably well
  - Supports AUDIO or TEXT response modality per session (client toggle)
"""
from __future__ import annotations

import asyncio
import inspect
import logging
import traceback
from pathlib import Path

from google import genai
from google.genai import types

from tool_bridge import get_tools, get_tool_mapping

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "system-prompt.txt"


def _load_system_prompt() -> str:
    return _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


class GeminiLive:
    """Thin wrapper around Gemini Live API for the Sundry Shop Assistant session."""

    def __init__(
        self,
        api_key: str,
        model: str,
        input_sample_rate: int = 16000,
        response_modality: str = "AUDIO",  # "AUDIO" or "TEXT"
        voice_name: str = "Puck",
    ):
        self.api_key = api_key
        self.model = model
        self.input_sample_rate = input_sample_rate
        self.response_modality = response_modality.upper()
        self.voice_name = voice_name
        self.client = genai.Client(api_key=api_key)
        self.tools = get_tools()
        self.tool_mapping = get_tool_mapping()
        self.system_prompt = _load_system_prompt()

    async def start_session(
        self,
        audio_input_queue: asyncio.Queue,
        text_input_queue: asyncio.Queue,
        audio_output_callback,
        audio_interrupt_callback=None,
    ):
        modality = (
            types.Modality.AUDIO if self.response_modality == "AUDIO" else types.Modality.TEXT
        )

        config_kwargs = {
            "response_modalities": [modality],
            "system_instruction": types.Content(
                parts=[types.Part(text=self.system_prompt)]
            ),
            "input_audio_transcription": types.AudioTranscriptionConfig(),
            "output_audio_transcription": types.AudioTranscriptionConfig(),
            "realtime_input_config": types.RealtimeInputConfig(
                turn_coverage="TURN_INCLUDES_ONLY_ACTIVITY",
            ),
            "tools": self.tools,
        }
        if modality == types.Modality.AUDIO:
            config_kwargs["speech_config"] = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.voice_name
                    )
                )
            )

        config = types.LiveConnectConfig(**config_kwargs)

        logger.info(
            f"Connecting to Gemini Live: model={self.model}, "
            f"modality={self.response_modality}, voice={self.voice_name}"
        )

        try:
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
                logger.info("Gemini Live session opened")

                async def send_audio():
                    try:
                        while True:
                            chunk = await audio_input_queue.get()
                            await session.send_realtime_input(
                                audio=types.Blob(
                                    data=chunk,
                                    mime_type=f"audio/pcm;rate={self.input_sample_rate}",
                                )
                            )
                    except asyncio.CancelledError:
                        logger.debug("send_audio cancelled")
                    except Exception as e:
                        logger.error(f"send_audio error: {e}")

                async def send_text():
                    try:
                        while True:
                            text = await text_input_queue.get()
                            logger.info(f"Sending text to Gemini: {text!r}")
                            await session.send_realtime_input(text=text)
                    except asyncio.CancelledError:
                        logger.debug("send_text cancelled")
                    except Exception as e:
                        logger.error(f"send_text error: {e}")

                event_queue: asyncio.Queue = asyncio.Queue()

                async def receive_loop():
                    try:
                        while True:
                            async for response in session.receive():
                                server_content = response.server_content
                                tool_call = response.tool_call

                                if server_content:
                                    if server_content.model_turn:
                                        for part in server_content.model_turn.parts:
                                            # Audio output
                                            if part.inline_data:
                                                if inspect.iscoroutinefunction(audio_output_callback):
                                                    await audio_output_callback(part.inline_data.data)
                                                else:
                                                    audio_output_callback(part.inline_data.data)
                                            # Text output (when response_modalities=TEXT)
                                            if part.text:
                                                await event_queue.put(
                                                    {"type": "gemini", "text": part.text}
                                                )

                                    if (
                                        server_content.input_transcription
                                        and server_content.input_transcription.text
                                    ):
                                        await event_queue.put(
                                            {
                                                "type": "user",
                                                "text": server_content.input_transcription.text,
                                            }
                                        )

                                    if (
                                        server_content.output_transcription
                                        and server_content.output_transcription.text
                                    ):
                                        await event_queue.put(
                                            {
                                                "type": "gemini",
                                                "text": server_content.output_transcription.text,
                                            }
                                        )

                                    if server_content.turn_complete:
                                        await event_queue.put({"type": "turn_complete"})

                                    if server_content.interrupted:
                                        if audio_interrupt_callback:
                                            if inspect.iscoroutinefunction(audio_interrupt_callback):
                                                await audio_interrupt_callback()
                                            else:
                                                audio_interrupt_callback()
                                        await event_queue.put({"type": "interrupted"})

                                if tool_call:
                                    function_responses = []
                                    for fc in tool_call.function_calls:
                                        func_name = fc.name
                                        args = fc.args or {}
                                        logger.info(f"Tool call: {func_name}({args})")

                                        if func_name in self.tool_mapping:
                                            try:
                                                tool_func = self.tool_mapping[func_name]
                                                if inspect.iscoroutinefunction(tool_func):
                                                    result = await tool_func(**args)
                                                else:
                                                    loop = asyncio.get_running_loop()
                                                    result = await loop.run_in_executor(
                                                        None, lambda: tool_func(**args)
                                                    )
                                            except Exception as e:
                                                logger.error(f"Tool {func_name} failed: {e}")
                                                result = {"error": str(e)}

                                            function_responses.append(
                                                types.FunctionResponse(
                                                    name=func_name,
                                                    id=fc.id,
                                                    response={"result": result},
                                                )
                                            )
                                            await event_queue.put(
                                                {
                                                    "type": "tool_call",
                                                    "name": func_name,
                                                    "args": args,
                                                    "result": result,
                                                }
                                            )

                                    await session.send_tool_response(
                                        function_responses=function_responses
                                    )

                    except asyncio.CancelledError:
                        logger.debug("receive_loop cancelled")
                    except Exception as e:
                        logger.error(
                            f"receive_loop error: {type(e).__name__}: {e}\n"
                            f"{traceback.format_exc()}"
                        )
                        await event_queue.put(
                            {"type": "error", "error": f"{type(e).__name__}: {e}"}
                        )
                    finally:
                        await event_queue.put(None)

                send_audio_task = asyncio.create_task(send_audio())
                send_text_task = asyncio.create_task(send_text())
                receive_task = asyncio.create_task(receive_loop())

                try:
                    while True:
                        event = await event_queue.get()
                        if event is None:
                            break
                        yield event
                finally:
                    logger.info("Cleaning up Gemini Live tasks")
                    send_audio_task.cancel()
                    send_text_task.cancel()
                    receive_task.cancel()

        except Exception as e:
            logger.error(
                f"Gemini Live session error: {type(e).__name__}: {e}\n"
                f"{traceback.format_exc()}"
            )
            raise
        finally:
            logger.info("Gemini Live session closed")
