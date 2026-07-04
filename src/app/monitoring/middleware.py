import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.monitoring.posthog import capture_request

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        process_time = time.time() - start
        response.headers["X-Process-Time"] = str(process_time)

        request_id = getattr(request.state, "request_id", None)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            duration=process_time,
            status_code=response.status_code,
            request_id=request_id,
        )
        capture_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration=process_time,
        )
        return response
