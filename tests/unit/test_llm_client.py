from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.infrastructure.llm_client import LLMClient


class TestLLMClient:
    """Testes para o LLMClient (comunicação com API OpenAI)."""

    def _mock_post(self, status_code=200, response_data=None):
        if response_data is None:
            response_data = {
                "choices": [{"message": {"content": "Resposta simulada."}}]
            }
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = response_data
        if status_code >= 400:
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=mock_response
            )
        mock_post = AsyncMock()
        mock_post.return_value = mock_response
        return mock_post

    @pytest.mark.asyncio
    async def test_chat_returns_response_content(self):
        client = LLMClient(api_key="sk-test", model="gpt-4")
        mock_post = self._mock_post()

        with patch.object(httpx.AsyncClient, "post", mock_post):
            result = await client.chat("Olá, tudo bem?")

        assert result == "Resposta simulada."

    @pytest.mark.asyncio
    async def test_chat_sends_correct_payload(self):
        client = LLMClient(api_key="sk-test", model="gpt-4")
        mock_post = self._mock_post()

        with patch.object(httpx.AsyncClient, "post", mock_post):
            await client.chat("Meu prompt de teste")

        # Verifica se a chamada foi feita com os parâmetros corretos
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["model"] == "gpt-4"
        assert call_kwargs["json"]["messages"][0]["content"] == "Meu prompt de teste"
        assert call_kwargs["headers"]["Authorization"] == "Bearer sk-test"

    @pytest.mark.asyncio
    async def test_chat_raises_on_http_error(self):
        client = LLMClient(api_key="sk-test", model="gpt-4")
        mock_post = self._mock_post(status_code=401)

        with patch.object(httpx.AsyncClient, "post", mock_post):
            with pytest.raises(httpx.HTTPStatusError):
                await client.chat("prompt")

    @pytest.mark.asyncio
    async def test_chat_sends_correct_url_and_timeout(self):
        client = LLMClient(api_key="sk-test", model="gpt-4")
        mock_post = self._mock_post()

        with patch.object(httpx.AsyncClient, "post", mock_post):
            await client.chat("prompt")

        called_url = mock_post.call_args.args[0]
        assert "chat/completions" in called_url
        assert mock_post.call_args.kwargs["timeout"] == 30.0
