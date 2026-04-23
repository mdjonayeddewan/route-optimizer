from __future__ import annotations

import math
from typing import Sequence


def haversine_km(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Compute Haversine distance in kilometers between two (lat, lon) points."""
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371.0 * c


def route_cost(order: Sequence[int], matrix: list[list[float]]) -> float:
    """Sum pairwise segment costs for a full path over matrix indices."""
    if len(order) < 2:
        return 0.0

    total = 0.0
    for i in range(len(order) - 1):
        total += matrix[order[i]][order[i + 1]]
    return total


def fitness_from_cost(cost: float) -> float:
    if cost <= 0:
        return 0.0
    return 1.0 / cost
