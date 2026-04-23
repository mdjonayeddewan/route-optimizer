from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

import pandas as pd


Coordinate = tuple[float, float]


def format_coordinate(coord: Coordinate) -> str:
    """Return a stable text representation of a coordinate."""
    return f"{coord[0]:.6f}, {coord[1]:.6f}"


def meters_to_km(value_m: float) -> float:
    return round(value_m / 1000.0, 3)


def seconds_to_minutes(value_s: float) -> float:
    return round(value_s / 60.0, 2)


def ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def save_json(path: str | Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with Path(path).open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


def save_csv(path: str | Path, rows: Sequence[dict[str, Any]]) -> None:
    ensure_parent(path)
    pd.DataFrame(rows).to_csv(path, index=False)


def flatten(items: Iterable[Iterable[Any]]) -> list[Any]:
    return [x for group in items for x in group]
