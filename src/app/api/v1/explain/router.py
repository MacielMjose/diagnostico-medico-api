import time

from fastapi import APIRouter, Depends

from app.api.v1.explain.schemas import ExplainInput, ExplainOutput
from app.core.config import Settings
from app.core.dependencies import get_explainer, get_settings
from app.monitoring.posthog import capture_llm_request
from app.services.llm_explainer import LLMExplainerService

router = APIRouter()


@router.post("/", response_model=ExplainOutput)
async def explain(
    input_data: ExplainInput,
    explainer: LLMExplainerService = Depends(get_explainer),
    settings: Settings = Depends(get_settings),
):
    start = time.time()
    result = await explainer.explain(
        features=input_data.features,
        diagnosis=input_data.diagnosis,
        probability=input_data.probability,
    )
    duration = time.time() - start

    capture_llm_request(
        provider=settings.llm_provider,
        model=getattr(
            settings, f"{settings.llm_provider}_model", "unknown"
        ),
        duration=duration,
        status="success",
    )

    return ExplainOutput(
        explanation=result.text,
        risk_factors=result.risk_factors,
        insights=result.insights,
    )
