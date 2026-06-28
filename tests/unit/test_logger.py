
from app.core.logger import setup_logging


class TestLogger:
    """Testes para a configuração de logging"""

    def test_setup_logging_does_not_raise(self):
        mock_settings = type("Settings", (), {"log_level": "INFO"})()
        setup_logging(mock_settings)

    def test_setup_logging_with_debug_level(self):
        mock_settings = type("Settings", (), {"log_level": "DEBUG"})()
        setup_logging(mock_settings)
