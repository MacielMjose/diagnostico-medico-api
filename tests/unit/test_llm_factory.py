from unittest.mock import MagicMock, patch

import pytest

from app.core.config import Settings
from app.domain.exceptions import LLMConfigurationError
from app.infrastructure.llm.factory import (
    _provider_chain,
    _require_api_key,
    create_llm_provider,
)


class TestRequireApiKey:
    def test_passes_with_valid_key(self):
        _require_api_key("openai", "sk-valid")
        _require_api_key("openai", "  sk-valid  ")

    def test_raises_with_empty_key(self):
        with pytest.raises(LLMConfigurationError, match="credencial"):
            _require_api_key("openai", "")

    def test_raises_with_whitespace_only_key(self):
        with pytest.raises(LLMConfigurationError, match="credencial"):
            _require_api_key("openai", "   ")


class TestCreateLLMProvider:
    def test_factory_raises_for_unknown_provider(self):
        settings = Settings(llm_provider="gpt99")
        with pytest.raises(ValueError, match="não suportado"):
            create_llm_provider(settings)

    def test_factory_creates_openai_provider(self):
        with patch(
            "app.infrastructure.llm.openai_provider.OpenAI",
            return_value=MagicMock(),
        ):
            from app.infrastructure.llm.openai_provider import OpenAIProvider

            settings = Settings(llm_provider="openai", openai_api_key="sk-test")
            provider = create_llm_provider(settings)
            assert isinstance(provider, OpenAIProvider)
            assert provider.provider_name.startswith("openai/")


    def test_factory_raises_if_key_missing_for_openai(self):
        settings = Settings(llm_provider="openai", openai_api_key="")
        with pytest.raises(LLMConfigurationError, match="credencial"):
            create_llm_provider(settings)

    def test_factory_creates_anthropic_provider(self):
        with patch(
            "app.infrastructure.llm.anthropic_provider.anthropic.Anthropic",
            return_value=MagicMock(),
        ):
            from app.infrastructure.llm.anthropic_provider import AnthropicProvider

            settings = Settings(
                llm_provider="anthropic", anthropic_api_key="sk-ant-test"
            )
            provider = create_llm_provider(settings)
            assert isinstance(provider, AnthropicProvider)
            assert provider.provider_name.startswith("anthropic/")

    def test_factory_raises_if_key_missing_for_anthropic(self):
        settings = Settings(llm_provider="anthropic", anthropic_api_key="")
        with pytest.raises(LLMConfigurationError, match="credencial"):
            create_llm_provider(settings)

    def test_factory_creates_gemini_provider(self):
        with patch(
            "app.infrastructure.llm.gemini_provider.genai.Client",
            return_value=MagicMock(),
        ):
            from app.infrastructure.llm.gemini_provider import GeminiProvider

            settings = Settings(llm_provider="gemini", gemini_api_key="ai-test-key")
            provider = create_llm_provider(settings)
            assert isinstance(provider, GeminiProvider)
            assert provider.provider_name.startswith("gemini/")

    def test_factory_raises_if_key_missing_for_gemini(self):
        settings = Settings(llm_provider="gemini", gemini_api_key="")
        with pytest.raises(LLMConfigurationError, match="credencial"):
            create_llm_provider(settings)

    def test_factory_creates_groq_provider(self):
        with patch(
            "app.infrastructure.llm.groq_provider.OpenAI",
            return_value=MagicMock(),
        ):
            from app.infrastructure.llm.groq_provider import GroqProvider

            settings = Settings(llm_provider="groq", groq_api_key="gsk-test")
            provider = create_llm_provider(settings)
            assert isinstance(provider, GroqProvider)
            assert provider.provider_name.startswith("groq/")

    def test_factory_raises_if_key_missing_for_groq(self):
        settings = Settings(llm_provider="groq", groq_api_key="")
        with pytest.raises(LLMConfigurationError, match="credencial"):
            create_llm_provider(settings)

    def test_factory_creates_harness_with_fallback_providers(self):
        with (
            patch(
                "app.infrastructure.llm.openai_provider.OpenAI",
                return_value=MagicMock(),
            ),
            patch(
                "app.infrastructure.llm.groq_provider.OpenAI",
                return_value=MagicMock(),
            ),
        ):
            from app.infrastructure.llm.harness import LLMHarnessProvider

            settings = Settings(
                llm_provider="openai",
                openai_api_key="sk-test",
                llm_fallback_providers="groq",
                groq_api_key="gsk-test",
            )
            provider = create_llm_provider(settings)

            assert isinstance(provider, LLMHarnessProvider)
            assert provider.provider_name.startswith("harness[openai/")
            assert " -> groq/" in provider.provider_name

    def test_factory_raises_if_fallback_key_missing(self):
        settings = Settings(
            llm_provider="openai",
            llm_fallback_providers="groq",
            openai_api_key="sk-test",
            groq_api_key="",
        )
        with pytest.raises(LLMConfigurationError, match="credencial"):
            create_llm_provider(settings)

    def test_provider_chain_deduplicates_preserving_order(self):
        settings = Settings(
            llm_provider="openai",
            llm_fallback_providers="groq, openai, gemini",
        )

        assert _provider_chain(settings) == ("openai", "groq", "gemini")
