from app.core.config import Settings


class TestSettings:
    """Testes para a configuração da aplicação (Settings)."""

    def test_default_values(self):
        settings = Settings()
        assert settings.model_path == "./models"
        assert settings.llm_model == "gpt-4"
        assert settings.log_level == "INFO"
        assert settings.max_image_size_mb == 10
        assert settings.llm_api_key == ""

    def test_custom_values(self, monkeypatch):
        monkeypatch.setenv("MODEL_PATH", "/custom/models")
        monkeypatch.setenv("LLM_API_KEY", "sk-test-key")
        monkeypatch.setenv("LLM_MODEL", "gpt-4-turbo")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "20")

        settings = Settings()
        assert settings.model_path == "/custom/models"
        assert settings.llm_api_key == "sk-test-key"
        assert settings.llm_model == "gpt-4-turbo"
        assert settings.log_level == "DEBUG"
        assert settings.max_image_size_mb == 20

    def test_model_path_is_string(self):
        settings = Settings()
        assert isinstance(settings.model_path, str)

    def test_llm_api_key_empty_by_default(self):
        settings = Settings()
        assert settings.llm_api_key == ""
