import os
import base64
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(title="Virtual Try-On Studio", description="Virtual fashion try-on using Gemini AI")

# Setup templates safely
templates = None
if os.path.isdir("templates"):
    templates = Jinja2Templates(directory="templates")

# Setup static files only if folder exists
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("<h1>Welcome to Virtual Try-On Studio</h1>")

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy"}

async def virtual_try_on(
    person_data: bytes,
    person_mime: str,
    item_data: bytes,
    item_mime: str,
    item_type: str = "clothing",
    style: str = "realistic"
) -> str:
    """Perform virtual try-on using Gemini AI"""
    try:
        person_b64 = base64.b64encode(person_data).decode('utf-8')
        item_b64 = base64.b64encode(item_data).decode('utf-8')

        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        if item_type == "clothing":
            prompt = f"""Create a {style} virtual try-on image with these requirements:
1. Use the person from the first image as the model
2. Have them wear the clothing item from the second image
3. Ensure the clothing fits naturally on the person's body
4. Maintain the person's pose, face, and overall appearance
5. Adjust lighting and shadows to make it look realistic
6. Remove any background distractions
7. Style: {style}
8. Make sure the clothing matches the person's body proportions"""
        elif item_type == "accessories":
            prompt = f"""Create a {style} virtual try-on image with these requirements:
1. Use the person from the first image as the model  
2. Add the accessory from the second image
3. Place it in the appropriate location (glasses on face, jewelry, etc.)
4. Maintain the person's natural appearance and pose
5. Ensure realistic lighting and reflections
6. Style: {style}
7. Make the accessory look naturally worn by the person"""
        else:
            prompt = f"""Create a {style} virtual try-on image combining these elements:
1. Use the person from the first image as the base
2. Apply or add the item from the second image appropriately
3. Ensure natural integration and realistic appearance
4. Maintain the person's identity and characteristics
5. Style: {style}
6. Create a professional, high-quality result"""

        person_part = {"mime_type": person_mime, "data": person_b64}
        item_part = {"mime_type": item_mime, "data": item_b64}

        response = model.generate_content(
            contents=[prompt, person_part, item_part],
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 2048,
            }
        )

        if hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data

        return response.text if response.text else "No image generated"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virtual try-on failed: {str(e)}")

@app.post("/try-on")
async def try_on_endpoint(
    person_image: UploadFile = File(..., description="Person/model image"),
    item_image: UploadFile = File(..., description="Clothing/accessory item image"),
    item_type: str = Form("clothing", description="Type: clothing, accessories, or general"),
    style: str = Form("realistic", description="Style: realistic, artistic, fashion")
):
    """Virtual try-on endpoint"""
    try:
        if not person_image.content_type or not person_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Person image must be a valid image file")
        
        if not item_image.content_type or not item_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Item image must be a valid image file")

        person_data = await person_image.read()
        item_data = await item_image.read()

        if item_type not in ["clothing", "accessories", "general"]:
            item_type = "clothing"
        if style not in ["realistic", "artistic", "fashion"]:
            style = "realistic"

        result = await virtual_try_on(
            person_data, person_image.content_type,
            item_data, item_image.content_type,
            item_type, style
        )

        return JSONResponse({
            "success": True,
            "result": result,
            "item_type": item_type,
            "style": style,
            "person_filename": person_image.filename,
            "item_filename": item_image.filename
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on host 0.0.0.0 and port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, access_log=True, log_level="info")
