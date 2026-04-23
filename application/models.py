from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LiveLocation:
    latitude: float
    longitude: float

    @property
    def latlon(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)

    @property
    def lonlat(self) -> list[float]:
        return [self.longitude, self.latitude]


@dataclass(slots=True)
class PlaceSuggestion:
    display_name: str
    latitude: float
    longitude: float

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def latlon(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)

    @property
    def lonlat(self) -> list[float]:
        return [self.longitude, self.latitude]


@dataclass(slots=True)
class RouteData:
    distance_m: float
    duration_s: float
    geometry: dict
    provider: str
