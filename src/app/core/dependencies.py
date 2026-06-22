from fastapi import Depends

from app.core.config import Settings
from app.services.predictor import PredictorService
from app.services.genetic_optimizer import GeneticOptimizerService
from app.services.llm_explainer import LLMExplainerService
from app.infrastructure.model_registry import ModelRegistry
from app.infrastructure.llm_client import LLMClient


def get_settings() -> Settings:
    return Settings()


def get_model_registry(settings: Settings = Depends(get_settings)) -> ModelRegistry:
    return ModelRegistry(settings.model_path)


def get_predictor(
    registry: ModelRegistry = Depends(get_model_registry),
) -> PredictorService:
    return PredictorService(registry)


def get_optimizer(
    registry: ModelRegistry = Depends(get_model_registry),
) -> GeneticOptimizerService:
    return GeneticOptimizerService(registry)


def get_llm_client(settings: Settings = Depends(get_settings)) -> LLMClient:
    return LLMClient(api_key=settings.llm_api_key, model=settings.llm_model)


def get_explainer(
    client: LLMClient = Depends(get_llm_client),
) -> LLMExplainerService:
    return LLMExplainerService(client)
