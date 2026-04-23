from __future__ import annotations

from typing import Literal

import requests

from src.api.directions import RouteResult


class OSRMClientError(RuntimeError):
    """Raised when OSRM request fails."""


def _map_profile(ors_profile: str) -> Literal["driving", "cycling", "walking"]:
    if ors_profile.startswith("driving"):
        return "driving"
    if ors_profile.startswith("cycling"):
        return "cycling"
    return "walking"


def get_osrm_route(points_lonlat: list[list[float]], ors_profile: str, timeout: int = 15) -> RouteResult:
    """Fetch route from public OSRM endpoint as a no-key fallback."""
    if len(points_lonlat) < 2:
        raise OSRMClientError("At least two points are required for routing.")

    profile = _map_profile(ors_profile)
    coordinates = ";".join(f"{p[0]},{p[1]}" for p in points_lonlat)
    url = f"https://router.project-osrm.org/route/v1/{profile}/{coordinates}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise OSRMClientError(f"OSRM request failed: {exc}") from exc

    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise OSRMClientError("OSRM returned no valid route.")

    route = payload["routes"][0]
    geometry = route.get("geometry")
    if not geometry:
        raise OSRMClientError("OSRM route geometry is missing.")

    return RouteResult(
        distance_m=float(route.get("distance", 0.0)),
        duration_s=float(route.get("duration", 0.0)),
        geometry=geometry,
    )
