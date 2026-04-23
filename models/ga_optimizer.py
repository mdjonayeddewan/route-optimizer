from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable


FitnessFn = Callable[[list[int]], float]


@dataclass(slots=True)
class GAConfig:
    population_size: int
    generations: int
    mutation_rate: float
    crossover_rate: float
    elitism_count: int
    tournament_size: int
    random_seed: int | None = None


@dataclass(slots=True)
class GAResult:
    best_chromosome: list[int]
    best_fitness: float
    history: list[float]


class GeneticAlgorithmOptimizer:
    """Permutation-based GA optimizer for stop ordering."""

    def __init__(self, chromosome_length: int, config: GAConfig) -> None:
        if chromosome_length < 1:
            raise ValueError("Chromosome length must be >= 1")
        self.chromosome_length = chromosome_length
        self.config = config
        self._rng = random.Random(config.random_seed)

    def initialize_population(self) -> list[list[int]]:
        base = list(range(self.chromosome_length))
        population: list[list[int]] = []
        for _ in range(self.config.population_size):
            candidate = base[:]
            self._rng.shuffle(candidate)
            population.append(candidate)
        return population

    def tournament_selection(self, population: list[list[int]], fitness_fn: FitnessFn) -> list[int]:
        tournament = self._rng.sample(population, k=min(self.config.tournament_size, len(population)))
        return max(tournament, key=fitness_fn)

    def ordered_crossover(self, parent1: list[int], parent2: list[int]) -> tuple[list[int], list[int]]:
        n = len(parent1)
        if n < 2 or self._rng.random() > self.config.crossover_rate:
            return parent1[:], parent2[:]

        i, j = sorted(self._rng.sample(range(n), 2))

        def _build_child(a: list[int], b: list[int]) -> list[int]:
            child = [-1] * n
            child[i:j + 1] = a[i:j + 1]
            remaining = [gene for gene in b if gene not in child]
            rem_idx = 0
            for pos in range(n):
                if child[pos] == -1:
                    child[pos] = remaining[rem_idx]
                    rem_idx += 1
            return child

        return _build_child(parent1, parent2), _build_child(parent2, parent1)

    def mutate(self, chromosome: list[int]) -> list[int]:
        candidate = chromosome[:]
        if len(candidate) > 1 and self._rng.random() < self.config.mutation_rate:
            i, j = self._rng.sample(range(len(candidate)), 2)
            candidate[i], candidate[j] = candidate[j], candidate[i]
        return candidate

    def evolve(self, fitness_fn: FitnessFn) -> GAResult:
        population = self.initialize_population()
        best: list[int] = population[0][:]
        best_fitness = fitness_fn(best)
        history: list[float] = []

        for _ in range(self.config.generations):
            ranked = sorted(population, key=fitness_fn, reverse=True)
            elites = [x[:] for x in ranked[: self.config.elitism_count]]

            generation_best = ranked[0]
            generation_best_fitness = fitness_fn(generation_best)
            history.append(generation_best_fitness)

            if generation_best_fitness > best_fitness:
                best = generation_best[:]
                best_fitness = generation_best_fitness

            new_population = elites
            while len(new_population) < self.config.population_size:
                parent1 = self.tournament_selection(population, fitness_fn)
                parent2 = self.tournament_selection(population, fitness_fn)
                child1, child2 = self.ordered_crossover(parent1, parent2)
                new_population.append(self.mutate(child1))
                if len(new_population) < self.config.population_size:
                    new_population.append(self.mutate(child2))

            population = new_population

        return GAResult(best_chromosome=best, best_fitness=best_fitness, history=history)
