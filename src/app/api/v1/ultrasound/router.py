import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.v1.ultrasound.schemas import UltrasoundOutput
from app.core.config import Settings
from app.core.dependencies import get_settings
from app.monitoring.posthog import capture_event

logger = structlog.get_logger()

router = APIRouter()


@router.post("/predict", response_model=UltrasoundOutput)
async def predict_ultrasound(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        logger.warning(
            "ultrasound_invalid_content_type",
            filename=file.filename,
            content_type=file.content_type,
        )
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    logger.info(
        "ultrasound_request_received",
        filename=file.filename,
        content_type=file.content_type,
        size_mb=round(file_size_mb, 2),
    )

    if len(contents) > settings.max_image_size_mb * 1024 * 1024:
        logger.warning(
            "ultrasound_image_too_large",
            filename=file.filename,
            size_mb=round(file_size_mb, 2),
            max_mb=settings.max_image_size_mb,
        )
        raise HTTPException(status_code=400, detail="Image too large")

    capture_event(
        "ultrasound_prediction",
        properties={
            "filename": file.filename,
            "content_type": file.content_type,
            "size_mb": round(file_size_mb, 2),
            "diagnosis": 0,
            "confidence": 0.0,
        },
    )

    logger.info(
        "ultrasound_response_sent",
        diagnosis=0,
        confidence=0.0,
    )

    return UltrasoundOutput(diagnosis=0, confidence=0.0)
