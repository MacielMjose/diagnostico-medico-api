from app.core.config import Settings


class TestSettings:
    """Testes para a configuração da aplicação (Settings)."""

    def test_default_values(self):
        settings = Settings()
        assert settings.model_path == "models/pcos_model.joblib"
        assert settings.log_level == "INFO"
        assert settings.max_image_size_mb == 10
        assert settings.llm_provider == "openai"
        assert settings.llm_fallback_providers == ""

    def test_custom_values(self, monkeypatch):
        monkeypatch.setenv("MODEL_PATH", "models/custom.joblib")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "20")
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_FALLBACK_PROVIDERS", "groq,gemini")

        settings = Settings()
        assert settings.model_path == "models/custom.joblib"
        assert settings.log_level == "DEBUG"
        assert settings.max_image_size_mb == 20
        assert settings.llm_provider == "anthropic"
        assert settings.llm_fallback_providers == "groq,gemini"

    def test_model_path_is_string(self):
        settings = Settings()
        assert isinstance(settings.model_path, str)

    def test_openai_api_key_empty_by_default(self):
        settings = Settings()
        assert settings.openai_api_key == ""
