from typing import List

from pydantic import BaseModel, Field


class AnalysisInput(BaseModel):
    follicle_no_r: float = Field(..., description="Folículos — ovário direito")
    follicle_no_l: float = Field(..., description="Folículos — ovário esquerdo")
    skin_darkening: int = Field(
        ..., ge=0, le=1, description="Escurecimento da pele (0/1)"
    )
    hair_growth: int = Field(..., ge=0, le=1, description="Hirsutismo (0/1)")
    weight_gain: int = Field(..., ge=0, le=1, description="Ganho de peso (0/1)")
    cycle: float = Field(..., description="Ciclo (2=Regular, 4=Irregular)")
    fast_food: int = Field(..., ge=0, le=1, description="Consumo de fast food (0/1)")
    pimples: int = Field(..., ge=0, le=1, description="Acne (0/1)")
    amh: float = Field(..., ge=0, description="Hormônio Antimülleriano em ng/mL")
    bmi: float = Field(..., ge=10, description="IMC em kg/m²")
    cycle_length: float = Field(..., ge=1, description="Duração do ciclo em dias")
    hair_loss: int = Field(..., ge=0, le=1, description="Alopecia (0/1)")
    age: float = Field(..., ge=10, le=100, description="Idade em anos")
    hip: float = Field(..., ge=20, description="Circunferência do quadril em polegadas")
    avg_f_size_l: float = Field(..., ge=0, description="Tam. médio folículos esq. (mm)")
    marriage_status: float = Field(..., ge=0, description="Anos de casamento")
    endometrium: float = Field(..., ge=0, description="Espessura do endométrio em mm")
    avg_f_size_r: float = Field(..., ge=0, description="Tam. médio folículos dir. (mm)")
    pulse_rate: float = Field(..., ge=30, description="Frequência cardíaca em bpm")
    hb: float = Field(..., ge=0, description="Hemoglobina em g/dL")


class FeatureContributionOutput(BaseModel):
    feature: str
    contribution: float
    direction: str


class AnalysisOutput(BaseModel):
    diagnosis: str
    probability: float
    confidence: str
    explanation: str
    risk_factors: List[str]
    insights: List[str]
    top_contributing_features: List[FeatureContributionOutput]
