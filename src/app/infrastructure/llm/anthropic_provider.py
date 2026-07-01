import anthropic

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    @property
    def provider_name(self) -> str:
        return f"anthropic/{self._model}"

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.3,
        )
        tokens = None
        if message.usage:
            tokens = message.usage.input_tokens + message.usage.output_tokens
        return LLMResponse(text=message.content[0].text, tokens_used=tokens)
