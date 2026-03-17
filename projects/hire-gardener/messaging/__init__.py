from config import MODE

if MODE == "real":
    from .whatsapp import get_vendor_response
else:
    from .mock import get_vendor_response

__all__ = ["get_vendor_response"]
