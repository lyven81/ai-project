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

app = FastAPI(title="Pose Perfect AI", description="Generate images with perfect poses using Gemini AI")

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
    return HTMLResponse("<h1>Welcome to Pose Perfect AI</h1>")

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy"}

async def generate_image_from_pose(
    subject_data: bytes, 
    subject_mime: str,
    pose_data: bytes, 
    pose_mime: str,
    aspect_ratio: str = "1:1"
) -> str:
    """Generate image with pose transfer using Gemini AI"""
    try:
        subject_b64 = base64.b64encode(subject_data).decode('utf-8')
        pose_b64 = base64.b64encode(pose_data).decode('utf-8')
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""Follow these instructions precisely:
1. The subject is the person in the first image. Preserve their face, features, clothing, and identity.
2. The pose is shown in the second image. Recreate the subject adopting this pose.
3. The output must be a photorealistic image.
4. The background should be a clean, minimalist studio with soft lighting. No text or watermarks.
5. Final image must have an aspect ratio of {aspect_ratio}.
6. Return the result strictly as an image in base64 inline_data. Do not return text."""

        response = model.generate_content(
            contents=[
                prompt,
                {
                    "inline_data": {
                        "mime_type": subject_mime,
                        "data": subject_b64
                    }
                },
                {
                    "inline_data": {
                        "mime_type": pose_mime,
                        "data": pose_b64
                    }
                }
            ],
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048,
            }
        )

        # Extract base64 image from response
        if hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data

        # If no image was returned, fallback to text
        return response.text if hasattr(response, "text") and response.text else "No image generated"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pose generation failed: {str(e)}")

@app.post("/generate")
async def generate_pose_endpoint(
    subject_image: UploadFile = File(..., description="Subject image"),
    pose_image: UploadFile = File(..., description="Pose reference image"),
    aspect_ratio: str = Form("1:1", description="Aspect ratio for output image")
):
    """Generate pose-perfect image endpoint"""
    try:
        if not subject_image.content_type or not subject_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Subject file must be a valid image")
        
        if not pose_image.content_type or not pose_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Pose file must be a valid image")
        
        subject_data = await subject_image.read()
        pose_data = await pose_image.read()
        
        if aspect_ratio not in ["1:1", "9:16", "16:9"]:
            aspect_ratio = "1:1"
        
        result = await generate_image_from_pose(
            subject_data, subject_image.content_type,
            pose_data, pose_image.content_type,
            aspect_ratio
        )
        
        return JSONResponse({
            "success": True,
            "result": result,
            "aspect_ratio": aspect_ratio,
            "subject_filename": subject_image.filename,
            "pose_filename": pose_image.filename
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
