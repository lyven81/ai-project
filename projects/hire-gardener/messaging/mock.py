import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

PERSONAS = {
    1: {
        "system": (
            "You are Ahmad, owner of Ahmad Landscaping in Kuala Lumpur. "
            "You speak in friendly Malay-English mix — use words like 'boleh', 'ok bro', 'insyaAllah', 'nanti'. "
            "You provide grass cutting services and charge RM150 to RM180. "
            "You are available Monday or Tuesday next week."
        ),
        "fallbacks": {
            "outreach": "Ya boleh, saya ada service kat kawasan tu. Nak buat bila?",
            "quoting": "Ok dah tengok gambar tu. Boleh buat RM160, insyaAllah Isnin minggu depan ok?",
            "confirmation": "Ok confirmed! Isnin minggu depan ya. Nanti saya gi awal pagi. Terima kasih!"
        },
        "rate": "160",
        "availability": "Monday next week",
        "declines": False
    },
    2: {
        "system": (
            "You are Sarah from Green Garden KL. "
            "You speak professional English. You are prompt and detailed in your replies. "
            "You charge RM200 to RM220 per standard plot. You are available this Saturday morning."
        ),
        "fallbacks": {
            "outreach": "Yes, we do cover that area. What is the approximate size of the plot?",
            "quoting": "Thank you for the photos! We can do this for RM210. We are available this Saturday morning.",
            "confirmation": "Confirmed! We will be there Saturday morning. Thank you for choosing Green Garden KL!"
        },
        "rate": "210",
        "availability": "This Saturday",
        "declines": False
    },
    3: {
        "system": (
            "You are Razif, a solo gardener based in Shah Alam. "
            "You speak mostly Malay with some English. "
            "For the first message (outreach stage), reply positively and ask about the area. "
            "For the quoting stage, apologise and say the area is too far from Shah Alam — you cannot take the job."
        ),
        "fallbacks": {
            "outreach": "Ok boleh, kawasan mana tu? Saya tengok dulu.",
            "quoting": "Eh maaf ya, dah tengok location tu. Jauh sangat dari Shah Alam, tak boleh la. Sorry sangat-sangat.",
            "confirmation": "Ok confirmed!"
        },
        "rate": None,
        "availability": None,
        "declines": True
    }
}


def call_llm(prompt, system):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.85}
            },
            timeout=60
        )
        return response.json().get("response", "").strip()
    except Exception:
        return None


def get_vendor_response(vendor: dict, message: str, stage: str) -> tuple:
    """
    Simulate a vendor reply using Llama3 with persona prompts.

    Returns:
        (reply_text: str, quote_data: dict | None)
        quote_data is only populated for stage == 'quoting'.
    """
    persona_id = vendor.get("persona_id", 1)
    persona = PERSONAS[persona_id]

    if stage == "quoting" and persona["declines"]:
        prompt = (
            f"Reply to this WhatsApp message. You are declining because the area is too far "
            f"from your base in Shah Alam. Be polite and apologetic: '{message}'"
        )
    else:
        prompt = f"Reply naturally to this WhatsApp message in your character: '{message}'"

    reply = call_llm(prompt, persona["system"]) or persona["fallbacks"].get(stage, "Ok, noted.")

    if stage == "quoting":
        if persona["declines"]:
            quote_data = {"declined": True, "rate": None, "availability": None}
        else:
            quote_data = {
                "declined": False,
                "rate": persona["rate"],
                "availability": persona["availability"]
            }
        return reply, quote_data

    return reply, None
