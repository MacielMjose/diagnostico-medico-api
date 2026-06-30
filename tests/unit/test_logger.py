from app.core.logger import setup_logging


class TestLogger:
    """Testes para a configuração de logging"""

    def test_setup_logging_does_not_raise(self):
        mock_settings = type(
            "Settings",
            (),
            {
                "log_level": "INFO",
                "posthog_enabled": False,
                "posthog_api_key": "",
                "environment": "dev",
            },
        )()
        setup_logging(mock_settings)

    def test_setup_logging_with_debug_level(self):
        mock_settings = type(
            "Settings",
            (),
            {
                "log_level": "DEBUG",
                "posthog_enabled": False,
                "posthog_api_key": "",
                "environment": "dev",
            },
        )()
        setup_logging(mock_settings)

    def test_setup_logging_with_posthog_enabled(self):
        """Quando posthog_enabled=True, o handler OTel deve ser configurado sem erro."""
        mock_settings = type(
            "Settings",
            (),
            {
                "log_level": "INFO",
                "posthog_enabled": True,
                "posthog_api_key": "phc_fake_key_for_testing",
                "environment": "dev",
            },
        )()
        setup_logging(mock_settings)
