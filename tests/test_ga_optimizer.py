from __future__ import annotations

from models.ga_optimizer import GAConfig, GeneticAlgorithmOptimizer
from models.route_decoder import decode_stop_order


def _make_optimizer(length: int = 5) -> GeneticAlgorithmOptimizer:
    cfg = GAConfig(
        population_size=20,
        generations=30,
        mutation_rate=0.2,
        crossover_rate=0.9,
        elitism_count=2,
        tournament_size=3,
        random_seed=7,
    )
    return GeneticAlgorithmOptimizer(chromosome_length=length, config=cfg)


def test_population_creation_is_permutation() -> None:
    optimizer = _make_optimizer(length=6)
    population = optimizer.initialize_population()
    assert len(population) == 20
    for chromosome in population:
        assert sorted(chromosome) == list(range(6))


def test_mutation_keeps_valid_permutation() -> None:
    optimizer = _make_optimizer(length=6)
    chromosome = [0, 1, 2, 3, 4, 5]
    mutated = optimizer.mutate(chromosome)
    assert sorted(mutated) == sorted(chromosome)


def test_crossover_keeps_valid_permutation() -> None:
    optimizer = _make_optimizer(length=6)
    parent1 = [0, 1, 2, 3, 4, 5]
    parent2 = [5, 4, 3, 2, 1, 0]
    child1, child2 = optimizer.ordered_crossover(parent1, parent2)
    assert sorted(child1) == list(range(6))
    assert sorted(child2) == list(range(6))


def test_optimize_returns_expected_structure() -> None:
    optimizer = _make_optimizer(length=4)

    def fitness(chromosome: list[int]) -> float:
        return 1.0 / (1 + sum(chromosome))

    result = optimizer.evolve(fitness)
    assert len(result.best_chromosome) == 4
    assert sorted(result.best_chromosome) == [0, 1, 2, 3]
    assert isinstance(result.best_fitness, float)
    assert len(result.history) == 30


def test_route_decoder_order_mapping() -> None:
    decoded = decode_stop_order(
        stop_order=[2, 0, 1],
        stop_names=["A", "B", "C"],
        stop_coordinates=[(24.0, 88.0), (24.1, 88.1), (24.2, 88.2)],
    )
    assert decoded.ordered_names == ["C", "A", "B"]
    assert decoded.ordered_coordinates == [(24.2, 88.2), (24.0, 88.0), (24.1, 88.1)]
