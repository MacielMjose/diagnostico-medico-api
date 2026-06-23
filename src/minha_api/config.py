from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM provider: "openai" | "anthropic" | "ollama" | "gemini"
    llm_provider: str = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    model_path: str = "models/pcos_model.joblib"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
