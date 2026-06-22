from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.v1.ultrasound.schemas import UltrasoundOutput
from app.core.config import Settings
from app.core.dependencies import get_settings

router = APIRouter()


@router.post("/predict", response_model=UltrasoundOutput)
async def predict_ultrasound(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if len(contents) > settings.max_image_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large")

    return UltrasoundOutput(diagnosis=0, confidence=0.0)
