import structlog

from app.core.config import Settings
from app.domain.exceptions import LLMConfigurationError
from app.infrastructure.llm.base import LLMProvider

logger = structlog.get_logger()

_SUPPORTED = ("openai", "anthropic", "ollama", "gemini", "groq")

# Env var that must be configured for each credential-based provider.
_REQUIRED_ENV_VAR = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
}


def _require_api_key(provider: str, api_key: str) -> None:
    if api_key and api_key.strip():
        return
    env_var = _REQUIRED_ENV_VAR[provider]
    logger.error("llm_provider_missing_credentials", provider=provider, env_var=env_var)
    raise LLMConfigurationError(
        f"O provedor de LLM '{provider}' está configurado, mas a credencial "
        f"não foi informada. Defina a variável de ambiente '{env_var}' no seu "
        f"arquivo .env."
    )


def _parse_provider_names(value: str) -> tuple[str, ...]:
    return tuple(item.strip().lower() for item in value.split(",") if item.strip())


def _provider_chain(settings: Settings) -> tuple[str, ...]:
    providers = [
        settings.llm_provider.lower(),
        *_parse_provider_names(settings.llm_fallback_providers),
    ]
    return tuple(dict.fromkeys(providers))


def _create_single_provider(provider: str, settings: Settings) -> LLMProvider:
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

    if provider == "groq":
        from app.infrastructure.llm.groq_provider import GroqProvider

        _require_api_key(provider, settings.groq_api_key)
        p = GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)
        logger.info(
            "llm_provider_created", provider=provider, model=settings.groq_model
        )
        return p

    logger.error("llm_provider_unsupported", provider=provider, supported=_SUPPORTED)
    raise ValueError(
        f"LLM provider '{provider}' não suportado. "
        f"Valores válidos: {', '.join(_SUPPORTED)}"
    )


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider_names = _provider_chain(settings)
    providers = [
        _create_single_provider(provider, settings) for provider in provider_names
    ]

    if len(providers) == 1:
        return providers[0]

    from app.infrastructure.llm.harness import LLMHarnessProvider

    harness = LLMHarnessProvider(providers)
    logger.info(
        "llm_harness_created",
        providers=provider_names,
        provider_count=len(providers),
    )
    return harness
