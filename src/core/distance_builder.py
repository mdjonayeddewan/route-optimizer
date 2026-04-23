from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from models.fitness_function import haversine_km
from src.api.geocoding import LocationPoint


@dataclass(slots=True)
class DistanceBuildResult:
    distance_matrix_km: np.ndarray
    labels: list[str]


def build_haversine_matrix(points: Sequence[LocationPoint]) -> DistanceBuildResult:
    labels = [point.name for point in points]
    n = len(points)
    matrix = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i, j] = 0.0
            else:
                matrix[i, j] = haversine_km(points[i].latlon, points[j].latlon)

    return DistanceBuildResult(distance_matrix_km=matrix, labels=labels)
