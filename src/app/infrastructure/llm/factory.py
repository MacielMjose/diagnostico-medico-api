import structlog

from app.core.config import Settings
from app.infrastructure.llm.base import LLMProvider

logger = structlog.get_logger()

_SUPPORTED = ("openai", "anthropic", "ollama", "gemini")


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from app.infrastructure.llm.openai_provider import OpenAIProvider

        p = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
        logger.info(
            "llm_provider_created", provider=provider, model=settings.openai_model
        )
        return p

    if provider == "anthropic":
        from app.infrastructure.llm.anthropic_provider import AnthropicProvider

        p = AnthropicProvider(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        )
        logger.info(
            "llm_provider_created", provider=provider, model=settings.anthropic_model
        )
        return p

    if provider == "ollama":
        from app.infrastructure.llm.ollama_provider import OllamaProvider

        p = OllamaProvider(
            base_url=settings.ollama_base_url, model=settings.ollama_model
        )
        logger.info(
            "llm_provider_created", provider=provider, model=settings.ollama_model
        )
        return p

    if provider == "gemini":
        from app.infrastructure.llm.gemini_provider import GeminiProvider

        p = GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
        logger.info(
            "llm_provider_created", provider=provider, model=settings.gemini_model
        )
        return p

    logger.error("llm_provider_unsupported", provider=provider, supported=_SUPPORTED)
    raise ValueError(
        f"LLM provider '{provider}' não suportado. "
        f"Valores válidos: {', '.join(_SUPPORTED)}"
    )
