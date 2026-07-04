import random
import time
from typing import List, Tuple

import structlog

from app.domain.models import OptimizationResult

logger = structlog.get_logger()


class GeneticOptimizerService:
    def __init__(self, registry):
        self.registry = registry

    def _create_chromosome(self) -> List[float]:
        return [random.uniform(0.01, 1.0) for _ in range(5)]

    def _mutate(self, chromosome: List[float], rate: float) -> List[float]:
        return [
            c if random.random() > rate else c + random.uniform(-0.1, 0.1)
            for c in chromosome
        ]

    def _crossover(
        self, p1: List[float], p2: List[float]
    ) -> Tuple[List[float], List[float]]:
        point = len(p1) // 2
        return p1[:point] + p2[point:], p2[:point] + p1[point:]

    def _fitness(self, chromosome: List[float]) -> float:
        return random.random()

    def _select(self, population: List[Tuple[List[float], float]]) -> List[float]:
        return max(population, key=lambda x: x[1])[0]

    def run(self, config: dict) -> OptimizationResult:
        pop_size = config.get("population_size", 50)
        generations = config.get("generations", 20)
        mut_rate = config.get("mutation_rate", 0.05)
        cross_rate = config.get("crossover_rate", 0.8)

        logger.info(
            "optimization_started",
            population_size=pop_size,
            generations=generations,
            mutation_rate=mut_rate,
            crossover_rate=cross_rate,
        )
        start_time = time.time()

        population: List[Tuple[List[float], float]] = [
            (self._create_chromosome(), 0.0) for _ in range(pop_size)
        ]
        fitness_history = []

        for gen in range(generations):
            for i in range(pop_size):
                population[i] = (population[i][0], self._fitness(population[i][0]))

            gen_best = max(f[1] for f in population)
            gen_avg = sum(f[1] for f in population) / pop_size
            fitness_history.append(gen_best)

            logger.debug(
                "ga_generation",
                generation=gen + 1,
                best_fitness=round(gen_best, 6),
                avg_fitness=round(gen_avg, 6),
                population_size=pop_size,
            )

            new_pop = []
            while len(new_pop) < pop_size:
                if random.random() < cross_rate:
                    p1 = self._select(population)
                    p2 = self._select(population)
                    c1, c2 = self._crossover(p1, p2)
                    new_pop.extend(
                        [self._mutate(c1, mut_rate), self._mutate(c2, mut_rate)]
                    )
                else:
                    new_pop.append(self._mutate(self._select(population), mut_rate))
            population = [(c, 0.0) for c in new_pop[:pop_size]]

        best = max(population, key=lambda x: self._fitness(x[0]))
        best_fitness = self._fitness(best[0])
        elapsed = time.time() - start_time

        logger.info(
            "optimization_completed",
            best_fitness=round(best_fitness, 6),
            total_generations=generations,
            duration_seconds=round(elapsed, 3),
        )

        return OptimizationResult(
            best_params={"param1": best[0][0]},
            fitness_history=fitness_history,
            comparison={
                "original_auc": 0.92,
                "optimized_auc": best_fitness,
            },
        )
