import os
import base64
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(title="AI Group Photo Generator", description="Create group photos using Gemini AI")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Setup static files only if folder exists
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "port": os.environ.get("PORT", 8080),
        "service": "ai-group-photo-generator"
    }

async def generate_group_image(
    images_data: List[bytes],
    images_mimes: List[str],
    pose_data: Optional[bytes] = None,
    pose_mime: Optional[str] = None,
    scene: str = "modern office",
    aspect_ratio: str = "16:9"
) -> str:
    """Generate group photo using Gemini AI"""
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare content parts
        content_parts = []
        
        # Add scene description
        if pose_data and pose_mime:
            prompt = f"""Create a professional group photo with the following requirements:
1. Use the people from the uploaded images as the subjects
2. Arrange them in the pose/formation shown in the reference image
3. Set the scene in: {scene}
4. Maintain each person's individual features, clothing, and appearance
5. Ensure natural lighting and professional photography quality
6. Final aspect ratio: {aspect_ratio}
7. Remove any text or watermarks from the final image"""
        else:
            prompt = f"""Create a professional group photo with the following requirements:
1. Use the people from the uploaded images as the subjects  
2. Arrange them in a natural, professional group formation
3. Set the scene in: {scene}
4. Maintain each person's individual features, clothing, and appearance
5. Ensure natural lighting and professional photography quality
6. Final aspect ratio: {aspect_ratio}
7. Remove any text or watermarks from the final image"""
        
        content_parts.append(prompt)
        
        # Add individual photos
        for i, (img_data, mime_type) in enumerate(zip(images_data, images_mimes)):
            b64_data = base64.b64encode(img_data).decode('utf-8')
            content_parts.append({
                "mime_type": mime_type,
                "data": b64_data
            })
        
        # Add pose reference if provided
        if pose_data and pose_mime:
            pose_b64 = base64.b64encode(pose_data).decode('utf-8')
            content_parts.append({
                "mime_type": pose_mime,
                "data": pose_b64
            })
        
        # Generate content
        response = model.generate_content(
            contents=content_parts,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048,
            }
        )
        
        # Check if response has image data
        if hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data
        
        return response.text if response.text else "No image generated"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Group photo generation failed: {str(e)}")

@app.post("/generate")
async def generate_group_endpoint(
    images: List[UploadFile] = File(..., description="Individual photos"),
    pose_image: Optional[UploadFile] = File(None, description="Optional pose reference"),
    scene: str = Form("modern office", description="Scene setting"),
    aspect_ratio: str = Form("16:9", description="Output aspect ratio")
):
    """Generate group photo endpoint"""
    try:
        # Validate we have at least 2 images
        if len(images) < 2:
            raise HTTPException(status_code=400, detail="Please upload at least 2 individual photos")
        
        if len(images) > 8:
            raise HTTPException(status_code=400, detail="Maximum 8 photos allowed")
        
        # Process individual images
        images_data = []
        images_mimes = []
        
        for img in images:
            if not img.content_type or not img.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="All files must be valid images")
            
            img_data = await img.read()
            images_data.append(img_data)
            images_mimes.append(img.content_type)
        
        # Process pose image if provided
        pose_data = None
        pose_mime = None
        if pose_image and pose_image.filename:
            if not pose_image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Pose reference must be a valid image")
            pose_data = await pose_image.read()
            pose_mime = pose_image.content_type
        
        # Validate inputs
        if not scene.strip():
            scene = "modern office"
        
        valid_ratios = ["1:1", "4:3", "16:9", "9:16"]
        if aspect_ratio not in valid_ratios:
            aspect_ratio = "16:9"
        
        # Generate group image
        result = await generate_group_image(
            images_data, images_mimes,
            pose_data, pose_mime,
            scene.strip(), aspect_ratio
        )
        
        return JSONResponse({
            "success": True,
            "result": result,
            "scene": scene,
            "aspect_ratio": aspect_ratio,
            "num_people": len(images),
            "has_pose_reference": pose_data is not None
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