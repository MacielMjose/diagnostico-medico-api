from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import Settings
from app.core.logger import setup_logging
from app.domain.exceptions import (
    InvalidFeaturesError,
    LLMRequestError,
    ModelNotLoadedError,
)
from app.infrastructure.secrets_manager import get_secret_or_env
from app.monitoring.middleware import TimingMiddleware
from app.monitoring.posthog import capture_event, close_posthog, init_posthog


def create_app() -> FastAPI:
    settings = Settings()
    setup_logging(settings)

    # Fetch PostHog API Key from AWS Secrets Manager (or env var for local dev)
    if settings.posthog_enabled:
        try:
            posthog_api_key = get_secret_or_env(
                env_var_name="POSTHOG_API_KEY",
                secret_path=f"{settings.app_name}/{settings.environment}/posthog_api_key",
            )
            settings.posthog_api_key = posthog_api_key
        except ValueError as e:
            import structlog
            logger = structlog.get_logger()
            logger.warning(
                "posthog_api_key_not_found",
                error=str(e),
                message="PostHog disabled due to missing API key",
            )
            settings.posthog_enabled = False

    init_posthog(settings)

    app = FastAPI(
        title="PCOS Diagnosis API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TimingMiddleware)

    @app.exception_handler(ModelNotLoadedError)
    async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
        return JSONResponse(status_code=503, content={"error": str(exc)})

    @app.exception_handler(InvalidFeaturesError)
    async def invalid_features_handler(request: Request, exc: InvalidFeaturesError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(LLMRequestError)
    async def llm_error_handler(request: Request, exc: LLMRequestError):
        return JSONResponse(status_code=502, content={"error": str(exc)})

    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/health")
    async def health():
        capture_event("health_check")
        return {"status": "ok", "version": "1.0.0"}

    @app.on_event("startup")
    async def startup():
        capture_event("api_startup")

    @app.on_event("shutdown")
    async def shutdown():
        capture_event("api_shutdown")
        close_posthog()

    return app


app = create_app()
