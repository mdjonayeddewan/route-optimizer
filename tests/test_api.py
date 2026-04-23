from __future__ import annotations

import pytest

from src.api.directions import extract_route_result
from src.api.ors_client import ORSClient, ORSClientError


class DummyClient:
    def __init__(self, raise_error: bool = False) -> None:
        self.raise_error = raise_error

    def directions(self, coordinates, profile, format, validate):
        if self.raise_error:
            raise Exception("boom")
        return {
            "features": [
                {
                    "properties": {"summary": {"distance": 1000, "duration": 120}},
                    "geometry": {"type": "LineString", "coordinates": [[88.0, 24.0], [88.1, 24.1]]},
                }
            ]
        }


def test_extract_route_result_parses_summary() -> None:
    response = {
        "features": [
            {
                "properties": {"summary": {"distance": 5000, "duration": 600}},
                "geometry": {"type": "LineString", "coordinates": [[88.0, 24.0], [88.2, 24.2]]},
            }
        ]
    }
    result = extract_route_result(response)
    assert result.distance_m == 5000
    assert result.duration_s == 600


def test_ors_client_missing_key_fails() -> None:
    with pytest.raises(ORSClientError):
        ORSClient(api_key="")
