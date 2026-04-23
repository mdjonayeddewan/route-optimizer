from __future__ import annotations

import streamlit as st

from application.models import PlaceSuggestion, RouteData
from src.utils.helpers import meters_to_km, seconds_to_minutes


def _serialize_place(place: PlaceSuggestion) -> dict[str, float | str]:
    return {
        "display_name": place.display_name,
        "latitude": place.latitude,
        "longitude": place.longitude,
    }


def _deserialize_place(payload: dict[str, float | str]) -> PlaceSuggestion | None:
    try:
        return PlaceSuggestion(
            display_name=str(payload["display_name"]),
            latitude=float(payload["latitude"]),
            longitude=float(payload["longitude"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def render_live_autocomplete_selector(
    label: str,
    text_key: str,
    selected_key: str,
    suggestions: list[PlaceSuggestion],
) -> PlaceSuggestion | None:
    """Render live autocomplete with clickable suggestions (no dropdown)."""
    st.text_input(label, key=text_key, placeholder="Type place, road, landmark...")

    if suggestions:
        st.caption("Live suggestions:")
        for idx, item in enumerate(suggestions):
            btn_label = item.display_name
            if len(btn_label) > 95:
                btn_label = f"{btn_label[:95]}..."
            if st.button(btn_label, key=f"{selected_key}_suggestion_{idx}"):
                st.session_state[selected_key] = _serialize_place(item)

    selected_payload = st.session_state.get(selected_key)
    if isinstance(selected_payload, dict):
        selected = _deserialize_place(selected_payload)
        if selected is not None:
            st.success(f"Selected: {selected.display_name}")
            return selected

    return None


def render_route_metrics(route: RouteData) -> None:
    distance_km = meters_to_km(route.distance_m)
    duration_min = seconds_to_minutes(route.duration_s)
    col1, col2 = st.columns(2)
    col1.metric("Road Distance (km)", f"{distance_km:.2f}")
    col2.metric("Estimated Duration (min)", f"{duration_min:.2f}")
