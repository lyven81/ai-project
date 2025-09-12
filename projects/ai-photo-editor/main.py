import os
import base64
from typing import Optional
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

app = FastAPI(title="AI Photo Editor", description="Edit photos using Gemini AI")

# Setup templates (safe version)
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
    return HTMLResponse("<h1>Welcome to AI Photo Editor</h1>")

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy"}

async def edit_image_with_gemini(image_data: bytes, mime_type: str, prompt: str) -> str:
    """Edit image using Gemini AI"""
    try:
        # Convert image data to base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare the content
        image_part = {
            "mime_type": mime_type,
            "data": base64_data
        }
        
        # Generate content with image and prompt
        response = model.generate_content(
            contents=[image_part, prompt],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            }
        )
        
        # Check if response has image data
        if hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data
        
        # If no image in response, return text explanation
        return response.text if response.text else "No image generated"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image editing failed: {str(e)}")

@app.post("/edit")
async def edit_image_endpoint(
    image: UploadFile = File(...),
    prompt: str = Form(...)
):
    """Edit image endpoint"""
    try:
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Please upload a valid image file")
        
        # Read image data
        image_data = await image.read()
        
        # Validate prompt
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Please provide an editing prompt")
        
        # Edit image with Gemini
        result = await edit_image_with_gemini(image_data, image.content_type, prompt.strip())
        
        return JSONResponse({
            "success": True,
            "result": result,
            "original_filename": image.filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on host 0.0.0.0 and port {port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        access_log=True,
        log_level="info"
    )
