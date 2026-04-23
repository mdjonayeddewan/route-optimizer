from __future__ import annotations

from typing import Any

import requests

from application.models import PlaceSuggestion


class SearchError(RuntimeError):
    """Raised when place autocomplete lookup fails."""


def fetch_place_suggestions(query: str, limit: int = 6) -> list[PlaceSuggestion]:
    """Fetch live destination suggestions from Nominatim."""
    q = query.strip()
    if len(q) < 3:
        return []

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": q,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limit,
        "countrycodes": "bd",
        "dedupe": 1,
    }
    headers = {
        "User-Agent": "route-optimizer-live-search/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data: Any = response.json()
    except requests.RequestException as exc:
        raise SearchError(f"Live search request failed: {exc}") from exc

    if not isinstance(data, list):
        return []

    suggestions: list[PlaceSuggestion] = []
    for row in data:
        try:
            suggestions.append(
                PlaceSuggestion(
                    display_name=str(row.get("display_name", "Unknown place")),
                    latitude=float(row["lat"]),
                    longitude=float(row["lon"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue

    return suggestions
