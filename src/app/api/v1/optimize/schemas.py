from typing import List

from pydantic import BaseModel, Field


class GeneticConfig(BaseModel):
    population_size: int = Field(default=50, ge=10, le=500)
    mutation_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    crossover_rate: float = Field(default=0.8, ge=0.0, le=1.0)
    generations: int = Field(default=20, ge=1, le=200)
    model_type: str = "xgboost"


class OptimizeOutput(BaseModel):
    best_params: dict
    fitness_history: List[float]
    comparison: dict
