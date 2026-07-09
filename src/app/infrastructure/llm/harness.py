import structlog

from app.infrastructure.llm.base import LLMProvider, LLMResponse

logger = structlog.get_logger()


class LLMFallbackError(RuntimeError):
    """Raised when every provider in the LLM harness fails."""


class LLMHarnessProvider(LLMProvider):
    """Sequential fallback harness for multiple LLM providers."""

    def __init__(self, providers: list[LLMProvider]) -> None:
        if not providers:
            raise ValueError("LLM harness requires at least one provider.")
        self._providers = providers

    @property
    def provider_name(self) -> str:
        chain = " -> ".join(provider.provider_name for provider in self._providers)
        return f"harness[{chain}]"

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        failures: list[str] = []

        for index, provider in enumerate(self._providers):
            provider_name = provider.provider_name
            logger.info(
                "llm_harness_attempt_started",
                provider=provider_name,
                fallback_index=index,
            )

            try:
                response = provider.generate(system_prompt, user_prompt)
                logger.info(
                    "llm_harness_attempt_succeeded",
                    provider=provider_name,
                    fallback_index=index,
                    fallback_used=index > 0,
                )
                return response
            except Exception as exc:
                error = f"{provider_name}: {type(exc).__name__}: {exc}"
                failures.append(error)
                logger.warning(
                    "llm_harness_attempt_failed",
                    provider=provider_name,
                    fallback_index=index,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

        raise LLMFallbackError(
            "Todos os providers LLM falharam. Tentativas: " + " | ".join(failures)
        )
