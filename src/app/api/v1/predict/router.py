from fastapi import APIRouter, Depends

from app.api.v1.predict.schemas import PCOSInput, PCOSOutput
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
        model_version=result.model_version,
    )


@router.post("/top20", response_model=PCOSOutput)
async def predict_top20(
    input_data: PCOSInput,
    predictor: PredictorService = Depends(get_predictor),
):
    result = predictor.predict_top20(input_data.model_dump())
    return PCOSOutput(
        diagnosis=result.diagnosis,
        probability=result.probability,
        model_version=result.model_version,
    )
