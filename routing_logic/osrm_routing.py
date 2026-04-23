from __future__ import annotations

import math
from typing import Literal

import requests

from application.models import RouteData

MAX_ALLOWED_OVERLAP_FOR_COMPARISON = 0.60


class RoutingError(RuntimeError):
    """Raised when routing provider fails."""


def _map_profile(profile: str) -> Literal["driving", "cycling", "walking"]:
    if profile.startswith("driving"):
        return "driving"
    if profile.startswith("cycling"):
        return "cycling"
    return "walking"


def _sampled_point_set(coordinates: list[list[float]]) -> set[tuple[float, float]]:
    if not coordinates:
        return set()
    sampled = coordinates[:: max(1, len(coordinates) // 120)]
    if sampled[-1] != coordinates[-1]:
        sampled.append(coordinates[-1])
    return {(round(point[0], 5), round(point[1], 5)) for point in sampled}


def _route_signature(coordinates: list[list[float]]) -> tuple:
    if not coordinates:
        return tuple()
    step = max(1, len(coordinates) // 24)
    sampled = coordinates[::step]
    if sampled[-1] != coordinates[-1]:
        sampled.append(coordinates[-1])
    return tuple((round(point[0], 5), round(point[1], 5)) for point in sampled)


def _overlap_ratio(points_a: set[tuple[float, float]], points_b: set[tuple[float, float]]) -> float:
    if not points_a or not points_b:
        return 0.0
    intersection = len(points_a.intersection(points_b))
    base = float(min(len(points_a), len(points_b)))
    if base == 0:
        return 0.0
    return intersection / base


def _routes_are_distinct(
    candidate_coords: list[list[float]],
    candidate_distance: float,
    existing: list[RouteData],
) -> bool:
    candidate_points = _sampled_point_set(candidate_coords)
    for route in existing:
        existing_coords = route.geometry.get("coordinates", [])
        if not existing_coords:
            continue
        overlap = _overlap_ratio(candidate_points, _sampled_point_set(existing_coords))
        distance_gap = abs(candidate_distance - route.distance_m) / max(candidate_distance, route.distance_m, 1.0)
        # If almost exactly the same geometry and nearly same distance, treat as duplicate.
        if overlap >= 0.95 and distance_gap <= 0.015:
            return False
    return True


def _routes_overlap_ratio(route_a: RouteData, route_b: RouteData) -> float:
    coords_a = route_a.geometry.get("coordinates", [])
    coords_b = route_b.geometry.get("coordinates", [])
    return _overlap_ratio(_sampled_point_set(coords_a), _sampled_point_set(coords_b))


def _select_diverse_economical_routes(candidates: list[RouteData], limit: int) -> list[RouteData]:
    """Pick top economical routes while enforcing pairwise diversity.

    Any selected pair must have overlap <= 60%.
    """
    selected: list[RouteData] = []
    for candidate in sorted(candidates, key=lambda item: (item.distance_m, item.duration_s)):
        if all(_routes_overlap_ratio(candidate, chosen) <= MAX_ALLOWED_OVERLAP_FOR_COMPARISON for chosen in selected):
            selected.append(candidate)
            if len(selected) >= limit:
                break
    return selected


def _fetch_osrm_routes(
    mapped_profile: str,
    coordinates: list[list[float]],
    alternatives: bool,
) -> list[dict]:
    coord_text = ";".join(f"{pt[0]},{pt[1]}" for pt in coordinates)
    url = f"https://router.project-osrm.org/route/v1/{mapped_profile}/{coord_text}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
        "alternatives": "true" if alternatives else "false",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "Ok" or not payload.get("routes"):
        return []
    return payload["routes"]


def _candidate_vias(origin_lonlat: list[float], destination_lonlat: list[float]) -> list[list[float] | None]:
    lat1, lon1 = origin_lonlat[1], origin_lonlat[0]
    lat2, lon2 = destination_lonlat[1], destination_lonlat[0]

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    norm = math.hypot(delta_lat, delta_lon)
    if norm == 0:
        return [None]

    perp_lat = -delta_lon / norm
    perp_lon = delta_lat / norm
    span = max(abs(delta_lat), abs(delta_lon), 0.002)

    dir_lat = delta_lat / norm
    dir_lon = delta_lon / norm

    vias: list[list[float] | None] = [None]
    fractions = [0.18, 0.28, 0.38, 0.5, 0.62, 0.72, 0.82]
    multipliers = [0.7, -0.7, 1.3, -1.3, 2.0, -2.0, 2.8, -2.8]
    along_multipliers = [0.0, 0.35, -0.35]
    for frac in fractions:
        base_lat = lat1 + delta_lat * frac
        base_lon = lon1 + delta_lon * frac
        for mul in multipliers:
            off = span * 0.20 * mul
            for along_mul in along_multipliers:
                along_off = span * 0.08 * along_mul
                via_lat = base_lat + perp_lat * off + dir_lat * along_off
                via_lon = base_lon + perp_lon * off + dir_lon * along_off
                vias.append([via_lon, via_lat])

    return vias


def _candidate_waypoint_sets(origin_lonlat: list[float], destination_lonlat: list[float]) -> list[list[list[float]]]:
    single_vias = [via for via in _candidate_vias(origin_lonlat, destination_lonlat) if via is not None]

    waypoint_sets: list[list[list[float]]] = []

    # Single-via waypoint sets.
    waypoint_sets.extend([[via] for via in single_vias])

    # Two-via waypoint sets on same side to force corridor-level diversity.
    # Use sparse pairing to avoid excessive API load.
    for i in range(0, max(0, len(single_vias) - 8), 8):
        left = single_vias[i]
        right = single_vias[i + 4]
        waypoint_sets.append([left, right])

    return waypoint_sets


def build_route(origin_lonlat: list[float], destination_lonlat: list[float], profile: str = "driving-car") -> RouteData:
    routes = build_route_alternatives(origin_lonlat, destination_lonlat, profile=profile, limit=1)
    if not routes:
        raise RoutingError("No drivable road route found between current location and destination.")
    return routes[0]


def build_route_alternatives(
    origin_lonlat: list[float],
    destination_lonlat: list[float],
    profile: str = "driving-car",
    limit: int = 3,
) -> list[RouteData]:
    """Return up to `limit` distinct road routes ranked by road distance.

    We generate a direct route plus small midpoint detours to produce visibly
    different road candidates even when the routing backend returns limited
    native alternatives.
    """
    mapped_profile = _map_profile(profile)
    waypoint_sets = _candidate_waypoint_sets(origin_lonlat, destination_lonlat)

    routes: list[RouteData] = []
    seen_signatures: set[tuple] = set()
    max_queries = 72
    queries_done = 0

    # 1) Native alternatives from OSRM for the direct OD pair.
    try:
        for route in _fetch_osrm_routes(mapped_profile, [origin_lonlat, destination_lonlat], alternatives=True):
            geometry = route.get("geometry")
            if not geometry:
                continue
            coordinates = geometry.get("coordinates", [])
            signature = _route_signature(coordinates)
            distance_m = float(route.get("distance", 0.0))
            if not signature or signature in seen_signatures:
                continue
            if not _routes_are_distinct(coordinates, distance_m, routes):
                continue
            seen_signatures.add(signature)
            routes.append(
                RouteData(
                    distance_m=distance_m,
                    duration_s=float(route.get("duration", 0.0)),
                    geometry=geometry,
                    provider="osrm",
                )
            )
    except requests.RequestException:
        pass
    queries_done += 1

    # 2) Extra waypoint probing to discover additional valid road corridors.
    for waypoints in waypoint_sets:
        if queries_done >= max_queries:
            break
        coordinates = [origin_lonlat]
        coordinates.extend(waypoints)
        coordinates.append(destination_lonlat)

        try:
            fetched = _fetch_osrm_routes(mapped_profile, coordinates, alternatives=True)
        except requests.RequestException:
            queries_done += 1
            continue
        queries_done += 1
        if not fetched:
            continue

        for route in fetched:
            geometry = route.get("geometry")
            if not geometry:
                continue
            geometry_coords = geometry.get("coordinates", [])

            signature = _route_signature(geometry_coords)
            if signature in seen_signatures:
                continue

            distance_m = float(route.get("distance", 0.0))
            if not _routes_are_distinct(geometry_coords, distance_m, routes):
                continue

            seen_signatures.add(signature)

            routes.append(
                RouteData(
                    distance_m=distance_m,
                    duration_s=float(route.get("duration", 0.0)),
                    geometry=geometry,
                    provider="osrm",
                )
            )

    routes = _select_diverse_economical_routes(routes, limit=limit)
    if not routes:
        raise RoutingError("No drivable road route found between current location and destination.")

    return routes
