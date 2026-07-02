from google import genai
from google.genai import types

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    @property
    def provider_name(self) -> str:
        return f"gemini/{self._model}"

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                max_output_tokens=800,
            ),
        )
        tokens = None
        if response.usage_metadata:
            tokens = response.usage_metadata.total_token_count
        return LLMResponse(text=response.text, tokens_used=tokens)
