# PostHog Dashboard Examples

Este documento fornece exemplos de dashboards e insights que você pode criar no PostHog para monitorar a sua API.

## Dashboard 1: Performance Geral da API

Crie um novo dashboard chamado "API Performance" com os seguintes insights:

### Insight 1: Requisições por Segundo (Taxa de Throughput)
```
Evento: api_request
Tipo: Time Series
Métrica: Count
Intervalo: Por hora
```

### Insight 2: Status Codes (Distribuição)
```
Evento: api_request
Tipo: Bar Chart
Agrupamento: status_code
Métrica: Count
```

### Insight 3: Tempo de Resposta Médio (P95)
```
Evento: api_request
Tipo: Time Series
Propriedade: duration_ms
Métrica: 95th percentile
Intervalo: Por hora
```

### Insight 4: Endpoints Mais Lentos
```
Evento: api_request
Tipo: Table
Agrupamento: endpoint
Propriedade: duration_ms
Métrica: Average
Ordenação: Decrescente
```

## Dashboard 2: Análise de Predições (Modelo ML)

Crie um novo dashboard chamado "Model Predictions Analytics":

### Insight 1: Taxa de Sucesso de Predições
```
Evento: model_prediction
Tipo: Pie Chart
Agrupamento: status
Métrica: Count
```

### Insight 2: Tempo Médio de Predição
```
Evento: model_prediction
Tipo: Single Value
Propriedade: duration_ms
Métrica: Average
```

### Insight 3: Volume de Predições ao Longo do Tempo
```
Evento: model_prediction
Tipo: Line Chart
Métrica: Count
Intervalo: Por dia
```

### Insight 4: Taxa de Erro (últimos 7 dias)
```
Evento: model_prediction
Filtro: status = "error"
Tipo: Single Value
Métrica: Count
```

## Dashboard 3: Integração com LLM

Crie um novo dashboard chamado "LLM Integration Metrics":

### Insight 1: Distribuição de Providers LLM
```
Evento: llm_request
Tipo: Pie Chart
Agrupamento: provider
Métrica: Count
```

### Insight 2: Tempo Médio por Provider
```
Evento: llm_request
Tipo: Bar Chart
Agrupamento: provider
Propriedade: duration_ms
Métrica: Average
```

### Insight 3: Modelos Mais Utilizados
```
Evento: llm_request
Tipo: Bar Chart
Agrupamento: model
Métrica: Count
Ordenação: Decrescente
```

### Insight 4: Taxa de Erro de LLM
```
Evento: llm_request
Filtro: status = "error"
Tipo: Time Series
Métrica: Count
Intervalo: Por hora
```

### Insight 5: Consumo de Tokens (se disponível)
```
Evento: llm_request
Tipo: Single Value
Propriedade: tokens_used
Métrica: Sum
```

## Dashboard 4: Otimização Genética

Crie um novo dashboard chamado "Genetic Optimization":

### Insight 1: Execuções de Otimização por Dia
```
Evento: genetic_optimization
Tipo: Line Chart
Métrica: Count
Intervalo: Por dia
```

### Insight 2: Melhoria Média (%)
```
Evento: genetic_optimization
Tipo: Single Value
Propriedade: improvement
Métrica: Average
Suffix: %
```

### Insight 3: Duração Média de Otimização
```
Evento: genetic_optimization
Tipo: Single Value
Propriedade: duration_ms
Métrica: Average
Suffix: ms
```

### Insight 4: Configurações Mais Comuns
```
Evento: genetic_optimization
Tipo: Table
Agrupamento: [population_size, generations, mutation_rate]
Métrica: Count
```

## Dashboard 5: Saúde da API (Operacional)

Crie um novo dashboard chamado "API Health":

### Insight 1: Uptime da API
```
Evento: health_check
Tipo: Line Chart
Métrica: Count
Intervalo: Por hora
```

### Insight 2: Últimas Startups e Shutdowns
```
Evento: api_startup OR api_shutdown
Tipo: Table
Propriedade: timestamp
Limite: 10 eventos mais recentes
```

### Insight 3: Taxa de Erros (últimas 24h)
```
Evento: api_request
Filtro: status_code >= 400
Tipo: Time Series
Métrica: Count
Intervalo: Por hora
```

## Alertas Recomendados

Configure os seguintes alertas no PostHog:

### Alerta 1: Taxa de Erro Elevada
```
Condição: Quando "api_request" com status_code >= 400 > 5 em 10 minutos
Ação: Notificar via email/Slack
```

### Alerta 2: Latência Elevada
```
Condição: Quando "api_request" duration_ms P95 > 5000ms
Ação: Notificar via email/Slack
```

### Alerta 3: Falha de Previsão
```
Condição: Quando "model_prediction" status = "error" > 0 em 1 hora
Ação: Notificar via email/Slack
```

### Alerta 4: Falha de LLM
```
Condição: Quando "llm_request" status = "error" > 3 em 1 hora
Ação: Notificar via email/Slack
```

## Como Criar Alertas no PostHog

1. Vá para **Settings** → **Alerts**
2. Clique em **Create Alert**
3. Configure a condição desejada
4. Defina o canal de notificação (email, Slack, webhook)
5. Salve o alerta

## Exportando Dados

O PostHog permite exportar dados para análise externa:

1. Acesse uma insight
2. Clique em **Export**
3. Escolha o formato (CSV, JSON)
4. Download dos dados

## Integrando com Slack

Para receber notificações no Slack:

1. Vá para **Settings** → **Integrations**
2. Conecte sua workspace do Slack
3. Ao configurar um alerta, escolha "Slack" como ação
4. Selecione o canal

## Comparando Períodos

Use a funcionalidade "Compare Periods" para:

- Comparar performance de semanas diferentes
- Validar impacto de mudanças
- Identificar tendências

Para usar:
1. Abra uma insight
2. Clique em **Compare**
3. Selecione dois períodos diferentes

## Criando Cohorts (Grupos de Eventos)

Crie cohorts para segmentar análise:

```
Cohorte: "Requisições com Sucesso"
Filtro: api_request status_code < 400

Cohorte: "Predições Rápidas"
Filtro: model_prediction duration_ms < 1000

Cohorte: "Usando OpenAI"
Filtro: llm_request provider = "openai"
```

## Dicas de Performance

1. **Use filtros**: Limitar dados reduz o tempo de cálculo
2. **Intervalo apropriado**: Use "por hora" para últimas 24h, "por dia" para períodos maiores
3. **Métricas simples**: Count é mais rápido que percentiles
4. **Cache de dados**: PostHog cacheia resultados automaticamente

## Próximos Passos

- [ ] Criar dashboard "API Performance"
- [ ] Configurar alerta de taxa de erro
- [ ] Configurar integração com Slack
- [ ] Revisar dashboards semanalmente
- [ ] Documentar métricas SLA para a API
