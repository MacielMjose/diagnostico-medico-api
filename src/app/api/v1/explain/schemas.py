from pydantic import BaseModel
from typing import List, Dict


class ExplainInput(BaseModel):
    features: Dict[str, float]
    diagnosis: int
    probability: float


class ExplainOutput(BaseModel):
    explanation: str
    risk_factors: List[str]
    insights: List[str]
