from __future__ import annotations

from typing import Sequence

import folium
from streamlit_folium import st_folium


def render_map(fmap: folium.Map, height: int = 500) -> None:
    st_folium(fmap, width=None, height=height)


def add_route_polyline(fmap: folium.Map, coordinates_lonlat: Sequence[Sequence[float]], color: str = "blue") -> None:
    latlon = [(coord[1], coord[0]) for coord in coordinates_lonlat]
    folium.PolyLine(latlon, color=color, weight=5, opacity=0.8).add_to(fmap)


def fit_map_to_points(fmap: folium.Map, points_latlon: Sequence[tuple[float, float]]) -> None:
    if not points_latlon:
        return
    fmap.fit_bounds(points_latlon)
