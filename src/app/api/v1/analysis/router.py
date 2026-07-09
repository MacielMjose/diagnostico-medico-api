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
from app.monitoring.posthog import (
    capture_llm_error,
    capture_llm_success,
    capture_prediction_error,
    capture_prediction_success,
)
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

    # 1) Predição — diagnóstico, probabilidade e features determinantes.
    prediction_start = time.time()
    try:
        prediction = predictor.predict(payload)
        capture_prediction_success(
            model_name="pcos_model",
            duration=time.time() - prediction_start,
            endpoint="/analysis",
        )
    except Exception as e:
        capture_prediction_error(
            model_name="pcos_model",
            duration=time.time() - prediction_start,
            endpoint="/analysis",
            error=str(e),
        )
        raise

    # 2) Explicação clínica via LLM a partir do resultado da predição.
    llm_start = time.time()
    try:
        explanation, tokens_used = await explainer.explain(
            features=features,
            diagnosis=prediction.diagnosis,
            probability=prediction.probability,
        )
        capture_llm_success(
            provider=settings.llm_provider,
            model=provider_model,
            duration=time.time() - llm_start,
            tokens_used=tokens_used,
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
        capture_llm_error(
            provider=settings.llm_provider,
            model=provider_model,
            duration=time.time() - llm_start,
            error=str(e),
        )
        raise
