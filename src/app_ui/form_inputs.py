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
    """Render live autocomplete with a selectable suggestion dropdown and persisted selection."""
    query = st.text_input(label, key=text_key, placeholder="Type place, road, landmark...")

    if query.strip():
        st.session_state[f"{text_key}_query"] = query.strip()

    if suggestions:
        options = ["-- select a suggestion --"] + [item.display_name for item in suggestions]
        selected_label = st.selectbox(
            f"{label} suggestions",
            options=options,
            key=f"{selected_key}_selectbox",
        )
        if selected_label != options[0]:
            for item in suggestions:
                if item.display_name == selected_label:
                    st.session_state[selected_key] = _serialize_place(item)
                    break
    else:
        st.caption("Type at least 3 characters to see live suggestions.")

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
