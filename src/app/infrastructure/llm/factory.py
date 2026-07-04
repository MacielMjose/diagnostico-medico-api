import structlog

from app.core.config import Settings
from app.domain.exceptions import LLMConfigurationError
from app.infrastructure.llm.base import LLMProvider

logger = structlog.get_logger()

_SUPPORTED = ("openai", "anthropic", "ollama", "gemini")

# Env var that must be configured for each credential-based provider.
_REQUIRED_ENV_VAR = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def _require_api_key(provider: str, api_key: str) -> None:
    if api_key and api_key.strip():
        return
    env_var = _REQUIRED_ENV_VAR[provider]
    logger.error("llm_provider_missing_credentials", provider=provider, env_var=env_var)
    raise LLMConfigurationError(
        f"O provedor de LLM '{provider}' está selecionado (LLM_PROVIDER={provider}), "
        f"mas a credencial não foi configurada. Defina a variável de ambiente "
        f"'{env_var}' no seu arquivo .env (ou troque LLM_PROVIDER para 'ollama', "
        f"que não exige chave de API)."
    )


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from app.infrastructure.llm.openai_provider import OpenAIProvider

        _require_api_key(provider, settings.openai_api_key)
        p = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
        logger.info(
            "llm_provider_created", provider=provider, model=settings.openai_model
        )
        return p

    if provider == "anthropic":
        from app.infrastructure.llm.anthropic_provider import AnthropicProvider

        _require_api_key(provider, settings.anthropic_api_key)
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

        _require_api_key(provider, settings.gemini_api_key)
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
