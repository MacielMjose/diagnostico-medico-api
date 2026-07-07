from dataclasses import dataclass, field
from typing import List


@dataclass
class FeatureContribution:
    feature: str
    contribution: float
    direction: str  # "positiva" | "negativa"


@dataclass
class PCOSPrediction:
    diagnosis: int
    probability: float
    model_version: str
    confidence: str = "Baixa"  # "Alta" | "Média" | "Baixa"
    top_contributing_features: List[FeatureContribution] = field(default_factory=list)


@dataclass
class Explanation:
    text: str
    risk_factors: List[str]
    insights: List[str]
