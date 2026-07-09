import logging

import structlog
from opentelemetry import _logs as otel_logs
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


def setup_logging(settings):
    """Configura structlog + OpenTelemetry para envio de logs ao PostHog.

    Fluxo
    -----
    structlog → stdlib logging → LoggingHandler (OTel) → PostHog Logs
                                 → StreamHandler (console) → stdout/stderr

    A ordem é importante:
    1. ``logging.basicConfig`` garantante um StreamHandler no root logger ANTES
       de qualquer outro handler ser adicionado. Sem isso, o handler OTel pode
       ser o único e, se ele falhar silenciosamente, nenhum log aparece.
    2. O handler OTel é adicionado ao root logger para que qualquer log
       ``logger.info / .warning / .error`` via structlog também seja exportado
       para a aba **Logs** do PostHog (não confundir com a aba **Activity**,
       que recebe eventos de produto via ``posthog.capture()``).
    3. ``structlog.configure`` conecta o structlog ao stdlib logging, permitindo
       que os logs atravessem todos os handlers registrados no root logger.
    """
    # ── 1. Console handler (garante output local) ────────────────────────
    log_level = getattr(settings, "log_level", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level)
    # Garante que o root logger tenha o nível correto mesmo que basicConfig
    # seja um no-op (já existem handlers de testes anteriores, por exemplo).
    logging.root.setLevel(numeric_level)

    # ── 2. OpenTelemetry → PostHog Logs (aba Logs, NÃO Activity) ─────────
    if settings.posthog_enabled and settings.posthog_api_key:
        logger_provider = LoggerProvider()
        otel_logs.set_logger_provider(logger_provider)

        otlp_exporter = OTLPLogExporter(
            endpoint="https://us.i.posthog.com/i/v1/logs",
            headers={"Authorization": f"Bearer {settings.posthog_api_key}"},
        )

        logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

        # Handler OTel: converte registros stdlib → OTLP e envia ao PostHog.
        # O handler não tem nível próprio — herda o do root logger.
        otel_handler = LoggingHandler(logger_provider=logger_provider)
        logging.getLogger().addHandler(otel_handler)

    # ── 3. structlog → stdlib logging ─────────────────────────────────────
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
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ── 4. Log de diagnóstico (confirma que o pipeline está ativo) ────────
    diag_logger = structlog.get_logger("logging.setup")
    diag_logger.info(
        "logging_setup_completed",
        log_level=log_level,
        otel_enabled=settings.posthog_enabled,
        environment=getattr(settings, "environment", "dev"),
    )
