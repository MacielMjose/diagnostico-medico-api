from pydantic import BaseModel


class UltrasoundOutput(BaseModel):
    diagnosis: int
    confidence: float
