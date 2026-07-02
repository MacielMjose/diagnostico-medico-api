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


def capture_prediction(
    model_name: str,
    duration: float,
    status: str = "success",
    error: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "model_name": model_name,
        "duration_ms": round(duration * 1000, 2),
        "status": status,
    }
    if error:
        properties["error"] = error

    distinct_id = user_id or "api_server"
    capture_event("model_prediction", distinct_id, properties)


def capture_llm_request(
    provider: str,
    model: str,
    duration: float,
    tokens_used: Optional[int] = None,
    status: str = "success",
    error: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    properties = {
        "provider": provider,
        "model": model,
        "duration_ms": round(duration * 1000, 2),
        "status": status,
    }
    if tokens_used:
        properties["tokens_used"] = tokens_used
    if error:
        properties["error"] = error

    distinct_id = user_id or "api_server"
    capture_event("llm_request", distinct_id, properties)


def close_posthog() -> None:
    client = get_posthog_client()
    if client:
        try:
            client.shutdown()
        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.error("Failed to shutdown PostHog", error=str(e), exc_info=True)
