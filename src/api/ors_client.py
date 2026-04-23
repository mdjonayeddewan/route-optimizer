from __future__ import annotations

import os
from typing import Any

import openrouteservice
from openrouteservice.exceptions import ApiError, HTTPError, Timeout


class ORSClientError(RuntimeError):
    """Raised when openrouteservice request fails."""


class ORSClient:
    """Thin wrapper around openrouteservice.Client."""

    def __init__(self, api_key: str | None = None, timeout: int = 15) -> None:
        key = api_key or self._resolve_api_key()
        if not key:
            raise ORSClientError(
                "OpenRouteService API key not found. Set OPENROUTESERVICE_API_KEY in Streamlit secrets or the environment."
            )
        self._client = openrouteservice.Client(key=key, timeout=timeout)

    @staticmethod
    def _resolve_api_key() -> str | None:
        key = os.getenv("OPENROUTESERVICE_API_KEY")
        if key:
            return key

        try:
            import streamlit as st

            secret_key = st.secrets.get("OPENROUTESERVICE_API_KEY")
            if secret_key:
                return str(secret_key)
        except Exception:
            pass

        return None

    def directions(self, coordinates: list[list[float]], profile: str = "driving-car") -> dict[str, Any]:
        try:
            return self._client.directions(
                coordinates=coordinates,
                profile=profile,
                format="geojson",
                validate=True,
            )
        except (ApiError, HTTPError, Timeout) as exc:
            raise ORSClientError(f"Failed to fetch directions: {exc}") from exc

    def distance_matrix(self, locations: list[list[float]], profile: str = "driving-car") -> dict[str, Any]:
        try:
            return self._client.distance_matrix(
                locations=locations,
                profile=profile,
                metrics=["distance", "duration"],
                units="m",
            )
        except (ApiError, HTTPError, Timeout) as exc:
            raise ORSClientError(f"Failed to fetch distance matrix: {exc}") from exc
