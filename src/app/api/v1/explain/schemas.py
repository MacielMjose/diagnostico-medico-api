from typing import Dict, List

from pydantic import BaseModel


class ExplainInput(BaseModel):
    features: Dict[str, float]
    diagnosis: int
    probability: float


class ExplainOutput(BaseModel):
    explanation: str
    risk_factors: List[str]
    insights: List[str]
