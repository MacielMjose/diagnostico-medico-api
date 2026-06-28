# PostHog Integration Guide

Este documento explica como configurar e usar o PostHog para monitorar eventos e métricas de uso na API de diagnóstico médico.

## O que é PostHog?

PostHog é uma plataforma de análise de produto open-source que permite rastrear eventos de uso, entender o comportamento dos usuários e medir performance da aplicação. Diferente do Prometheus (que foca em métricas de infraestrutura), PostHog captura **eventos** de negócio e uso.

## Configuração

### 1. Criar Conta PostHog

1. Acesse [PostHog](https://posthog.com) e crie uma conta
2. Após criar a conta, você receberá um **API Key**
3. Você também terá acesso a um **Project ID** (opcional, mas útil)

### 2. Configurar Variáveis de Ambiente

No seu arquivo `.env`, adicione:

```env
POSTHOG_ENABLED=true
POSTHOG_API_KEY=seu_api_key_aqui
```

Se não quiser usar PostHog, simplesmente deixe `POSTHOG_ENABLED=false` ou não configure a variável.

### 3. Instalar Dependências

A dependência `posthog>=3.0` já está adicionada no `pyproject.toml`. Se precisar reinstalar:

```bash
pip install posthog>=3.0
```

## Eventos Capturados

A integração captura automaticamente os seguintes eventos:

### Eventos de Requisição HTTP
- **Event**: `api_request`
- **Properties**:
  - `endpoint`: caminho da requisição
  - `method`: GET, POST, PUT, DELETE, etc.
  - `status_code`: código HTTP de resposta
  - `duration_ms`: tempo de processamento em milissegundos

### Eventos de Previsão (Predict)
- **Event**: `model_prediction`
- **Properties**:
  - `model_name`: nome do modelo usado
  - `duration_ms`: tempo de execução
  - `status`: "success" ou "error"
  - `error`: mensagem de erro (se houver)

### Eventos de LLM (Explain)
- **Event**: `llm_request`
- **Properties**:
  - `provider`: "openai", "anthropic", "ollama", "gemini"
  - `model`: nome do modelo LLM
  - `duration_ms`: tempo de processamento
  - `tokens_used`: número de tokens (se disponível)
  - `status`: "success" ou "error"
  - `error`: mensagem de erro (se houver)

### Eventos de Sistema
- **Event**: `api_startup` - quando a API inicia
- **Event**: `api_shutdown` - quando a API é desligada
- **Event**: `health_check` - quando o endpoint `/health` é acessado

## Dashboard e Análise

### Criar um Dashboard no PostHog

1. Acesse seu projeto PostHog
2. Vá para **Insights**
3. Crie uma nova insight clicando em **New Insight**

### Exemplos de Análises Úteis

#### 1. Taxa de Sucesso de Previsões
```
Evento: model_prediction
Filtro: status = "success"
Agrupamento: model_name
Métrica: Count
```

#### 2. Performance Média das Requisições
```
Evento: api_request
Propriedade: duration_ms
Cálculo: Average
Agrupamento: endpoint
```

#### 3. Distribuição de Providers LLM
```
Evento: llm_request
Agrupamento: provider
Métrica: Count
```

#### 4. Erros por Endpoint
```
Evento: api_request
Filtro: status_code >= 400
Agrupamento: endpoint
Métrica: Count
```

## Integração com AWS Dashboards

PostHog completa os dashboards AWS existentes:

| Métrica | Ferramenta | Tipo |
|---------|-----------|------|
| CPU/Memória | AWS CloudWatch | Infraestrutura |
| Requisições HTTP | PostHog | Negócio/Uso |
| Tempo de Resposta | PostHog | Performance |
| Erros de Previsão | PostHog | Aplicação |
| Uso de LLM | PostHog | Aplicação |

## Adicionando Eventos Customizados

Para adicionar novos eventos, use as funções do módulo `app.monitoring.posthog`:

```python
from app.monitoring.posthog import capture_event

# Evento simples
capture_event("meu_evento")

# Evento com propriedades
capture_event(
    "usuario_login",
    distinct_id="usuario_123",
    properties={
        "tipo_conta": "premium",
        "localizacao": "brasil"
    }
)
```

### Funções Disponíveis

```python
# Eventos genéricos
capture_event(event_name, distinct_id, properties)

# Eventos específicos (com schema)
capture_request(endpoint, method, status_code, duration, error, user_id)
capture_prediction(model_name, duration, status, error, user_id)
capture_llm_request(provider, model, duration, tokens_used, status, error, user_id)
```

## Performance e Melhores Práticas

1. **Não envie dados sensíveis**: evite incluir dados de pacientes, senhas ou tokens
2. **Use distinct_id apropriado**: para rastrear usuários, use um ID único (não é obrigatório)
3. **Batelamento**: PostHog automaticamente agrupa eventos antes de enviar
4. **Shutdown**: Os eventos são enviados com buffer, então deixe a API desligar naturalmente
5. **Desabilitar em Teste**: Configure `POSTHOG_ENABLED=false` no ambiente de teste

## Troubleshooting

### PostHog não está capturando eventos

1. Verifique se `POSTHOG_ENABLED=true`
2. Verifique se `POSTHOG_API_KEY` está correto
3. Verifique os logs da aplicação para erros
4. Aguarde alguns segundos, pois há um buffer de envio

### Eventos aparecem como "unknown" no PostHog

Isso é normal no PostHog. Nomes de eventos e propriedades aparecem como "unknown" até que haja tráfego suficiente ou você os configure manualmente.

### Performance afetada

PostHog envia eventos de forma assíncrona e com batelamento, então o impacto de performance é mínimo. Se notar latência aumentada, verifique a latência de rede para `us.posthog.com`.

## Referências

- [PostHog Documentation](https://posthog.com/docs)
- [Python SDK](https://posthog.com/docs/libraries/python)
- [Best Practices](https://posthog.com/docs/best-practices)
