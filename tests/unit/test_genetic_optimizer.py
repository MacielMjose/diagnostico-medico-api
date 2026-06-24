import random

from app.services.genetic_optimizer import GeneticOptimizerService


class TestGeneticOperators:
    """Testes para os operadores do algoritmo genético"""

    def setup_method(self):
        self.optimizer = GeneticOptimizerService(None)

    def test_crossover_maintains_length(self):
        p1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        p2 = [0.6, 0.7, 0.8, 0.9, 1.0]
        c1, c2 = self.optimizer._crossover(p1, p2)
        assert len(c1) == len(p1)
        assert len(c2) == len(p2)

    def test_crossover_combines_parents(self):
        p1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        p2 = [0.6, 0.7, 0.8, 0.9, 1.0]
        c1, c2 = self.optimizer._crossover(p1, p2)
        assert c1[:2] == p1[:2]
        assert c1[2:] == p2[2:]

    def test_mutation_changes_value_with_high_rate(self):
        chromo = [0.5, 0.5, 0.5]
        mutated = self.optimizer._mutate(chromo, rate=1.0)
        assert mutated != chromo

    def test_mutation_preserves_with_zero_rate(self):
        chromo = [0.5, 0.5, 0.5]
        mutated = self.optimizer._mutate(chromo, rate=0.0)
        assert mutated == chromo

    def test_create_chromosome_has_correct_length(self):
        chromo = self.optimizer._create_chromosome()
        assert len(chromo) == 5

    def test_create_chromosome_values_in_range(self):
        for _ in range(100):
            chromo = self.optimizer._create_chromosome()
            for gene in chromo:
                assert 0.01 <= gene <= 1.0

    def test_select_returns_best_chromosome(self):
        population = [
            ([0.1, 0.2], 0.5),
            ([0.3, 0.4], 0.9),
            ([0.5, 0.6], 0.3),
        ]
        selected = self.optimizer._select(population)
        assert selected == [0.3, 0.4]

    def test_run_returns_result_with_defaults(self):
        config = {
            "population_size": 30,
            "generations": 10,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
        }
        result = self.optimizer.run(config)
        assert result.best_params is not None
        assert len(result.fitness_history) == 10
        assert "original_auc" in result.comparison
        assert "optimized_auc" in result.comparison

    def test_run_with_minimal_config(self):
        config = {
            "population_size": 10,
            "generations": 2,
            "mutation_rate": 0.0,
            "crossover_rate": 1.0,
        }
        result = self.optimizer.run(config)
        assert len(result.fitness_history) == 2

    def test_run_fitness_history_tracks_best_per_generation(self):
        config = {
            "population_size": 20,
            "generations": 5,
            "mutation_rate": 0.05,
            "crossover_rate": 0.8,
        }
        result = self.optimizer.run(config)
        for fitness in result.fitness_history:
            assert isinstance(fitness, float)

    def test_run_with_zero_crossover_generates_only_mutated_copies(self):
        random.seed(42)
        config = {
            "population_size": 10,
            "generations": 3,
            "mutation_rate": 0.1,
            "crossover_rate": 0.0,
        }
        result = self.optimizer.run(config)
        assert len(result.fitness_history) == 3
