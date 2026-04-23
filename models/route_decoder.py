from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class DecodedRoute:
    ordered_names: list[str]
    ordered_coordinates: list[tuple[float, float]]


def decode_stop_order(
    stop_order: Sequence[int],
    stop_names: Sequence[str],
    stop_coordinates: Sequence[tuple[float, float]],
) -> DecodedRoute:
    if len(stop_names) != len(stop_coordinates):
        raise ValueError("Stop names and stop coordinates size mismatch.")

    ordered_names = [stop_names[idx] for idx in stop_order]
    ordered_coordinates = [stop_coordinates[idx] for idx in stop_order]
    return DecodedRoute(ordered_names=ordered_names, ordered_coordinates=ordered_coordinates)
