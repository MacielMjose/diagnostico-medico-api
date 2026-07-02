from openai import OpenAI

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @property
    def provider_name(self) -> str:
        return f"openai/{self._model}"

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        tokens = None
        if response.usage:
            tokens = response.usage.total_tokens
        return LLMResponse(text=response.choices[0].message.content, tokens_used=tokens)
