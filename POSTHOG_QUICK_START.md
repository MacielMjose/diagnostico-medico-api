# PostHog Quick Start Guide

## 1. Configuração Rápida (5 minutos)

### 1.1 Obter API Key
- Acesse [PostHog](https://posthog.com)
- Faça login com sua conta
- Copie seu **API Key** em Settings → Project

### 1.2 Configurar .env
```bash
# Adicione ao arquivo .env
POSTHOG_ENABLED=true
POSTHOG_API_KEY=seu_api_key_aqui
```

### 1.3 Reiniciar a API
A integração ativará automaticamente ao iniciar.

## 2. Verificar que Está Funcionando

### Opção A: Usar o exemplo
```bash
python examples/posthog_integration_example.py
```

### Opção B: Fazer requisições
```bash
# Terminal 1: Iniciar a API
uvicorn app.main:app --reload

# Terminal 2: Fazer requisições
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Age_yrs": 25,
    "Weight_kg": 70,
    "Height_m": 1.65,
    ...outras features...
  }'
```

### Opção C: Verificar os logs
Procure por mensagens tipo:
```
event_name=api_request endpoint=/api/v1/predict duration=0.123
```

## 3. Ver os Eventos no PostHog

1. Acesse seu projeto PostHog
2. Vá para **Insights**
3. Clique em **New Insight**
4. Selecione **Events** e escolha um evento:
   - `api_request` - requisições HTTP
   - `model_prediction` - previsões do modelo
   - `llm_request` - chamadas para LLM
   - `genetic_optimization` - otimizações genéticas

## 4. Criar Seu Primeiro Dashboard

### 4.1 Dashboard: Taxa de Sucesso
1. **New Insight**
2. Evento: `api_request`
3. Type: **Pie Chart**
4. Agrupar por: `status_code`
5. Visualizar sucessos (status < 400) vs erros

### 4.2 Dashboard: Latência
1. **New Insight**
2. Evento: `api_request`
3. Type: **Line Chart**
4. Property: `duration_ms`
5. Metric: **Average**
6. Interval: **Hourly**

### 4.3 Dashboard: Providers LLM
1. **New Insight**
2. Evento: `llm_request`
3. Type: **Bar Chart**
4. Agrupar por: `provider`

## 5. Estrutura de Eventos

```
api_request
├── endpoint: string (caminho da requisição)
├── method: string (GET, POST, etc.)
├── status_code: number
└── duration_ms: number

model_prediction
├── model_name: string
├── duration_ms: number
├── status: "success" | "error"
└── error: string (opcional)

llm_request
├── provider: string (openai, anthropic, etc.)
├── model: string (nome do modelo)
├── duration_ms: number
├── tokens_used: number (opcional)
├── status: "success" | "error"
└── error: string (opcional)

genetic_optimization
├── duration_ms: number
├── population_size: number
├── generations: number
├── mutation_rate: number
└── improvement: number (%)
```

## 6. Troubleshooting

| Problema | Solução |
|----------|---------|
| "Events not showing" | Aguarde 30s, PostHog tem latência de ingestão |
| "No events received" | Verifique se `POSTHOG_ENABLED=true` |
| "Invalid API key" | Copie a chave corretamente de PostHog Settings |
| "High latency" | PostHog é async, não deve afetar sua API |

## 7. Documentação Completa

- **Setup Detalhado**: `POSTHOG_SETUP.md`
- **Dashboard Templates**: `POSTHOG_DASHBOARDS.md`
- **Exemplos**: `examples/posthog_integration_example.py`

## 8. Próximos Passos

- [ ] Confirmar que eventos estão chegando
- [ ] Criar dashboard de Performance
- [ ] Configurar alertas (optional)
- [ ] Revisar métricas de SLA
- [ ] Documentar métricas importantes

## 9. Comandos Úteis

```bash
# Ver logs da API
uvicorn app.main:app --reload --log-level DEBUG

# Testar captura de eventos
python examples/posthog_integration_example.py

# Instalar dependências
pip install posthog>=3.0
```

## 10. Comparação: AWS + PostHog

| Métrica | Ferramenta | Dashboard |
|---------|-----------|-----------|
| CPU/Memory/Disk | AWS CloudWatch | AWS Console |
| Network I/O | AWS CloudWatch | AWS Console |
| HTTP Requests | PostHog | PostHog Insights |
| Response Time | PostHog | PostHog Insights |
| Error Rate | PostHog | PostHog Insights |
| Model Predictions | PostHog | PostHog Insights |
| LLM Usage | PostHog | PostHog Insights |

---

**Suporte**: Para dúvidas sobre PostHog, veja [docs.posthog.com](https://docs.posthog.com)
