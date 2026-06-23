from minha_api.config import settings
from minha_api.services.llm.base import LLMProvider

_SUPPORTED = ("openai", "anthropic", "ollama", "gemini")


def create_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from minha_api.services.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)

    if provider == "anthropic":
        from minha_api.services.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        )

    if provider == "ollama":
        from minha_api.services.llm.ollama_provider import OllamaProvider

        return OllamaProvider(base_url=settings.ollama_base_url, model=settings.ollama_model)

    if provider == "gemini":
        from minha_api.services.llm.gemini_provider import GeminiProvider

        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)

    raise ValueError(
        f"LLM provider '{provider}' não suportado. "
        f"Valores válidos: {', '.join(_SUPPORTED)}"
    )
