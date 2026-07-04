#!/bin/bash
set -e

echo "[entrypoint] Iniciando Ollama server em background..."
ollama serve &
OLLAMA_PID=$!

echo "[entrypoint] Aguardando Ollama estar pronto..."
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "[entrypoint] Ollama ainda não está pronto, aguardando..."
    sleep 2
done

echo "[entrypoint] Ollama pronto. Fazendo pull do modelo ${OLLAMA_MODEL:-llama3.2}..."
ollama pull "${OLLAMA_MODEL:-llama3.2}"

echo "[entrypoint] Modelo baixado. Iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
