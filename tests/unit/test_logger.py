import logging

from app.core.logger import setup_logging


class TestLogger:
    """Testes para a configuração de logging"""

    def _make_settings(self, **overrides):
        defaults = {
            "log_level": "INFO",
            "posthog_enabled": False,
            "posthog_api_key": "",
            "environment": "dev",
        }
        defaults.update(overrides)
        return type("Settings", (), defaults)()

    def test_setup_logging_does_not_raise(self):
        setup_logging(self._make_settings())

    def test_setup_logging_with_debug_level(self):
        setup_logging(self._make_settings(log_level="DEBUG"))

    def test_setup_logging_with_posthog_enabled(self):
        """Quando posthog_enabled=True, o handler OTel deve ser configurado sem erro."""
        setup_logging(
            self._make_settings(
                posthog_enabled=True,
                posthog_api_key="phc_fake_key_for_testing",
            )
        )

    def test_root_logger_has_stream_handler(self):
        """basicConfig deve garantir um StreamHandler no root logger."""
        setup_logging(self._make_settings())
        handlers = logging.getLogger().handlers
        stream_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) >= 1

    def test_log_level_is_applied(self):
        """O nível de log das settings deve ser aplicado ao root logger."""
        setup_logging(self._make_settings(log_level="DEBUG"))
        assert logging.getLogger().level <= logging.DEBUG

    def test_structlog_works_after_setup(self):
        """Após setup_logging, structlog deve produzir logs sem erro."""
        import structlog

        setup_logging(self._make_settings())
        logger = structlog.get_logger("test")
        # Não deve levantar exceção
        logger.info("test_log_message", key="value")
