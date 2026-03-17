"""
Real WhatsApp Cloud API integration (used when MODE=real).

To activate:
1. Set MODE=real in your .env file
2. Add your WHATSAPP_API_TOKEN and WHATSAPP_PHONE_NUMBER_ID
3. Set up a public webhook to receive incoming replies (ngrok or cloud server)
4. Implement the webhook handler in your server to call this module
"""

import requests
from config import WHATSAPP_API_TOKEN, WHATSAPP_PHONE_NUMBER_ID

BASE_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}"


def _headers():
    return {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }


def _send_text(to_number: str, message: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(f"{BASE_URL}/messages", json=payload, headers=_headers())
    return response.json()


def get_vendor_response(vendor: dict, message: str, stage: str) -> tuple:
    """
    Send a WhatsApp message to the vendor and wait for their reply via webhook.

    Returns:
        (reply_text: str, quote_data: dict | None)

    NOTE: This stub sends the outbound message but does not yet receive replies automatically.
    You need a webhook endpoint to capture incoming replies and feed them back into the workflow.
    See the user guide for webhook setup instructions.
    """
    to_number = vendor.get("number", "")
    _send_text(to_number, message)

    raise NotImplementedError(
        "Real mode requires a webhook endpoint to receive vendor replies. "
        "Set up an ngrok tunnel or cloud server, then implement the webhook handler. "
        "See 'user guide.md' for full setup instructions."
    )
