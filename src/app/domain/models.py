from dataclasses import dataclass
from typing import List


@dataclass
class PCOSPrediction:
    diagnosis: int
    probability: float
    model_version: str


@dataclass
class OptimizationResult:
    best_params: dict
    fitness_history: List[float]
    comparison: dict


@dataclass
class Explanation:
    text: str
    risk_factors: List[str]
    insights: List[str]
