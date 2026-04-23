from __future__ import annotations

import pytest

from models.fitness_function import haversine_km
from src.api.geocoding import parse_latlon_text
from src.utils.validators import ValidationError, validate_coordinate_pair, validate_stop_count


def test_haversine_returns_zero_for_same_point() -> None:
    point = (24.0, 88.0)
    assert haversine_km(point, point) == 0.0


def test_parse_latlon_text_valid() -> None:
    parsed = parse_latlon_text("24.5,88.3")
    assert parsed == (24.5, 88.3)


def test_validate_coordinate_pair_invalid() -> None:
    with pytest.raises(ValidationError):
        validate_coordinate_pair(95.0, 88.0)


def test_validate_stop_count() -> None:
    with pytest.raises(ValidationError):
        validate_stop_count(["A"], minimum=2)
