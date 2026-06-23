from pydantic import BaseModel, Field

# Mapeia nomes de campos Python limpos → nomes originais das colunas do dataset (preservando o espaçamento original)
FEATURE_COLUMN_MAP: dict[str, str] = {
    "follicle_no_r": "Follicle No. (R)",
    "follicle_no_l": "Follicle No. (L)",
    "skin_darkening": "Skin darkening (Y/N)",
    "hair_growth": "hair growth(Y/N)",
    "weight_gain": "Weight gain(Y/N)",
    "cycle": "Cycle(R/I)",
    "fast_food": "Fast food (Y/N)",
    "pimples": "Pimples(Y/N)",
    "amh": "AMH(ng/mL)",
    "bmi": "BMI",
    "cycle_length": "Cycle length(days)",
    "hair_loss": "Hair loss(Y/N)",
    "age": " Age (yrs)",
    "hip": "Hip(inch)",
    "avg_f_size_l": "Avg. F size (L) (mm)",
    "marriage_status": "Marraige Status (Yrs)",
    "endometrium": "Endometrium (mm)",
    "avg_f_size_r": "Avg. F size (R) (mm)",
    "pulse_rate": "Pulse rate(bpm) ",
    "hb": "Hb(g/dl)",
}


class PatientData(BaseModel):
    follicle_no_r: float = Field(..., description="Número de folículos (ovário direito)")
    follicle_no_l: float = Field(..., description="Número de folículos (ovário esquerdo)")
    skin_darkening: int = Field(..., ge=0, le=1, description="Escurecimento da pele — 0=Não, 1=Sim")
    hair_growth: int = Field(..., ge=0, le=1, description="Hirsutismo — 0=Não, 1=Sim")
    weight_gain: int = Field(..., ge=0, le=1, description="Ganho de peso — 0=Não, 1=Sim")
    cycle: float = Field(..., description="Regularidade do ciclo (2=Regular, 4=Irregular)")
    fast_food: int = Field(..., ge=0, le=1, description="Consumo de fast food — 0=Não, 1=Sim")
    pimples: int = Field(..., ge=0, le=1, description="Acne — 0=Não, 1=Sim")
    amh: float = Field(..., ge=0, description="Hormônio Antimülleriano em ng/mL")
    bmi: float = Field(..., ge=10, description="IMC em kg/m²")
    cycle_length: float = Field(..., ge=1, description="Duração do ciclo em dias")
    hair_loss: int = Field(..., ge=0, le=1, description="Alopecia — 0=Não, 1=Sim")
    age: float = Field(..., ge=10, le=100, description="Idade em anos")
    hip: float = Field(..., ge=20, description="Circunferência do quadril em polegadas")
    avg_f_size_l: float = Field(..., ge=0, description="Tamanho médio dos folículos esquerdo em mm")
    marriage_status: float = Field(..., ge=0, description="Anos de casamento")
    endometrium: float = Field(..., ge=0, description="Espessura do endométrio em mm")
    avg_f_size_r: float = Field(..., ge=0, description="Tamanho médio dos folículos direito em mm")
    pulse_rate: float = Field(..., ge=30, description="Frequência cardíaca em bpm")
    hb: float = Field(..., ge=0, description="Hemoglobina em g/dL")

    def to_dataframe_row(self) -> dict[str, float]:
        return {FEATURE_COLUMN_MAP[k]: v for k, v in self.model_dump().items()}


class FeatureContribution(BaseModel):
    feature: str
    contribution: float
    direction: str  # "positiva" | "negativa"


class DiagnosisResponse(BaseModel):
    diagnosis: bool
    probability: float
    confidence: str  # "Alta" | "Média" | "Baixa"
    top_contributing_features: list[FeatureContribution]
    interpretation: str
    disclaimer: str = (
        "Este resultado é apenas uma ferramenta de apoio diagnóstico "
        "e não substitui avaliação médica especializada."
    )
