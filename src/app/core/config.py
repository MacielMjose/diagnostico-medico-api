import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM provider: "openai" | "anthropic" | "ollama" | "gemini" | "groq"
    llm_provider: str = "openai"
    # Ordered, comma-separated fallback providers tried after llm_provider.
    llm_fallback_providers: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    # Path to the serialized model artifact (dict with pipeline/explainer/...).
    model_path: str = "models/pcos_model.joblib"

    log_level: str = "INFO"
    max_image_size_mb: int = 10

    # Application metadata
    app_name: str = "diagnostico-medico-api"
    environment: str = os.environ.get("ENVIRONMENT", "dev")

    # PostHog analytics
    posthog_api_key: str = ""
    posthog_enabled: bool = os.environ.get("POSTHOG_ENABLED", "false").lower() == "true"
