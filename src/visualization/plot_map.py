from __future__ import annotations

import folium


def create_base_map(center: tuple[float, float], zoom: int) -> folium.Map:
    return folium.Map(location=center, zoom_start=zoom, control_scale=True)


def add_marker(fmap: folium.Map, latlon: tuple[float, float], popup: str, color: str = "blue", icon: str = "map-marker") -> None:
    folium.Marker(
        location=latlon,
        popup=popup,
        icon=folium.Icon(color=color, icon=icon, prefix="fa"),
    ).add_to(fmap)
