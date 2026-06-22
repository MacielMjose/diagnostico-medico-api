from pydantic import BaseModel, Field, ConfigDict


class PCOSInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    age: float = Field(..., alias="Age (yrs)")
    bmi: float = Field(..., alias="BMI")
    follicle_no_r: float = Field(..., alias="Follicle No. (R)")
    follicle_no_l: float = Field(..., alias="Follicle No. (L)")
    skin_darkening: int = Field(..., alias="Skin darkening (Y/N)")
    hair_growth: int = Field(..., alias="hair growth(Y/N)")
    weight_gain: int = Field(..., alias="Weight gain(Y/N)")
    amh: float = Field(..., alias="AMH(ng/mL)")
    cycle_r_i: int = Field(..., alias="Cycle(R/I)")
    fast_food: int = Field(..., alias="Fast food (Y/N)")


class PCOSOutput(BaseModel):
    diagnosis: int
    probability: float
    model_version: str
