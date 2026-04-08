"""
Kereta Sewa Jalan-jalan - Car Rental Booking Agent - FastAPI REST API
Agentic AI workflow using code-as-action pattern
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import google.generativeai as genai
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
import re, io, sys, traceback

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if GOOGLE_API_KEY and GOOGLE_API_KEY != "placeholder_key_to_update":
    genai.configure(api_key=GOOGLE_API_KEY)
    API_CONFIGURED = True
else:
    API_CONFIGURED = False

app = FastAPI(title="Kereta Sewa Jalan-jalan API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

db = TinyDB('kereta_sewa_bookings.json')
vehicles_tbl = db.table('vehicles')
bookings_tbl = db.table('bookings')

PICKUP_LOCATIONS = ["KLIA", "KL Sentral", "Subang Airport (SZB)", "TBS"]
BOOKING_DEPOSIT = 100.0
HOTEL_DELIVERY_FEE = 50.0

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    status: str

# Helper functions
def next_booking_id(tbl, prefix="RNT"):
    records = tbl.all()
    if not records:
        return f"{prefix}001"
    nums = [int(r.get("booking_id", prefix+"000")[len(prefix):]) for r in records if r.get("booking_id", "").startswith(prefix)]
    return f"{prefix}{max(nums, default=0) + 1:03d}"

def get_daily_rate(tier):
    return {"Economy": 120.0, "Compact": 160.0, "SUV": 250.0, "MPV": 220.0, "Premium": 350.0}.get(tier, 150.0)

def get_weekly_rate(tier):
    return {"Economy": 700.0, "Compact": 950.0}.get(tier, None)

def calculate_rental_cost(tier, days, hotel_delivery=False):
    weekly = get_weekly_rate(tier)
    daily = get_daily_rate(tier)
    if weekly and days == 7:
        base = weekly
    else:
        base = daily * days
    total = base + BOOKING_DEPOSIT
    if hotel_delivery:
        total += HOTEL_DELIVERY_FEE
    return {"base": base, "deposit": BOOKING_DEPOSIT, "delivery": HOTEL_DELIVERY_FEE if hotel_delivery else 0, "total": total}

def has_date_conflict(vehicle_id, pickup_date, return_date, bookings_tbl):
    start = datetime.strptime(pickup_date, "%Y-%m-%d")
    end = datetime.strptime(return_date, "%Y-%m-%d")
    existing = bookings_tbl.search((Query().vehicle_id == vehicle_id) & (Query().status.one_of(["rented", "booked"])))
    for b in existing:
        ex_start = datetime.strptime(b["pickup_date"], "%Y-%m-%d")
        ex_end = datetime.strptime(b["return_date"], "%Y-%m-%d")
        if not (end <= ex_start or start >= ex_end):
            return True
    return False

PROMPT = """You are Kereta Sewa Jalan-jalan car rental booking assistant. WRITE PYTHON CODE.

Database: vehicles_tbl, bookings_tbl | Functions: next_booking_id, get_daily_rate, get_weekly_rate, calculate_rental_cost, has_date_conflict, datetime, timedelta
Fleet: 56 vehicles across Economy/Compact/SUV/MPV/Premium tiers
Pricing: Economy RM120/day RM700/week | Compact RM160/day RM950/week | SUV RM250/day | MPV RM220/day | Premium RM350/day
Booking deposit: RM 100 (deducted from final bill). Hotel delivery: RM 50 add-on.
Pickup locations (free): KLIA, KL Sentral, Subang Airport (SZB), TBS
Required: customer_name, phone, license_no. Booking prefix: RNT. Min 1 day, max 7 days.
Reference: Wednesday, 8 Apr 2026

Set STATUS (success|vehicle_unavailable|date_conflict|invalid_request) and answer_text
Output: Python code in markdown block

Request: {question}"""

def generate_code(prompt):
    if not API_CONFIGURED:
        raise HTTPException(500, "API key not configured. Please set GOOGLE_API_KEY environment variable.")
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=genai.GenerationConfig(temperature=0.2))
    response = model.generate_content(prompt)
    return response.candidates[0].content.parts[0].text if response.candidates else ""

def extract_code(text):
    m = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else text.strip()

def execute_code(code, user_request):
    SAFE = {"Query": Query, "next_booking_id": next_booking_id, "get_daily_rate": get_daily_rate,
            "get_weekly_rate": get_weekly_rate, "calculate_rental_cost": calculate_rental_cost,
            "has_date_conflict": has_date_conflict, "datetime": datetime, "timedelta": timedelta,
            "user_request": user_request}
    LOCALS = {"db": db, "vehicles_tbl": vehicles_tbl, "bookings_tbl": bookings_tbl}
    stdout, old = io.StringIO(), sys.stdout
    sys.stdout = stdout
    err = None
    try:
        exec(code, SAFE, LOCALS)
    except Exception:
        err = traceback.format_exc()
    finally:
        sys.stdout = old
    return {"code": code, "error": err, "answer": LOCALS.get("answer_text", "No response"), "status": LOCALS.get("STATUS", "unknown")}

@app.get("/")
async def root():
    return FileResponse("demo.html")

@app.get("/api/status")
async def status():
    return {
        "message": "Kereta Sewa Jalan-jalan API",
        "version": "1.0.0",
        "docs": "/docs",
        "api_configured": API_CONFIGURED,
        "status": "API key required" if not API_CONFIGURED else "Ready"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        content = generate_code(PROMPT.format(question=request.message))
        result = execute_code(extract_code(content), request.message)
        if result["error"]:
            raise HTTPException(500, detail=f"Error: {result['error']}")
        return ChatResponse(answer=result["answer"], status=result["status"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/vehicles")
async def get_vehicles(status: Optional[str] = None, tier: Optional[str] = None):
    vehicles = [v for v in vehicles_tbl.all()
                if (not status or v.get("status") == status)
                and (not tier or v.get("tier") == tier)]
    return {"vehicles": vehicles, "total": len(vehicles)}

@app.get("/api/bookings")
async def get_bookings(status: Optional[str] = None, date: Optional[str] = None):
    bookings = [b for b in bookings_tbl.all()
                if (not status or b.get("status") == status)
                and (not date or b.get("pickup_date") == date)]
    return {"bookings": bookings, "total": len(bookings)}

@app.get("/api/locations")
async def get_locations():
    return {"pickup_locations": PICKUP_LOCATIONS, "hotel_delivery_fee_myr": HOTEL_DELIVERY_FEE}

FLEET_SPEC = [
    # (id_range_start, count, model, tier, plate_prefix)
    (1, 10, "Perodua Axia", "Economy", "WXY"),
    (11, 10, "Perodua Myvi", "Economy", "WAB"),
    (21, 10, "Honda City", "Compact", "WCD"),
    (31, 10, "Toyota Vios", "Compact", "WEF"),
    (41, 3, "Proton X50", "SUV", "WGH"),
    (44, 3, "Honda HR-V", "SUV", "WJK"),
    (47, 3, "Perodua Alza", "MPV", "WLM"),
    (50, 3, "Toyota Avanza", "MPV", "WNP"),
    (53, 2, "Toyota Camry", "Premium", "WQR"),
    (55, 2, "Honda Accord", "Premium", "WST"),
]

@app.on_event("startup")
async def startup():
    if not vehicles_tbl.all():
        for start, count, model, tier, prefix in FLEET_SPEC:
            for i in range(count):
                vid = start + i
                plate_num = 1000 + vid * 7
                vehicles_tbl.insert({
                    "vehicle_id": f"VHC{vid:03d}",
                    "model": model,
                    "tier": tier,
                    "plate_number": f"{prefix} {plate_num}",
                    "daily_rate_myr": get_daily_rate(tier),
                    "weekly_rate_myr": get_weekly_rate(tier),
                    "status": "available",
                    "location": "KL Sentral"
                })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
