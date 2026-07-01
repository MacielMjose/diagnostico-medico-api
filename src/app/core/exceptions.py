import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(
        "app_exception",
        path=request.url.path,
        status_code=exc.status_code,
        detail=exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )
