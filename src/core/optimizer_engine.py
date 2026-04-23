from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from models.fitness_function import fitness_from_cost, route_cost
from models.ga_optimizer import GAConfig, GAResult, GeneticAlgorithmOptimizer
from src.api.directions import RouteResult, get_route
from src.api.geocoding import LocationPoint, resolve_location_input
from src.api.osrm_client import OSRMClientError, get_osrm_route
from src.api.ors_client import ORSClient, ORSClientError
from src.core.distance_builder import build_haversine_matrix
from src.core.evaluator import ComparisonResult, compare_costs


@dataclass(slots=True)
class OptimizationOutput:
    start: LocationPoint
    stops_original: list[LocationPoint]
    stops_optimized: list[LocationPoint]
    end: LocationPoint | None
    comparison: ComparisonResult
    ga_result: GAResult
    final_route: RouteResult
    distance_matrix_km: np.ndarray
    matrix_labels: list[str]
    used_fallback: bool
    route_provider: str


def _build_full_order(optimized_stop_indices: list[int], stop_offset: int, has_end: bool) -> list[int]:
    order = [0]
    order.extend(idx + stop_offset for idx in optimized_stop_indices)
    if has_end:
        order.append(stop_offset + len(optimized_stop_indices))
    return order


def run_multi_stop_optimization(
    start_input: str,
    stop_inputs: list[str],
    end_input: str | None,
    profile: str,
    ga_config: GAConfig,
    api_key: str | None = None,
    use_haversine_fallback: bool = True,
) -> OptimizationOutput:
    start = resolve_location_input(start_input, default_name="Start")
    stops_original = [resolve_location_input(value, default_name=f"Stop {idx + 1}") for idx, value in enumerate(stop_inputs)]
    end = resolve_location_input(end_input, default_name="End") if end_input and end_input.strip() else None

    matrix_points = [start] + stops_original + ([end] if end else [])
    matrix_result = build_haversine_matrix(matrix_points)
    matrix = matrix_result.distance_matrix_km

    stop_count = len(stops_original)
    optimizer = GeneticAlgorithmOptimizer(chromosome_length=stop_count, config=ga_config)

    def _fitness(chromosome: list[int]) -> float:
        full_order = _build_full_order(chromosome, stop_offset=1, has_end=end is not None)
        cost = route_cost(full_order, matrix.tolist())
        return fitness_from_cost(cost)

    ga_result = optimizer.evolve(_fitness)

    original_order = _build_full_order(list(range(stop_count)), stop_offset=1, has_end=end is not None)
    optimized_order = _build_full_order(ga_result.best_chromosome, stop_offset=1, has_end=end is not None)

    original_cost = route_cost(original_order, matrix.tolist())
    optimized_cost = route_cost(optimized_order, matrix.tolist())
    comparison = compare_costs(original_cost, optimized_cost)

    stops_optimized = [stops_original[idx] for idx in ga_result.best_chromosome]

    ordered_points = [start] + stops_optimized + ([end] if end else [])
    points_lonlat = [point.lonlat for point in ordered_points]

    used_fallback = False
    route_provider = "ors"
    try:
        client = ORSClient(api_key=api_key)
        final_route = get_route(client=client, points_lonlat=points_lonlat, profile=profile)
    except ORSClientError:
        if not use_haversine_fallback:
            raise
        used_fallback = True
        try:
            final_route = get_osrm_route(points_lonlat=points_lonlat, ors_profile=profile)
            route_provider = "osrm"
        except OSRMClientError:
            route_provider = "haversine"
            avg_speed_kmph = 35.0
            duration_h = optimized_cost / avg_speed_kmph if avg_speed_kmph > 0 else 0.0
            final_route = RouteResult(
                distance_m=optimized_cost * 1000.0,
                duration_s=duration_h * 3600.0,
                geometry={
                    "type": "LineString",
                    "coordinates": points_lonlat,
                },
            )

    return OptimizationOutput(
        start=start,
        stops_original=stops_original,
        stops_optimized=stops_optimized,
        end=end,
        comparison=comparison,
        ga_result=ga_result,
        final_route=final_route,
        distance_matrix_km=matrix,
        matrix_labels=matrix_result.labels,
        used_fallback=used_fallback,
        route_provider=route_provider,
    )
