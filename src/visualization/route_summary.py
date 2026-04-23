from __future__ import annotations

from src.utils.helpers import meters_to_km, seconds_to_minutes


def generate_route_summary(distance_m: float, duration_s: float) -> str:
    distance_km = meters_to_km(distance_m)
    duration_min = seconds_to_minutes(duration_s)
    return f"Total distance: {distance_km:.2f} km | Estimated duration: {duration_min:.2f} minutes"
