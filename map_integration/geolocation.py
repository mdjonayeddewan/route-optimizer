from __future__ import annotations

from typing import Any
import requests

try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None

from application.models import LiveLocation


def request_live_location() -> tuple[LiveLocation | None, str | None]:
    """Request browser geolocation using permission prompt.

    Returns:
        (location, error_message)
    """
    if get_geolocation is None:
        return None, "Dependency missing: streamlit-js-eval is not installed."

    payload: Any = get_geolocation(component_key="live_geolocation")

    if not isinstance(payload, dict):
        return None, "Waiting for browser geolocation response."

    # streamlit-js-eval returns a wrapper object: {"value": {...}, "dataType": "json"}
    value = payload.get("value", payload)
    if not isinstance(value, dict):
        return None, "Browser geolocation response format is invalid."

    # Error shape: {"error": {"code": ..., "message": ...}}
    error_obj = value.get("error")
    if isinstance(error_obj, dict):
        code = error_obj.get("code", "unknown")
        message = error_obj.get("message", "Unknown geolocation error")
        return None, f"Browser geolocation error ({code}): {message}"

    coords = value.get("coords", {})
    if not isinstance(coords, dict):
        return None, "No coordinates received from browser geolocation."

    lat = coords.get("latitude")
    lng = coords.get("longitude")
    if lat is None or lng is None:
        return None, "Latitude/longitude not found in browser geolocation response."

    try:
        return LiveLocation(latitude=float(lat), longitude=float(lng)), None
    except (TypeError, ValueError):
        return None, "Received invalid coordinate values from browser geolocation."


def request_ip_based_location(timeout: int = 10) -> LiveLocation | None:
    """Fallback approximate location by IP when browser geolocation is blocked.

    This is not GPS-accurate and should be used only as fallback.
    """
    url = "https://ipapi.co/json/"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        payload: Any = response.json()
    except requests.RequestException:
        return None

    if not isinstance(payload, dict):
        return None

    lat = payload.get("latitude")
    lng = payload.get("longitude")
    if lat is None or lng is None:
        return None

    try:
        return LiveLocation(latitude=float(lat), longitude=float(lng))
    except (TypeError, ValueError):
        return None
