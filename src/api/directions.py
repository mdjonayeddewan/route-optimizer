from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.api.ors_client import ORSClient


@dataclass(slots=True)
class RouteResult:
    distance_m: float
    duration_s: float
    geometry: dict[str, Any]


def extract_route_result(response: dict[str, Any]) -> RouteResult:
    features = response.get("features", [])
    if not features:
        raise ValueError("No route found in API response.")

    feature = features[0]
    properties = feature.get("properties", {})
    summary = properties.get("summary", {})
    geometry = feature.get("geometry", {})

    if not geometry:
        raise ValueError("Route geometry missing in API response.")

    return RouteResult(
        distance_m=float(summary.get("distance", 0.0)),
        duration_s=float(summary.get("duration", 0.0)),
        geometry=geometry,
    )


def get_route(client: ORSClient, points_lonlat: list[list[float]], profile: str) -> RouteResult:
    response = client.directions(coordinates=points_lonlat, profile=profile)
    return extract_route_result(response)
