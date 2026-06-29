import logging

import structlog
from opentelemetry import logs as otel_logs
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor


def setup_logging(settings):
    """
    Configura structlog + OpenTelemetry para envio de logs ao PostHog.

    Fluxo:
        structlog → stdlib logging → LoggingHandler (OTel) → PostHog Logs
    """
    # ── 1. OpenTelemetry → PostHog Logs ──────────────────────────────────
    if settings.posthog_enabled and settings.posthog_api_key:
        logger_provider = LoggerProvider()
        otel_logs.set_logger_provider(logger_provider)

        otlp_exporter = OTLPLogExporter(
            endpoint="https://us.i.posthog.com/i/v1/logs",
            headers={"Authorization": f"Bearer {settings.posthog_api_key}"},
        )

        logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

        # Adiciona o handler OTel ao root logger do Python stdlib
        otel_handler = LoggingHandler(logger_provider=logger_provider)
        otel_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(otel_handler)

    # ── 2. structlog → stdlib logging (necessário para o handler OTel pegar) ─
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Renderiza JSON em produção, legível em dev
            structlog.processors.JSONRenderer()
            if getattr(settings, "environment", "dev") == "production"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),  # ← stdlib, não PrintLogger
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Nível mínimo do root logger
    logging.basicConfig(level=logging.INFO)
