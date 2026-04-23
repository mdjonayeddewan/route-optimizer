from __future__ import annotations

from typing import Sequence

import folium


def draw_route(fmap: folium.Map, route_geometry: dict, color: str = "blue") -> None:
    coordinates = route_geometry.get("coordinates", [])
    if not coordinates:
        return
    latlon = [(coord[1], coord[0]) for coord in coordinates]
    folium.PolyLine(latlon, color=color, weight=5, opacity=0.9).add_to(fmap)


def extract_bounds(points: Sequence[tuple[float, float]]) -> list[list[float]]:
    return [[lat, lon] for lat, lon in points]
