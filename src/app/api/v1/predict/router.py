import time

import structlog
from fastapi import APIRouter, Depends

from app.api.v1.predict.schemas import (
    FeatureContributionOutput,
    PCOSInput,
    PCOSOutput,
)
from app.core.dependencies import get_predictor
from app.monitoring.posthog import capture_prediction_error, capture_prediction_success
from app.services.predictor import PredictorService

logger = structlog.get_logger()

router = APIRouter()


@router.post("/", response_model=PCOSOutput)
async def predict(
    input_data: PCOSInput,
    predictor: PredictorService = Depends(get_predictor),
):
    logger.info(
        "predict_request_received", features=list(input_data.model_dump().keys())
    )
    start = time.time()

    try:
        result = predictor.predict(input_data.model_dump())
        duration = time.time() - start

        capture_prediction_success(
            model_name="pcos_model",
            duration=duration,
            endpoint="/predict",
        )

        logger.info(
            "predict_response_sent",
            diagnosis=result.diagnosis,
            probability=result.probability,
            confidence=result.confidence,
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
    except Exception as e:
        duration = time.time() - start
        capture_prediction_error(
            model_name="pcos_model",
            duration=duration,
            endpoint="/predict",
            error=str(e),
        )
        raise
