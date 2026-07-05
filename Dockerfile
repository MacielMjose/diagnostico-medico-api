# Multi-stage build for Python FastAPI application
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
    && rm -rf /var/lib/apt/lists/*

# Copiar pacotes Python do builder
COPY --from=builder /root/.local /root/.local

# Variáveis de ambiente com valores padrão
# Sensíveis (API keys) vêm do AWS Secrets Manager em runtime
ENV PATH=/root/.local/bin:$PATH \
    LLM_PROVIDER=groq \
    GROQ_MODEL=llama-3.1-8b-instant \
    POSTHOG_ENABLED=true \
    LOG_LEVEL=INFO \
    ENVIRONMENT=dev \
    APP_NAME=diagnostico-medico-api \
    MODEL_PATH=models/pcos_model.joblib

# Copiar código da aplicação
COPY --from=builder /app/src src/

# Copiar modelo ML
COPY models/ models/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
