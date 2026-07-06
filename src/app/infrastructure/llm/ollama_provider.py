import httpx

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Chama Ollama via endpoint OpenAI-compatível (/v1/chat/completions)."""

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    @property
    def provider_name(self) -> str:
        return f"ollama/{self._model}"

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        response = httpx.post(
            f"{self._base_url}/v1/chat/completions",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 800,
                "stream": False,
            },
            timeout=180.0,
        )
        response.raise_for_status()
        data = response.json()
        tokens = None
        usage = data.get("usage")
        if usage:
            tokens = usage.get("total_tokens")
        return LLMResponse(
            text=data["choices"][0]["message"]["content"], tokens_used=tokens
        )
