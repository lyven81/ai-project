"""Good Company — Stock Research Assistant."""

import os
import re
import json
import webbrowser
import threading
from pathlib import Path
from datetime import datetime

import fitz  # PyMuPDF
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

from prompts import PHASE_1, READ_MORE, PHASE_2, FINAL

load_dotenv()

app = FastAPI()

# --- Config ---

REPORT_DIR = Path(__file__).parent / "Quarter report"
REPORT_DIR.mkdir(exist_ok=True)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-2.5-flash")

# --- PDF text cache ---

_text_cache: dict[str, str] = {}


def extract_text(filename: str) -> str:
    """Extract text from a PDF in the Quarter report folder. Cached per filename."""
    if filename in _text_cache:
        return _text_cache[filename]
    path = REPORT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {filename}")
    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    _text_cache[filename] = text
    return text


def parse_visual_data(response_text: str) -> tuple[str, dict | None]:
    """Separate narrative text from VISUAL_DATA JSON block."""
    match = re.search(r"VISUAL_DATA_START\s*(\{.*?\})\s*VISUAL_DATA_END", response_text, re.DOTALL)
    if match:
        text = response_text[:match.start()].strip()
        try:
            visual_data = json.loads(match.group(1))
            return text, visual_data
        except json.JSONDecodeError:
            return text, None
    return response_text.strip(), None


def parse_date_from_filename(filename: str) -> tuple[datetime, str]:
    """Parse date and company name from 'Company - DD Mon YY.pdf' pattern.
    Returns (date, company_name). Falls back to file mod time if pattern doesn't match."""
    name = Path(filename).stem  # remove .pdf
    # Try pattern: "Company - DD Mon YY" or "Company -DD Mon YY"
    match = re.match(r"^(.+?)\s*-\s*(\d{1,2}\s+\w{3}\s+\d{2})\s*$", name)
    if match:
        company = match.group(1).strip()
        date_str = match.group(2).strip()
        try:
            dt = datetime.strptime(date_str, "%d %b %y")
            return dt, company
        except ValueError:
            pass
    # Fallback: use file modification time
    path = REPORT_DIR / filename
    if path.exists():
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime), name
    return datetime.min, name


# --- API models ---

class AnalyzeRequest(BaseModel):
    report: str
    prompt: str
    params: dict = {}


# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = Path(__file__).parent / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/reports")
async def list_reports():
    """List PDF files sorted by date (newest first), then alphabetical."""
    pdfs = list(REPORT_DIR.glob("*.pdf"))

    # Parse dates and sort
    entries = []
    for p in pdfs:
        dt, company = parse_date_from_filename(p.name)
        date_label = dt.strftime("%-d %b %y") if os.name != "nt" else dt.strftime("%#d %b %y")
        entries.append({
            "file": p.name,
            "company": company,
            "date": dt,
            "date_label": date_label,
        })

    # Sort: newest date first, then company A-Z within same date
    entries.sort(key=lambda e: (-e["date"].timestamp(), e["company"].lower()))

    # Group by date
    groups = []
    current_label = None
    current_group = None
    for e in entries:
        if e["date_label"] != current_label:
            current_label = e["date_label"]
            current_group = {"date": current_label, "reports": []}
            groups.append(current_group)
        current_group["reports"].append({"file": e["file"], "company": e["company"]})

    return {"groups": groups}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """Run a single analysis prompt against a quarter report."""
    all_prompts = {**PHASE_1, **READ_MORE, **PHASE_2, **FINAL}
    prompt_data = all_prompts.get(req.prompt)
    if not prompt_data:
        return {"error": f"Unknown prompt: {req.prompt}"}

    text = extract_text(req.report)
    template = prompt_data["instruction"]

    if req.prompt == "company_comparison":
        report_b = req.params.get("report_b", "")
        if not report_b:
            return {"error": "Company comparison requires a second report (report_b)."}
        text_b = extract_text(report_b)
        full_prompt = template.replace("{report_text_a}", text).replace("{report_text_b}", text_b)
    elif req.prompt == "risk_check":
        price = req.params.get("price", "not specified")
        horizon = req.params.get("horizon", "3 years")
        risk_tolerance = req.params.get("risk_tolerance", "medium")
        full_prompt = (
            template
            .replace("{price}", str(price))
            .replace("{horizon}", str(horizon))
            .replace("{risk_tolerance}", str(risk_tolerance))
            .replace("{report_text}", text)
        )
    else:
        full_prompt = template.replace("{report_text}", text)

    response = model.generate_content(full_prompt)
    narrative, visual_data = parse_visual_data(response.text)

    return {
        "result": narrative,
        "visual_data": visual_data,
        "visual_type": prompt_data.get("visual_type", "none"),
        "prompt": req.prompt,
        "name": prompt_data["name"],
    }


@app.post("/clear-cache")
async def clear_cache():
    """Clear the PDF text cache (useful after adding new reports)."""
    _text_cache.clear()
    return {"status": "cache cleared"}


# --- Startup ---

def open_browser():
    import time
    time.sleep(2)
    webbrowser.open("http://localhost:8080")


if __name__ == "__main__":
    import uvicorn
    print("\n  Good Company — Stock Research Assistant")
    print("  http://localhost:8080\n")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
