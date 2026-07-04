import time

import structlog
from fastapi import APIRouter, Depends

from app.api.v1.explain.schemas import ExplainInput, ExplainOutput
from app.core.config import Settings
from app.core.dependencies import get_explainer, get_settings
from app.monitoring.posthog import capture_llm_request
from app.services.llm_explainer import LLMExplainerService

logger = structlog.get_logger()

router = APIRouter()


@router.post("/", response_model=ExplainOutput)
async def explain(
    input_data: ExplainInput,
    explainer: LLMExplainerService = Depends(get_explainer),
    settings: Settings = Depends(get_settings),
):
    provider_model = getattr(settings, f"{settings.llm_provider}_model", "unknown")
    logger.info(
        "explain_request_received",
        provider=settings.llm_provider,
        model=provider_model,
        diagnosis=input_data.diagnosis,
        probability=input_data.probability,
        features=input_data.features,
    )
    start = time.time()

    try:
        result, tokens_used = await explainer.explain(
            features=input_data.features,
            diagnosis=input_data.diagnosis,
            probability=input_data.probability,
        )
        duration = time.time() - start

        capture_llm_request(
            provider=settings.llm_provider,
            model=provider_model,
            duration=duration,
            tokens_used=tokens_used,
            status="success",
        )

        logger.info(
            "explain_response_sent",
            provider=settings.llm_provider,
            explanation_length=len(result.text),
            explanation_preview=result.text[:150],
            risk_factors=result.risk_factors,
            insights=result.insights,
            tokens_used=tokens_used,
        )

        return ExplainOutput(
            explanation=result.text,
            risk_factors=result.risk_factors,
            insights=result.insights,
        )
    except Exception as e:
        duration = time.time() - start
        capture_llm_request(
            provider=settings.llm_provider,
            model=provider_model,
            duration=duration,
            status="error",
            error=str(e),
        )
        raise
