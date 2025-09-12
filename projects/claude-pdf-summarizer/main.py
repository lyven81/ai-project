import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
from dotenv import load_dotenv
from anthropic import Anthropic
from typing import Literal
import io

load_dotenv()

app = FastAPI(
    title="Claude PDF Summarizer API",
    description="Upload a PDF and get AI-powered summaries in multiple languages and styles",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

try:
    client = Anthropic(api_key=API_KEY)
except Exception as e:
    raise ValueError(f"Failed to initialize Anthropic client: {str(e)}")

def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        
        if len(reader.pages) == 0:
            raise ValueError("PDF has no pages")
            
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        if not text.strip():
            raise ValueError("No text could be extracted from PDF")
            
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting PDF: {str(e)}")

def build_prompt(text: str, style: str, language: str, bullet_points: int = 3) -> str:
    if language == "Bahasa Malaysia":
        if style == "Professional Executive Summary":
            return (
                f"Hanya gunakan Bahasa Malaysia dalam jawapan; jangan campurkan bahasa lain. "
                f"Tolong ringkaskan kandungan berikut kepada {bullet_points} isi penting "
                f"dalam gaya formal dan padat untuk pembuat keputusan perniagaan:\n\n{text}"
            )
        elif style == "Simple Version":
            return (
                f"Hanya gunakan Bahasa Malaysia dalam jawapan; jangan campurkan bahasa lain. "
                f"Tolong ringkaskan kandungan berikut kepada {bullet_points} isi penting "
                f"dengan bahasa yang mudah difahami oleh orang ramai:\n\n{text}"
            )
        else:  # For Kids
            return (
                f"Hanya gunakan Bahasa Malaysia dalam jawapan; jangan campurkan bahasa lain. "
                f"Tolong terangkan kandungan berikut untuk kanak-kanak dalam {bullet_points} "
                f"isi mudah difahami:\n\n{text}"
            )

    if language == "中文（简体）":
        if style == "Professional Executive Summary":
            return (
                f"请只用简体中文回答，不要混用其他语言。"
                f"请将以下内容以正式、简洁的语气总结为 {bullet_points} 个要点，适合商业决策者阅读：\n\n{text}"
            )
        elif style == "Simple Version":
            return (
                f"请只用简体中文回答，不要混用其他语言。"
                f"请用简洁易懂的语言将以下内容总结为 {bullet_points} 个要点：\n\n{text}"
            )
        else:  # For Kids
            return (
                f"请只用简体中文回答，不要混用其他语言。"
                f"请用适合 10 岁儿童理解的方式，将以下内容总结为 {bullet_points} 个简单要点：\n\n{text}"
            )

    # Default to English
    if style == "Professional Executive Summary":
        return (
            f"Answer only in English; do not mix other languages. "
            f"Write in a formal, concise tone for business decision-makers. "
            f"Summarize the following into {bullet_points} bullet points:\n\n{text}"
        )
    elif style == "Simple Version":
        return (
            f"Answer only in English; do not mix other languages. "
            f"Write in simple, everyday language. "
            f"Summarize the following into {bullet_points} bullet points:\n\n{text}"
        )
    else:  # For Kids
        return (
            f"Answer only in English; do not mix other languages. "
            f"Explain in a fun, friendly way for a 10-year-old. "
            f"Summarize the following into {bullet_points} bullet points:\n\n{text}"
        )

def summarize_with_claude(prompt: str) -> str:
    try:
        if not prompt or not prompt.strip():
            raise ValueError("Empty prompt provided")
        
        if len(prompt) > 100000:
            raise ValueError("Content too long for processing")
        
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        
        if resp.content and len(resp.content) > 0:
            return resp.content[0].text
        else:
            raise ValueError("No response received from Claude API")
            
    except Exception as e:
        raise ValueError(f"Claude API error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Claude PDF Summarizer API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "claude-pdf-summarizer"}

@app.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    style: Literal["Professional Executive Summary", "Simple Version", "For Kids"] = Form("Simple Version"),
    language: Literal["English", "Bahasa Malaysia", "中文（简体）"] = Form("English"),
    bullet_points: int = Form(3, ge=3, le=10)
):
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Extract text from PDF
        try:
            text = extract_text_from_pdf(file_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate extracted text
        if len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="PDF content too short to summarize effectively")
        
        # Build prompt and summarize
        prompt = build_prompt(text, style, language, bullet_points)
        
        try:
            summary = summarize_with_claude(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        return JSONResponse({
            "success": True,
            "summary": summary,
            "metadata": {
                "filename": file.filename,
                "style": style,
                "language": language,
                "bullet_points": bullet_points,
                "text_length": len(text)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)