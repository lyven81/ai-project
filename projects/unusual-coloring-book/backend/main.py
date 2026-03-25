import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from image_service import ImageService
from story_library import STORY
from cache import BookCache

app = FastAPI(title="Unusual Coloring Book API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = BookCache()
image_service = ImageService()


# --- Request models ---

class PageImageRequest(BaseModel):
    page_number: int   # 1–6
    option_id: str     # "a", "b", or "c"

class EditImageRequest(BaseModel):
    image_base64: str
    instruction: str


# --- Routes ---

@app.get("/")
async def root():
    return {"status": "Unusual Coloring Book API v3 running"}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/story")
async def get_story():
    """Return the full story structure (all pages + options) without images."""
    pages_out = []
    for p in STORY["pages"]:
        options_out = [
            {
                "id": opt["id"],
                "preview": opt["preview"],
                "story_text": opt["story_text"],
            }
            for opt in p["options"]
        ]
        pages_out.append({
            "page": p["page"],
            "chapter_title": p["chapter_title"],
            "options": options_out,
        })
    return {
        "id": STORY["id"],
        "title": STORY["title"],
        "subtitle": STORY["subtitle"],
        "total_pages": STORY["total_pages"],
        "pages": pages_out,
    }


@app.get("/story/cover")
async def get_cover():
    """Return the cover illustration (generated once, then cached)."""
    if cache.has("cover_image"):
        return {"image": cache.get("cover_image")}
    try:
        image = await image_service.generate_single(STORY["cover_prompt"])
        cache.set("cover_image", image)
        return {"image": image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/page-image")
async def generate_page_image(req: PageImageRequest):
    """Generate (or return cached) illustration for a specific page + option."""
    if not 1 <= req.page_number <= STORY["total_pages"]:
        raise HTTPException(status_code=400, detail="page_number out of range")
    if req.option_id not in ("a", "b", "c"):
        raise HTTPException(status_code=400, detail="option_id must be a, b, or c")

    cache_key = f"page_{req.page_number}_{req.option_id}"
    if cache.has(cache_key):
        return {"image": cache.get(cache_key)}

    page_data = next((p for p in STORY["pages"] if p["page"] == req.page_number), None)
    option = next((o for o in page_data["options"] if o["id"] == req.option_id), None)

    try:
        image = await image_service.generate_single(option["image_prompt"])
        cache.set(cache_key, image)
        return {"image": image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/edit/image")
async def edit_image(req: EditImageRequest):
    try:
        result = await image_service.edit(req.image_base64, req.instruction)
        return {"image": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
