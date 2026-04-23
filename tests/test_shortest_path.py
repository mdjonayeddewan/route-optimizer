from __future__ import annotations

from models.shortest_path import PathRequest, build_two_point_path
from src.api.geocoding import LocationPoint


def test_build_two_point_path_returns_lonlat_order() -> None:
    source = LocationPoint(name="A", latitude=24.0, longitude=88.0)
    destination = LocationPoint(name="B", latitude=25.0, longitude=89.0)
    request = PathRequest(source=source, destination=destination)

    points = build_two_point_path(request)
    assert points == [[88.0, 24.0], [89.0, 25.0]]
