"""
Gemini image generation and editing service.
Uses a single model for generation, editing, and cover creation.
"""

import os
import base64
import asyncio
from google import genai
from google.genai import types

IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview")

COLORING_BOOK_STYLE = (
    "children's coloring book illustration, thick clean black outlines, "
    "white background, no color fill, simple friendly style, "
    "large expressive characters, suitable for ages 5-10, "
    "child-safe, no scary elements, warm and inviting"
)


class ImageService:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    async def generate_single(self, prompt: str) -> str:
        full_prompt = (
            f"{COLORING_BOOK_STYLE}. "
            f"Scene: {prompt}. "
            "Draw only clean black outlines on pure white. No shading, no color fill anywhere."
        )

        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=IMAGE_MODEL,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    )
                )
            )

            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    data = part.inline_data.data
                    if isinstance(data, bytes):
                        return base64.b64encode(data).decode("utf-8")
                    return data

        except Exception as e:
            print(f"Image generation error: {e}")

        # Fallback: return a placeholder SVG as base64
        return self._placeholder_svg(prompt[:40])

    async def generate_parallel(self, prompts: list) -> list:
        tasks = [self.generate_single(p) for p in prompts]
        return await asyncio.gather(*tasks)

    async def edit(self, image_base64: str, instruction: str) -> str:
        full_instruction = (
            f"Edit this coloring book illustration: {instruction}. "
            "Keep the style identical: thick black outlines, white background, "
            "no color fill, child-safe coloring book style."
        )

        try:
            image_bytes = base64.b64decode(image_base64)
            loop = asyncio.get_event_loop()

            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=IMAGE_MODEL,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        full_instruction,
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    )
                )
            )

            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    data = part.inline_data.data
                    if isinstance(data, bytes):
                        return base64.b64encode(data).decode("utf-8")
                    return data

        except Exception as e:
            print(f"Image edit error: {e}")

        return image_base64  # Return original if edit fails

    async def generate_cover(self, title: str, character_name: str) -> str:
        prompt = (
            f"Cover illustration for a children's coloring book titled '{title}'. "
            f"Show {character_name} in a friendly, welcoming central pose. "
            "Leave empty space at the top third for the title text. "
            f"{COLORING_BOOK_STYLE}. "
            "Clean black outlines only, white background, no fill."
        )
        return await self.generate_single(prompt)

    def _placeholder_svg(self, label: str) -> str:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="white" stroke="#2D3436" stroke-width="4"/>
  <rect x="40" y="40" width="520" height="520" fill="none" stroke="#2D3436" stroke-width="3" rx="20"/>
  <circle cx="300" cy="220" r="80" fill="none" stroke="#2D3436" stroke-width="4"/>
  <ellipse cx="300" cy="400" rx="120" ry="80" fill="none" stroke="#2D3436" stroke-width="4"/>
  <line x1="220" y1="350" x2="180" y2="460" stroke="#2D3436" stroke-width="4" stroke-linecap="round"/>
  <line x1="380" y1="350" x2="420" y2="460" stroke="#2D3436" stroke-width="4" stroke-linecap="round"/>
  <text x="300" y="530" text-anchor="middle" font-family="Arial" font-size="16" fill="#2D3436">Illustration loading...</text>
  <text x="300" y="555" text-anchor="middle" font-family="Arial" font-size="12" fill="#95A5A6">{label}</text>
</svg>"""
        return base64.b64encode(svg.encode()).decode("utf-8")
