from fastapi import APIRouter, Depends

from app.api.v1.predict.schemas import (
    FeatureContributionOutput,
    PCOSInput,
    PCOSOutput,
)
from app.core.dependencies import get_predictor
from app.services.predictor import PredictorService

router = APIRouter()


@router.post("/", response_model=PCOSOutput)
async def predict(
    input_data: PCOSInput,
    predictor: PredictorService = Depends(get_predictor),
):
    result = predictor.predict(input_data.model_dump())
    return PCOSOutput(
        diagnosis=result.diagnosis,
        probability=result.probability,
        confidence=result.confidence,
        model_version=result.model_version,
        top_contributing_features=[
            FeatureContributionOutput(
                feature=c.feature,
                contribution=c.contribution,
                direction=c.direction,
            )
            for c in result.top_contributing_features
        ],
    )
