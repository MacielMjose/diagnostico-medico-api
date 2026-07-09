"""PostHog analytics — capture de eventos de produto.

Este módulo envia eventos para a aba **Activity** do PostHog (monitoramento
de comportamento de produto). Não confundir com a aba **Logs**, que recebe
logs técnicos de infraestrutura via OpenTelemetry/OTLP (configurado em
``app.core.logger.setup_logging``).

Fluxo dos dois canais complementares
-------------------------------------
- ``capture_*()`` (este módulo) → PostHog **Activity** (eventos de produto)
  Ex.: prediction_success, llm_success, api_startup, api_request.
- ``logger.info() / .error() / .warning()`` (structlog) → PostHog **Logs**
  via OTLP (logs técnicos de infraestrutura).
  Ex.: prediction_completed, llm_explanation_completed, request_completed.
"""

from typing import Any, Optional

from posthog import Posthog

from app.core.config import Settings

_posthog_client: Optional[Posthog] = None


def init_posthog(settings: Settings) -> Optional[Posthog]:
    global _posthog_client
    if settings.posthog_enabled and settings.posthog_api_key:
        _posthog_client = Posthog(
            project_api_key=settings.posthog_api_key,
            host="https://us.posthog.com",
        )
        return _posthog_client
    return None


def get_posthog_client() -> Optional[Posthog]:
    return _posthog_client


def capture_event(
    event_name: str,
    distinct_id: str = "api_server",
    properties: Optional[dict[str, Any]] = None,
) -> None:
    client = get_posthog_client()
    if client:
        try:
            properties = properties or {}
            client.capture(
                distinct_id=distinct_id,
                event=event_name,
                properties=properties,
            )
        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.error("Failed to capture PostHog event", error=str(e), exc_info=True)


def capture_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration: float,
    error: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
    }
    if error:
        properties["error"] = error

    distinct_id = user_id or "api_server"
    capture_event("api_request", distinct_id, properties)


def capture_prediction_success(
    model_name: str,
    duration: float,
    endpoint: str = "/predict",
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "model_name": model_name,
        "duration_ms": round(duration * 1000, 2),
        "endpoint": endpoint,
    }
    distinct_id = user_id or "api_server"
    capture_event("prediction_success", distinct_id, properties)


def capture_prediction_error(
    model_name: str,
    duration: float,
    error: str,
    endpoint: str = "/predict",
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "model_name": model_name,
        "duration_ms": round(duration * 1000, 2),
        "endpoint": endpoint,
        "error": error,
    }
    distinct_id = user_id or "api_server"
    capture_event("prediction_error", distinct_id, properties)


def capture_llm_success(
    provider: str,
    model: str,
    duration: float,
    tokens_used: Optional[int] = None,
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "provider": provider,
        "model": model,
        "duration_ms": round(duration * 1000, 2),
    }
    if tokens_used:
        properties["tokens_used"] = tokens_used
    distinct_id = user_id or "api_server"
    capture_event("llm_success", distinct_id, properties)


def capture_llm_error(
    provider: str,
    model: str,
    duration: float,
    error: str,
    tokens_used: Optional[int] = None,
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "provider": provider,
        "model": model,
        "duration_ms": round(duration * 1000, 2),
        "error": error,
    }
    if tokens_used:
        properties["tokens_used"] = tokens_used
    distinct_id = user_id or "api_server"
    capture_event("llm_error", distinct_id, properties)


def close_posthog() -> None:
    client = get_posthog_client()
    if client:
        try:
            client.shutdown()
        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.error("Failed to shutdown PostHog", error=str(e), exc_info=True)
