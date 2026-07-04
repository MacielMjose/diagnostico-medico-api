# Multi-stage build for Python FastAPI application + Ollama
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ src/

RUN pip install --no-cache-dir --user .

# ── Final stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Instalar Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copiar pacotes Python do builder
COPY --from=builder /root/.local /root/.local

# Variáveis de ambiente com valores padrão
# Sensíveis (API keys) vêm do AWS Secrets Manager em runtime
ENV PATH=/root/.local/bin:$PATH \
    LLM_PROVIDER=ollama \
    OLLAMA_BASE_URL=http://localhost:11434 \
    OLLAMA_MODEL=llama3.2 \
    POSTHOG_ENABLED=true \
    LOG_LEVEL=INFO \
    ENVIRONMENT=dev \
    APP_NAME=diagnostico-medico-api \
    MODEL_PATH=models/pcos_model.joblib

# Copiar código da aplicação
COPY --from=builder /app/src src/

# Copiar modelo ML
COPY models/ models/

# Copiar entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Entrypoint garante que Ollama está pronto antes de subir a API
ENTRYPOINT ["/entrypoint.sh"]
