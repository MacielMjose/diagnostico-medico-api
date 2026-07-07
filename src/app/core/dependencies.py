from fastapi import Depends

from app.core.config import Settings
from app.infrastructure.llm.base import LLMProvider
from app.infrastructure.llm.factory import create_llm_provider
from app.infrastructure.model_registry import ModelRegistry
from app.services.llm_explainer import LLMExplainerService
from app.services.predictor import PredictorService


def get_settings() -> Settings:
    return Settings()


def get_model_registry(settings: Settings = Depends(get_settings)) -> ModelRegistry:
    return ModelRegistry(settings.model_path)


def get_predictor(
    registry: ModelRegistry = Depends(get_model_registry),
) -> PredictorService:
    return PredictorService(registry)


def get_llm_provider(settings: Settings = Depends(get_settings)) -> LLMProvider:
    return create_llm_provider(settings)


def get_explainer(
    provider: LLMProvider = Depends(get_llm_provider),
) -> LLMExplainerService:
    return LLMExplainerService(provider)
