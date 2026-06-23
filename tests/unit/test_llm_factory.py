from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.infrastructure.llm.factory import create_llm_provider


def test_factory_raises_for_unknown_provider():
    settings = Settings(llm_provider="gpt99")
    with pytest.raises(ValueError, match="não suportado"):
        create_llm_provider(settings)


def test_factory_creates_gemini_provider():
    from app.infrastructure.llm.gemini_provider import GeminiProvider

    settings = Settings(llm_provider="gemini", gemini_api_key="fake-key")
    with patch("app.infrastructure.llm.gemini_provider.genai.Client"):
        provider = create_llm_provider(settings)

    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name.startswith("gemini/")


def test_factory_creates_ollama_provider():
    from app.infrastructure.llm.ollama_provider import OllamaProvider

    settings = Settings(llm_provider="ollama")
    provider = create_llm_provider(settings)

    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name.startswith("ollama/")
