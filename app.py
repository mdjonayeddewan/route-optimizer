from __future__ import annotations

from pathlib import Path

import streamlit as st

from application.models import PlaceSuggestion
from map_integration.geolocation import request_ip_based_location, request_live_location
from map_integration.map_renderer import render_live_route_map_alternatives
from map_integration.search import SearchError, fetch_place_suggestions
from routing_logic.osrm_routing import RoutingError, build_route_alternatives
from src.app_ui.form_inputs import render_live_autocomplete_selector, render_route_metrics
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger


ROOT = Path(__file__).resolve().parent


def _sample_route_points(coordinates: list[list[float]], max_points: int = 140) -> set[tuple[float, float]]:
    if not coordinates:
        return set()
    step = max(1, len(coordinates) // max_points)
    sampled = coordinates[::step]
    if sampled[-1] != coordinates[-1]:
        sampled.append(coordinates[-1])
    return {(round(point[0], 5), round(point[1], 5)) for point in sampled}


def _overlap_percent(coords_a: list[list[float]], coords_b: list[list[float]]) -> float:
    points_a = _sample_route_points(coords_a)
    points_b = _sample_route_points(coords_b)
    if not points_a or not points_b:
        return 0.0
    common = len(points_a.intersection(points_b))
    base = min(len(points_a), len(points_b))
    if base <= 0:
        return 0.0
    return (common / base) * 100.0


def main() -> None:
    app_config = FileHandler.read_yaml(ROOT / "config" / "config.yaml")
    ga_config_raw = FileHandler.read_yaml(ROOT / "config" / "routes_config.yaml")

    logger = setup_logger(
        name="route_optimizer",
        level=app_config["logging"]["level"],
        file_path=str(ROOT / app_config["logging"]["file_path"]),
    )
    logger.info("App startup")

    st.set_page_config(page_title=app_config["app"]["title"], layout="wide")
    st.title(app_config["app"]["title"])
    st.caption("Live current location, dynamic destination search, and real-time road routing.")

    profile = app_config["routing"]["profile"]
    default_zoom = int(app_config["map"]["default_zoom"])

    st.subheader("Live Route Finder")
    st.info("Choose source mode, then select source and destination from live suggestions, and generate road route.")

    current_location = st.session_state.get("current_location")
    geolocation_error = None

    detect_col, reset_col = st.columns(2)
    detect_clicked = detect_col.button("Detect My Location")
    reset_clicked = reset_col.button("Reset Location")

    if detect_clicked:
        st.session_state["location_request_pending"] = True
        st.rerun()

    if reset_clicked:
        st.session_state.pop("current_location", None)
        st.session_state["location_request_pending"] = False
        st.session_state.pop("live_route_result", None)
        st.rerun()

    if st.session_state.get("location_request_pending", False) or current_location is not None:
        live_location, geolocation_error = request_live_location()
        if live_location is not None:
            current_location = live_location
            st.session_state["current_location"] = live_location
            st.session_state["location_request_pending"] = False

    if current_location is None:
        st.warning("Click 'Detect My Location' to request browser permission and detect your current location.")
        if geolocation_error:
            st.caption(f"Geolocation details: {geolocation_error}")
        st.caption("If prompt does not appear, check browser site settings for location permission on localhost and then reload.")
        st.caption("If dependency is missing: python -m pip install streamlit-js-eval")
        if st.button("Use Approximate IP Location"):
            ip_location = request_ip_based_location()
            if ip_location is None:
                st.error("Unable to detect approximate location from IP.")
            else:
                st.session_state["current_location"] = ip_location
                st.info("Using approximate IP-based location (less accurate than device GPS).")
                st.rerun()
        return

    st.success(f"Current location detected: {current_location.latitude:.6f}, {current_location.longitude:.6f}")

    with st.expander("Current Location Details", expanded=False):
        st.write({
            "name": "Detected current location",
            "latitude": current_location.latitude,
            "longitude": current_location.longitude,
        })

    source_mode = st.radio(
        "Source mode",
        options=["Use Current Live Location", "Search Custom Source"],
        horizontal=True,
    )

    origin: PlaceSuggestion | None = None
    if source_mode == "Use Current Live Location":
        origin = PlaceSuggestion(
            display_name="Current Live Location",
            latitude=current_location.latitude,
            longitude=current_location.longitude,
        )
        st.caption("Source selected from live device location.")
    else:
        source_suggestions: list[PlaceSuggestion] = []
        source_query = st.session_state.get("source_query", "")
        if isinstance(source_query, str) and source_query.strip():
            try:
                source_suggestions = fetch_place_suggestions(source_query)
            except SearchError as exc:
                st.error(str(exc))

        origin = render_live_autocomplete_selector(
            label="Search source",
            text_key="source_query",
            selected_key="selected_source",
            suggestions=source_suggestions,
        )

    destination_suggestions: list[PlaceSuggestion] = []
    destination_query = st.session_state.get("destination_query", "")
    if isinstance(destination_query, str) and destination_query.strip():
        try:
            destination_suggestions = fetch_place_suggestions(destination_query)
        except SearchError as exc:
            st.error(str(exc))

    destination = render_live_autocomplete_selector(
        label="Search destination",
        text_key="destination_query",
        selected_key="selected_destination",
        suggestions=destination_suggestions,
    )

    if st.button("Generate Live Route", type="primary"):
        if origin is None:
            st.error("Please select a source from live suggestions.")
        elif destination is None:
            st.error("Please select a destination from live suggestions.")
        else:
            try:
                routes = build_route_alternatives(origin.lonlat, destination.lonlat, profile=profile, limit=3)
                st.session_state["live_route_result"] = {
                    "origin": origin,
                    "destination": destination,
                    "routes": routes,
                }
            except RoutingError as exc:
                logger.exception("Live routing failed")
                st.error(str(exc))

    cached = st.session_state.get("live_route_result")
    if cached is not None:
        routes = cached["routes"]
        best_route = routes[0]
        render_route_metrics(best_route)
        st.info(f"Routing provider: {best_route.provider.upper()} (OpenStreetMap ecosystem)")
        st.caption("Top 3 cheapest road routes are shown in different colors.")
        if len(routes) < 3:
            st.warning(f"Only {len(routes)} distinct road route(s) were available from the routing service.")

        st.subheader("Top-3 Route Ranking Table")
        colors = ["Blue", "Red", "Green"]
        best_distance = max(best_route.distance_m, 1.0)
        ranking_rows: list[dict[str, str]] = []
        for idx, route in enumerate(routes[:3]):
            ranking_rows.append(
                {
                    "Rank": str(idx + 1),
                    "Color (Blue/Red/Green)": colors[idx],
                    "Distance (km)": f"{route.distance_m / 1000:.2f}",
                    "Estimated Time (min)": f"{route.duration_s / 60:.2f}",
                    "Distance vs Best (%)": f"{((route.distance_m / best_distance) - 1.0) * 100.0:+.2f}%",
                }
            )
        st.table(ranking_rows)

        st.subheader("Route Diversity Panel")
        diversity_rows: list[dict[str, str]] = []
        best_coords = best_route.geometry.get("coordinates", [])
        for idx, route in enumerate(routes[:3]):
            coords = route.geometry.get("coordinates", [])
            overlap = 100.0 if idx == 0 else _overlap_percent(best_coords, coords)
            diversity_rows.append(
                {
                    "Route": f"Route {idx + 1}",
                    "Overlap With Route 1 (%)": f"{overlap:.1f}%",
                    "Distinctness (%)": f"{max(0.0, 100.0 - overlap):.1f}%",
                }
            )
        st.table(diversity_rows)

        st.subheader("Pairwise Overlap Matrix")
        st.caption("Route comparison is constrained so selected routes cannot exceed 60% pairwise overlap.")
        pairwise_rows: list[dict[str, str]] = []
        for i, route_i in enumerate(routes[:3]):
            row: dict[str, str] = {"Route": f"Route {i + 1}"}
            coords_i = route_i.geometry.get("coordinates", [])
            for j, route_j in enumerate(routes[:3]):
                coords_j = route_j.geometry.get("coordinates", [])
                overlap_ij = _overlap_percent(coords_i, coords_j)
                row[f"Route {j + 1}"] = f"{overlap_ij:.1f}%"
            pairwise_rows.append(row)
        st.table(pairwise_rows)

        render_live_route_map_alternatives(
            current=cached["origin"],
            destination=cached["destination"],
            routes=routes,
            default_zoom=default_zoom,
        )

        report_text = (
            f"Provider: {best_route.provider}\n"
            f"Best Distance (m): {best_route.distance_m:.2f}\n"
            f"Best Duration (s): {best_route.duration_s:.2f}\n"
            f"Origin Name: {cached['origin'].name}\n"
            f"Origin: {cached['origin'].latitude:.6f}, {cached['origin'].longitude:.6f}\n"
            f"Destination Name: {cached['destination'].name}\n"
            f"Destination: {cached['destination'].latitude:.6f}, {cached['destination'].longitude:.6f}\n"
        )
        FileHandler.write_text(ROOT / app_config["paths"]["route_report_txt"], report_text)


if __name__ == "__main__":
    main()
