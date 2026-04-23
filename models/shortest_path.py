from __future__ import annotations

from dataclasses import dataclass

from src.api.geocoding import LocationPoint


@dataclass(slots=True)
class PathRequest:
    source: LocationPoint
    destination: LocationPoint


def build_two_point_path(request: PathRequest) -> list[list[float]]:
    """Return ORS-compatible [lon, lat] route coordinates."""
    return [request.source.lonlat, request.destination.lonlat]
