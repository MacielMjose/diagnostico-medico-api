import pytest

from app.infrastructure.llm.base import LLMProvider, LLMResponse
from app.infrastructure.llm.harness import LLMFallbackError, LLMHarnessProvider


class _FakeProvider(LLMProvider):
    def __init__(self, name: str, response: LLMResponse | None = None) -> None:
        self._name = name
        self._response = response
        self.calls = 0

    @property
    def provider_name(self) -> str:
        return self._name

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        self.calls += 1
        if self._response is None:
            raise RuntimeError(f"{self._name} unavailable")
        return self._response


def test_harness_returns_first_successful_provider_response():
    first = _FakeProvider("openai/test", LLMResponse(text="ok", tokens_used=10))
    second = _FakeProvider("groq/test", LLMResponse(text="fallback"))
    harness = LLMHarnessProvider([first, second])

    response = harness.generate("system", "user")

    assert response.text == "ok"
    assert response.tokens_used == 10
    assert first.calls == 1
    assert second.calls == 0


def test_harness_falls_back_when_provider_raises():
    first = _FakeProvider("openai/test")
    second = _FakeProvider("groq/test", LLMResponse(text="fallback", tokens_used=20))
    harness = LLMHarnessProvider([first, second])

    response = harness.generate("system", "user")

    assert response.text == "fallback"
    assert response.tokens_used == 20
    assert first.calls == 1
    assert second.calls == 1


def test_harness_raises_when_all_providers_fail():
    harness = LLMHarnessProvider(
        [_FakeProvider("openai/test"), _FakeProvider("groq/test")]
    )

    with pytest.raises(LLMFallbackError, match="Todos os providers LLM falharam"):
        harness.generate("system", "user")


def test_harness_requires_at_least_one_provider():
    with pytest.raises(ValueError, match="at least one provider"):
        LLMHarnessProvider([])
