from fastapi import APIRouter

from app.api.v1.predict.router import router as predict_router
from app.api.v1.ultrasound.router import router as ultrasound_router
from app.api.v1.optimize.router import router as optimize_router
from app.api.v1.explain.router import router as explain_router

api_v1_router = APIRouter()
api_v1_router.include_router(predict_router, prefix="/predict", tags=["Predict"])
api_v1_router.include_router(
    ultrasound_router, prefix="/ultrasound", tags=["Ultrasound"]
)
api_v1_router.include_router(optimize_router, prefix="/optimize", tags=["Optimize"])
api_v1_router.include_router(explain_router, prefix="/explain", tags=["Explain"])
