from typing import Dict, List

from pydantic import BaseModel, Field, field_validator

from app.domain.features import FeatureValidator


class ExplainInput(BaseModel):
    features: Dict[str, float]
    diagnosis: int = Field(..., ge=0, le=1)
    probability: float = Field(..., ge=0.0, le=1.0)

    @field_validator("features")
    @classmethod
    def check_features(cls, v: dict) -> dict:
        FeatureValidator.validate_no_negative(v)
        FeatureValidator.validate_binary_only(v)
        return v


class ExplainOutput(BaseModel):
    explanation: str
    risk_factors: List[str]
    insights: List[str]
