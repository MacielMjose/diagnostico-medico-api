import time

from fastapi import APIRouter, Depends

from app.api.v1.predict.schemas import (
    FeatureContributionOutput,
    PCOSInput,
    PCOSOutput,
)
from app.core.dependencies import get_predictor
from app.monitoring.posthog import capture_prediction
from app.services.predictor import PredictorService

router = APIRouter()


@router.post("/", response_model=PCOSOutput)
async def predict(
    input_data: PCOSInput,
    predictor: PredictorService = Depends(get_predictor),
):
    start = time.time()
    result = predictor.predict(input_data.model_dump())
    duration = time.time() - start

    capture_prediction(
        model_name="pcos_model",
        duration=duration,
        status="success",
    )

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
