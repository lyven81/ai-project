import requests
import random
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

AGENT_SYSTEM = """You are a personal assistant helping a property owner find a grass cutting service in Malaysia.
You communicate naturally, like a real person sending WhatsApp messages.
Keep messages short and conversational — 2 to 4 sentences maximum.
Use a natural mix of English and Malay where appropriate (e.g. "boleh", "terima kasih", "ok").
Never reveal you are an AI. Always speak as if you are the property owner."""


def call_llm(prompt, system=AGENT_SYSTEM):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=60
        )
        return response.json().get("response", "").strip()
    except Exception:
        return None


def generate_vendors(area):
    """Return 3 fixed vendor profiles with randomised phone numbers."""
    return [
        {
            "id": "vendor_1",
            "name": "Ahmad Landscaping",
            "number": f"+6011{random.randint(10000000, 99999999)}",
            "persona_id": 1
        },
        {
            "id": "vendor_2",
            "name": "Green Garden KL",
            "number": f"+6012{random.randint(10000000, 99999999)}",
            "persona_id": 2
        },
        {
            "id": "vendor_3",
            "name": "Pak Razif Garden",
            "number": f"+6013{random.randint(10000000, 99999999)}",
            "persona_id": 3
        },
    ]


def compose_outreach(area):
    result = call_llm(
        f"Write a short WhatsApp message to a grass cutting service provider asking if they "
        f"cover {area}. Keep it friendly and casual, 2 to 3 sentences max."
    )
    return result or (
        f"Hi, I'm looking for a grass cutting service in {area}. "
        "Do you provide this service in the area? Thanks!"
    )


def compose_quote_request():
    result = call_llm(
        "Write a short WhatsApp follow-up to a grass cutter who confirmed they cover the area. "
        "Say you will share a photo and video of the area. "
        "Ask for their rate and when they are available. 2 to 4 sentences, casual tone."
    )
    return result or (
        "Great, thanks for confirming! I'll send you a photo and video of the area. "
        "Can you let me know your rate and when you'd be available to do the job?"
    )


def compose_confirmation(vendor_name, rate, availability):
    result = call_llm(
        f"Write a WhatsApp confirmation message to a grass cutter named {vendor_name}. "
        f"Confirm: rate RM{rate}, service date {availability}, "
        "job is to cut all grass in the area as shown in the shared photo and video. "
        "3 to 4 sentences, friendly and clear."
    )
    return result or (
        f"Hi {vendor_name}, I'd like to confirm the booking. "
        f"Rate: RM{rate}, Date: {availability}. "
        "The job is to cut all grass in the circled area as shown in the photo and video. "
        "Looking forward to it, thank you!"
    )


def generate_vendor_completion_report(vendor_name):
    result = call_llm(
        f"You are {vendor_name}, a grass cutter. "
        "Write a short WhatsApp message saying the grass cutting job is done. "
        "Say all the grass has been cut and completion photos have been sent. "
        "Casual Malaysian tone, 2 to 3 sentences."
    )
    return result or (
        "Hi, sudah siap dah. All grass dah potong habis, "
        "gambar completion dah send. Sila check ya. Terima kasih!"
    )


def verify_completion(vendor_name, job_scope, completion_report):
    result = call_llm(
        f"You are an AI assistant verifying a completed grass cutting job.\n\n"
        f"Original job scope:\n{job_scope}\n\n"
        f"Completion report from provider:\n{completion_report}\n\n"
        "Write a 3 to 4 sentence verification report confirming whether the job matches "
        "the scope and whether payment should be made."
    )
    return result or (
        f"{vendor_name} has reported the grass cutting job as complete and submitted completion photos. "
        "Based on the completion report, the work appears to match the agreed job scope — "
        "all grass in the marked area has been cut as instructed. "
        "Payment of the agreed rate is recommended."
    )
