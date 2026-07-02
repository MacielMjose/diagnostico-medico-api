from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class ExplainInput(BaseModel):
    features: Dict[str, float]
    diagnosis: int = Field(..., ge=0, le=1)
    probability: float = Field(..., ge=0.0, le=1.0)

    @field_validator("features")
    @classmethod
    def check_no_negative_features(cls, v: dict) -> dict:
        for key, val in v.items():
            if val < 0:
                raise ValueError(
                    f"Feature '{key}' não pode ser negativa: {val}"
                )
        return v


class ExplainOutput(BaseModel):
    explanation: str
    risk_factors: List[str]
    insights: List[str]
