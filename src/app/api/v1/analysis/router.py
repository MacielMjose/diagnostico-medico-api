import time
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from app.api.v1.analysis.schemas import (
    AnalysisInput,
    AnalysisOutput,
    FeatureContributionOutput,
)
from app.core.config import Settings
from app.core.dependencies import get_explainer, get_predictor, get_settings
from app.domain.features import FEATURE_COLUMN_MAP, validate_explain_features
from app.monitoring.posthog import capture_llm_request
from app.services.llm_explainer import LLMExplainerService
from app.services.predictor import PredictorService

logger = structlog.get_logger()

router = APIRouter()


@router.post("/", response_model=AnalysisOutput)
async def analysis(
    input_data: AnalysisInput,
    predictor: Annotated[PredictorService, Depends(get_predictor)],
    explainer: Annotated[LLMExplainerService, Depends(get_explainer)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    payload = input_data.model_dump()

    # Features com os nomes originais das colunas, como o /explain espera.
    features = {FEATURE_COLUMN_MAP[k]: v for k, v in payload.items()}
    validate_explain_features(features)

    provider_model = getattr(settings, f"{settings.llm_provider}_model", "unknown")
    start = time.time()

    try:
        # 1) Predição — diagnóstico, probabilidade e features determinantes.
        prediction = predictor.predict(payload)

        # 2) Explicação clínica via LLM a partir do resultado da predição.
        explanation, tokens_used = await explainer.explain(
            features=features,
            diagnosis=prediction.diagnosis,
            probability=prediction.probability,
        )
        duration = time.time() - start

        capture_llm_request(
            provider=settings.llm_provider,
            model=provider_model,
            duration=duration,
            tokens_used=tokens_used,
            status="success",
        )

        return AnalysisOutput(
            diagnosis="positivo" if prediction.diagnosis else "negativo",
            probability=prediction.probability,
            confidence=prediction.confidence,
            explanation=explanation.text,
            risk_factors=explanation.risk_factors,
            insights=explanation.insights,
            top_contributing_features=[
                FeatureContributionOutput(
                    feature=c.feature,
                    contribution=c.contribution,
                    direction=c.direction,
                )
                for c in prediction.top_contributing_features
            ],
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
