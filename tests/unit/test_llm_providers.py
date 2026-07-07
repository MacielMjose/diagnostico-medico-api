from unittest.mock import MagicMock, patch

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class TestOpenAIProvider:
    def test_provider_name(self):
        with patch("app.infrastructure.llm.openai_provider.OpenAI"):
            from app.infrastructure.llm.openai_provider import OpenAIProvider

            provider = OpenAIProvider(api_key="fake-key", model="gpt-4o-mini")
            assert provider.provider_name == "openai/gpt-4o-mini"

    def test_generate_returns_llm_response(self):
        with patch("app.infrastructure.llm.openai_provider.OpenAI") as mock_cls:
            from app.infrastructure.llm.openai_provider import OpenAIProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_resp = mock_client.chat.completions.create.return_value
            mock_resp.choices[0].message.content = "resposta simulada"
            mock_resp.usage = MagicMock(total_tokens=50)

            provider = OpenAIProvider(api_key="fake-key", model="gpt-4o-mini")
            result = provider.generate("system prompt", "user prompt")

            assert isinstance(result, LLMResponse)
            assert result.text == "resposta simulada"
            assert result.tokens_used == 50
            mock_client.chat.completions.create.assert_called_once()

    def test_generate_passes_correct_params(self):
        with patch("app.infrastructure.llm.openai_provider.OpenAI") as mock_cls:
            from app.infrastructure.llm.openai_provider import OpenAIProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_resp = mock_client.chat.completions.create.return_value
            mock_resp.choices[0].message.content = "ok"
            mock_resp.usage = None

            provider = OpenAIProvider(api_key="sk-test", model="gpt-4")
            provider.generate("sys", "usr")

            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["temperature"] == 0.3
            assert call_kwargs["max_tokens"] == 800
            messages = call_kwargs["messages"]
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"

    def test_is_subclass_of_llm_provider(self):
        with patch("app.infrastructure.llm.openai_provider.OpenAI"):
            from app.infrastructure.llm.openai_provider import OpenAIProvider

            assert issubclass(OpenAIProvider, LLMProvider)


class TestAnthropicProvider:
    def test_provider_name(self):
        with patch("app.infrastructure.llm.anthropic_provider.anthropic.Anthropic"):
            from app.infrastructure.llm.anthropic_provider import AnthropicProvider

            provider = AnthropicProvider(api_key="fake-key", model="claude-haiku")
            assert provider.provider_name == "anthropic/claude-haiku"

    def test_generate_returns_llm_response(self):
        with patch(
            "app.infrastructure.llm.anthropic_provider.anthropic.Anthropic"
        ) as mock_cls:
            from app.infrastructure.llm.anthropic_provider import AnthropicProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            message = mock_client.messages.create.return_value
            message.content = [MagicMock(text="resposta anthropic")]
            message.usage = MagicMock(input_tokens=20, output_tokens=30)

            provider = AnthropicProvider(api_key="fake-key", model="claude-haiku")
            result = provider.generate("system prompt", "user prompt")

            assert isinstance(result, LLMResponse)
            assert result.text == "resposta anthropic"
            assert result.tokens_used == 50

    def test_generate_passes_correct_params(self):
        with patch(
            "app.infrastructure.llm.anthropic_provider.anthropic.Anthropic"
        ) as mock_cls:
            from app.infrastructure.llm.anthropic_provider import AnthropicProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.messages.create.return_value.content = [MagicMock(text="ok")]
            mock_client.messages.create.return_value.usage = None

            provider = AnthropicProvider(api_key="sk-ant-test", model="claude-3")
            provider.generate("sys", "usr")

            call_kwargs = mock_client.messages.create.call_args.kwargs
            assert call_kwargs["model"] == "claude-3"
            assert call_kwargs["max_tokens"] == 800
            assert call_kwargs["temperature"] == 0.3
            assert call_kwargs["system"] == "sys"
            assert call_kwargs["messages"] == [{"role": "user", "content": "usr"}]

    def test_is_subclass_of_llm_provider(self):
        with patch("app.infrastructure.llm.anthropic_provider.anthropic.Anthropic"):
            from app.infrastructure.llm.anthropic_provider import AnthropicProvider

            assert issubclass(AnthropicProvider, LLMProvider)


class TestOllamaProvider:
    def test_provider_name(self):
        from app.infrastructure.llm.ollama_provider import OllamaProvider

        provider = OllamaProvider(base_url="http://localhost:11434", model="llama3.2")
        assert provider.provider_name == "ollama/llama3.2"

    def test_generate_returns_llm_response(self):
        from app.infrastructure.llm.ollama_provider import OllamaProvider

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "resposta ollama"}}],
            "usage": {"total_tokens": 80},
        }
        mock_response.raise_for_status = MagicMock()

        with patch(
            "app.infrastructure.llm.ollama_provider.httpx.post",
            return_value=mock_response,
        ):
            provider = OllamaProvider(
                base_url="http://localhost:11434", model="llama3.2"
            )
            result = provider.generate("system prompt", "user prompt")

            assert isinstance(result, LLMResponse)
            assert result.text == "resposta ollama"
            assert result.tokens_used == 80

    def test_generate_calls_correct_url(self):
        from app.infrastructure.llm.ollama_provider import OllamaProvider

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_response.raise_for_status = MagicMock()

        with patch(
            "app.infrastructure.llm.ollama_provider.httpx.post",
            return_value=mock_response,
        ) as mock_post:
            provider = OllamaProvider(
                base_url="http://localhost:11434/", model="llama3.2"
            )
            provider.generate("sys", "usr")

            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:11434/v1/chat/completions"

    def test_strips_trailing_slash_from_base_url(self):
        from app.infrastructure.llm.ollama_provider import OllamaProvider

        provider = OllamaProvider(
            base_url="http://localhost:11434///", model="llama3.2"
        )
        assert provider._base_url == "http://localhost:11434"

    def test_is_subclass_of_llm_provider(self):
        from app.infrastructure.llm.ollama_provider import OllamaProvider

        assert issubclass(OllamaProvider, LLMProvider)


class TestGeminiProvider:
    def test_provider_name(self):
        with patch("app.infrastructure.llm.gemini_provider.genai.Client"):
            from app.infrastructure.llm.gemini_provider import GeminiProvider

            provider = GeminiProvider(api_key="fake-key", model="gemini-2.0-flash")
            assert provider.provider_name == "gemini/gemini-2.0-flash"

    def test_generate_returns_llm_response(self):
        with patch("app.infrastructure.llm.gemini_provider.genai.Client") as mock_cls:
            from app.infrastructure.llm.gemini_provider import GeminiProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_resp = mock_client.models.generate_content.return_value
            mock_resp.text = "resposta gemini"
            mock_resp.usage_metadata = MagicMock(total_token_count=60)

            provider = GeminiProvider(api_key="fake-key", model="gemini-2.0-flash")
            result = provider.generate("system prompt", "user prompt")

            assert isinstance(result, LLMResponse)
            assert result.text == "resposta gemini"
            assert result.tokens_used == 60

    def test_generate_passes_correct_params(self):
        with patch("app.infrastructure.llm.gemini_provider.genai.Client") as mock_cls:
            from app.infrastructure.llm.gemini_provider import GeminiProvider

            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.models.generate_content.return_value.text = "ok"
            mock_client.models.generate_content.return_value.usage_metadata = None

            provider = GeminiProvider(api_key="AIza-test", model="gemini-pro")
            provider.generate("sys", "usr")

            call_kwargs = mock_client.models.generate_content.call_args.kwargs
            assert call_kwargs["model"] == "gemini-pro"
            assert call_kwargs["contents"] == "usr"

    def test_is_subclass_of_llm_provider(self):
        with patch("app.infrastructure.llm.gemini_provider.genai.Client"):
            from app.infrastructure.llm.gemini_provider import GeminiProvider

            assert issubclass(GeminiProvider, LLMProvider)
