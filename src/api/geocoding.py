from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from geopy.point import Point

from src.utils.validators import validate_coordinate_pair


@dataclass(slots=True)
class LocationPoint:
    name: str
    latitude: float
    longitude: float

    @property
    def latlon(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)

    @property
    def lonlat(self) -> list[float]:
        return [self.longitude, self.latitude]


def parse_latlon_text(value: str) -> Optional[tuple[float, float]]:
    parts = [x.strip() for x in value.split(",")]
    if len(parts) != 2:
        return None
    try:
        lat = float(parts[0])
        lon = float(parts[1])
        validate_coordinate_pair(lat, lon)
    except (ValueError, TypeError):
        return None
    return lat, lon


def geocode_place_name(place_name: str, timeout: int = 10) -> LocationPoint:
    geolocator = Nominatim(user_agent="route_optimizer_app")

    # Bias lookup to Bangladesh and Rajshahi region to avoid unrelated global matches.
    rajshahi_viewbox = [Point(24.50, 88.45), Point(24.20, 88.75)]
    candidate_queries = [
        place_name,
        f"{place_name}, Rajshahi, Bangladesh",
        f"{place_name}, Bangladesh",
    ]

    result = None
    try:
        for query in candidate_queries:
            result = geolocator.geocode(
                query,
                timeout=timeout,
                country_codes="bd",
                exactly_one=True,
                viewbox=rajshahi_viewbox,
                bounded=False,
            )
            if result is not None:
                break
    except GeocoderServiceError as exc:
        raise ValueError(f"Geocoding service unavailable: {exc}") from exc

    if result is None:
        raise ValueError(
            f"Unable to geocode place: {place_name}. Please provide a more specific name or use 'lat,lon'."
        )

    latitude = float(result.latitude)
    longitude = float(result.longitude)
    validate_coordinate_pair(latitude, longitude)
    return LocationPoint(name=place_name, latitude=latitude, longitude=longitude)


def resolve_location_input(raw_input: str, default_name: str) -> LocationPoint:
    """Resolve either 'lat,lon' or place name to a LocationPoint."""
    parsed = parse_latlon_text(raw_input)
    if parsed is not None:
        return LocationPoint(name=default_name, latitude=parsed[0], longitude=parsed[1])
    return geocode_place_name(raw_input)
