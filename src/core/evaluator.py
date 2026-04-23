from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ComparisonResult:
    original_cost_km: float
    optimized_cost_km: float
    improvement_percent: float


def compare_costs(original_cost_km: float, optimized_cost_km: float) -> ComparisonResult:
    if original_cost_km <= 0:
        improvement = 0.0
    else:
        improvement = ((original_cost_km - optimized_cost_km) / original_cost_km) * 100.0
    return ComparisonResult(
        original_cost_km=round(original_cost_km, 3),
        optimized_cost_km=round(optimized_cost_km, 3),
        improvement_percent=round(improvement, 2),
    )
