from __future__ import annotations

from typing import Iterable

import pandas as pd


class ValidationError(ValueError):
    """Raised when a user input fails validation."""


def validate_latitude(latitude: float) -> None:
    if not -90 <= latitude <= 90:
        raise ValidationError("Latitude must be between -90 and 90.")


def validate_longitude(longitude: float) -> None:
    if not -180 <= longitude <= 180:
        raise ValidationError("Longitude must be between -180 and 180.")


def validate_coordinate_pair(latitude: float, longitude: float) -> None:
    validate_latitude(latitude)
    validate_longitude(longitude)


def validate_non_empty_text(value: str, label: str) -> None:
    if not value or not value.strip():
        raise ValidationError(f"{label} is required.")


def validate_stop_count(stops: Iterable[object], minimum: int = 2) -> None:
    stop_list = list(stops)
    if len(stop_list) < minimum:
        raise ValidationError(f"At least {minimum} stops are required for optimization.")


def validate_csv_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValidationError(f"CSV is missing columns: {', '.join(missing)}")
