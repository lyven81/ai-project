from agent import (
    generate_vendors,
    compose_outreach,
    compose_quote_request,
    compose_confirmation,
    generate_vendor_completion_report,
    verify_completion
)
from messaging import get_vendor_response


def stage_1_discover(area: str) -> list:
    """Return a list of 3 vendor dicts for the given area."""
    return generate_vendors(area)


def stage_2_outreach(vendors: list, area: str) -> dict:
    """
    Send initial outreach to all vendors.
    Returns conversations dict: {vendor_id: [message_dicts]}
    """
    conversations = {v["id"]: [] for v in vendors}

    for vendor in vendors:
        msg = compose_outreach(area)
        conversations[vendor["id"]].append({"role": "agent", "text": msg})

        reply, _ = get_vendor_response(vendor, msg, "outreach")
        conversations[vendor["id"]].append({"role": "vendor", "text": reply})

    return conversations


def stage_3_quote(vendors: list, conversations: dict) -> tuple:
    """
    Send quote request with media to all vendors.
    Returns (conversations, quotes).
    quotes is a list of dicts with: vendor_id, vendor_name, number, persona_id,
    declined, rate, availability.
    """
    quotes = []

    for vendor in vendors:
        msg = compose_quote_request()

        # Display version includes media indicators
        display_msg = msg + "\n\n📷 [Area photo attached]\n🎥 [Area video attached]"
        conversations[vendor["id"]].append({
            "role": "agent",
            "text": display_msg,
            "has_media": True
        })

        # LLM gets the clean message
        reply, quote_data = get_vendor_response(vendor, msg, "quoting")
        conversations[vendor["id"]].append({"role": "vendor", "text": reply})

        quotes.append({
            **quote_data,
            "vendor_id": vendor["id"],
            "vendor_name": vendor["name"],
            "number": vendor["number"],
            "persona_id": vendor.get("persona_id", 1)
        })

    return conversations, quotes


def stage_5_confirm(selected_vendor: dict, conversations: dict) -> tuple:
    """
    Send confirmation and job scope to the selected vendor.
    Returns (conversations, job_scope_text).
    """
    msg = compose_confirmation(
        selected_vendor["vendor_name"],
        selected_vendor["rate"],
        selected_vendor["availability"]
    )

    vendor_id = selected_vendor["vendor_id"]
    conversations[vendor_id].append({"role": "agent", "text": msg})

    reply, _ = get_vendor_response(
        {
            "id": vendor_id,
            "name": selected_vendor["vendor_name"],
            "persona_id": selected_vendor.get("persona_id", 1)
        },
        msg,
        "confirmation"
    )
    conversations[vendor_id].append({"role": "vendor", "text": reply})

    job_scope = (
        f"Grass cutting at the marked area as shown in the shared photo and video.\n"
        f"Provider: {selected_vendor['vendor_name']}\n"
        f"Rate: RM {selected_vendor['rate']}\n"
        f"Service Date: {selected_vendor['availability']}\n"
        f"Scope: Cut all grass in the circled area completely and cleanly."
    )

    return conversations, job_scope


def stage_6_verify(selected_vendor: dict, job_scope: str) -> str:
    """
    Simulate provider completion report and run AI verification.
    Returns verification report text.
    """
    completion_report = generate_vendor_completion_report(selected_vendor["vendor_name"])
    report = verify_completion(selected_vendor["vendor_name"], job_scope, completion_report)
    return report
