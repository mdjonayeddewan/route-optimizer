from __future__ import annotations

import streamlit as st

try:
    import folium
    from streamlit_folium import st_folium
except ModuleNotFoundError:
    folium = None
    st_folium = None

from application.models import PlaceSuggestion, RouteData


def _ensure_map_dependencies() -> bool:
    if folium is None or st_folium is None:
        st.error(
            "Map dependencies are missing on this deployment environment. "
            "Please confirm requirements installation includes folium and streamlit-folium."
        )
        return False
    return True


def render_live_route_map(
    current: PlaceSuggestion,
    destination: PlaceSuggestion,
    route: RouteData,
    default_zoom: int,
) -> None:
    if not _ensure_map_dependencies():
        return

    center = (
        (current.latitude + destination.latitude) / 2,
        (current.longitude + destination.longitude) / 2,
    )
    fmap = folium.Map(location=center, zoom_start=default_zoom, control_scale=True)

    folium.Marker(
        current.latlon,
        popup=f"Source: {current.display_name}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(fmap)

    folium.Marker(
        destination.latlon,
        popup="Destination",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(fmap)

    coordinates = route.geometry.get("coordinates", [])
    latlon = [(coord[1], coord[0]) for coord in coordinates]
    folium.PolyLine(latlon, color="#0077cc", weight=6, opacity=0.9).add_to(fmap)

    if latlon:
        fmap.fit_bounds([current.latlon, destination.latlon])

    st_folium(fmap, width=None, height=520)


def render_live_route_map_alternatives(
    current: PlaceSuggestion,
    destination: PlaceSuggestion,
    routes: list[RouteData],
    default_zoom: int,
) -> None:
    if not _ensure_map_dependencies():
        return

    center = (
        (current.latitude + destination.latitude) / 2,
        (current.longitude + destination.longitude) / 2,
    )
    fmap = folium.Map(location=center, zoom_start=default_zoom, control_scale=True)

    folium.Marker(
        current.latlon,
        popup=f"Source: {current.display_name}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(fmap)

    folium.Marker(
        destination.latlon,
        popup=f"Destination: {destination.display_name}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(fmap)

    colors = ["#1f77b4", "#d62728", "#2ca02c"]
    route_bounds: list[tuple[float, float]] = [current.latlon, destination.latlon]
    for idx, route in enumerate(routes[:3]):
        coordinates = route.geometry.get("coordinates", [])
        latlon = [(coord[1], coord[0]) for coord in coordinates]
        route_bounds.extend(latlon)
        folium.PolyLine(
            latlon,
            color=colors[idx % len(colors)],
            weight=7,
            opacity=0.92,
            smooth_factor=2,
            tooltip=f"Route {idx + 1}: {route.distance_m / 1000:.2f} km | {route.duration_s / 60:.2f} min",
        ).add_to(fmap)

        if latlon:
            folium.Marker(
                latlon[len(latlon) // 2],
                icon=folium.DivIcon(
                    html=f'<div style="font-size:12px;font-weight:700;color:{colors[idx % len(colors)]};background:#ffffffdd;border:1px solid {colors[idx % len(colors)]};padding:2px 6px;border-radius:8px;">R{idx + 1}</div>'
                ),
            ).add_to(fmap)

    fmap.fit_bounds(route_bounds)
    st_folium(fmap, width=None, height=520)
