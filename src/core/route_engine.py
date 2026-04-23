from __future__ import annotations

from dataclasses import dataclass

from models.fitness_function import haversine_km
from models.shortest_path import PathRequest, build_two_point_path
from src.api.directions import RouteResult, get_route
from src.api.geocoding import LocationPoint, resolve_location_input
from src.api.osrm_client import OSRMClientError, get_osrm_route
from src.api.ors_client import ORSClient, ORSClientError


@dataclass(slots=True)
class SingleRouteOutput:
    source: LocationPoint
    destination: LocationPoint
    route: RouteResult
    used_fallback: bool
    route_provider: str


def run_single_route(
    source_input: str,
    destination_input: str,
    profile: str,
    api_key: str | None = None,
    use_haversine_fallback: bool = True,
) -> SingleRouteOutput:
    source = resolve_location_input(source_input, default_name="Source")
    destination = resolve_location_input(destination_input, default_name="Destination")

    request = PathRequest(source=source, destination=destination)
    points_lonlat = build_two_point_path(request)

    try:
        client = ORSClient(api_key=api_key)
        route = get_route(client=client, points_lonlat=points_lonlat, profile=profile)
        return SingleRouteOutput(
            source=source,
            destination=destination,
            route=route,
            used_fallback=False,
            route_provider="ors",
        )
    except ORSClientError:
        if not use_haversine_fallback:
            raise
        try:
            route = get_osrm_route(points_lonlat=points_lonlat, ors_profile=profile)
            return SingleRouteOutput(
                source=source,
                destination=destination,
                route=route,
                used_fallback=True,
                route_provider="osrm",
            )
        except OSRMClientError:
            distance_km = haversine_km(source.latlon, destination.latlon)
            avg_speed_kmph = 35.0
            duration_h = distance_km / avg_speed_kmph if avg_speed_kmph > 0 else 0.0
            route = RouteResult(
                distance_m=distance_km * 1000.0,
                duration_s=duration_h * 3600.0,
                geometry={
                    "type": "LineString",
                    "coordinates": points_lonlat,
                },
            )
            return SingleRouteOutput(
                source=source,
                destination=destination,
                route=route,
                used_fallback=True,
                route_provider="haversine",
            )
