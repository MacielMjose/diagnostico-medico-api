from unittest.mock import MagicMock, patch

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class TestGroqProvider:
    def test_provider_name(self):
        with patch("app.infrastructure.llm.groq_provider.OpenAI"):
            from app.infrastructure.llm.groq_provider import GroqProvider

            provider = GroqProvider(api_key="gsk-test", model="llama-3.1-8b-instant")
            assert provider.provider_name == "groq/llama-3.1-8b-instant"

    def test_generate_returns_llm_response(self):
        with patch("app.infrastructure.llm.groq_provider.OpenAI") as mock_cls:
            from app.infrastructure.llm.groq_provider import GroqProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_resp = mock_client.chat.completions.create.return_value
            mock_resp.choices[0].message.content = "resposta groq"
            mock_resp.usage = MagicMock(total_tokens=80)

            provider = GroqProvider(api_key="gsk-test", model="llama-3.1-8b-instant")
            result = provider.generate("system prompt", "user prompt")

            assert isinstance(result, LLMResponse)
            assert result.text == "resposta groq"
            assert result.tokens_used == 80
            mock_client.chat.completions.create.assert_called_once()

    def test_generate_passes_correct_params(self):
        with patch("app.infrastructure.llm.groq_provider.OpenAI") as mock_cls:
            from app.infrastructure.llm.groq_provider import GroqProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_resp = mock_client.chat.completions.create.return_value
            mock_resp.choices[0].message.content = "ok"
            mock_resp.usage = None

            provider = GroqProvider(api_key="gsk-test", model="llama-3.1-8b-instant")
            provider.generate("sys", "usr")

            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs["model"] == "llama-3.1-8b-instant"
            assert call_kwargs["temperature"] == 0.3
            assert call_kwargs["max_tokens"] == 800
            messages = call_kwargs["messages"]
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"

    def test_is_subclass_of_llm_provider(self):
        with patch("app.infrastructure.llm.groq_provider.OpenAI"):
            from app.infrastructure.llm.groq_provider import GroqProvider

            assert issubclass(GroqProvider, LLMProvider)
