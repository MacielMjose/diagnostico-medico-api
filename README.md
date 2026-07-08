# Diagnóstico Médico API — SOP/PCOS

API de suporte diagnóstico para **Síndrome dos Ovários Policísticos (SOP/PCOS)** desenvolvida como parte do Tech Challenge — Fase 2 do programa IADT.

Combina um modelo de **Regressão Logística** treinado em dados clínicos com **explicabilidade SHAP** e **interpretação em linguagem natural via LLM**, permitindo que médicos recebam não apenas um resultado numérico, mas uma análise clínica contextualizada.

## Stack

- **API**: FastAPI + Uvicorn
- **ML**: scikit-learn (Regressão Logística)
- **LLM**: OpenAI, Anthropic Claude, Google Gemini, Groq, Ollama (local)
- **Monitoramento**: Prometheus, structlog, PostHog, OpenTelemetry
- **Infra**: Docker, Terraform (AWS ECS Fargate)
- **CI/CD**: GitHub Actions

---

## Arquitetura

```
POST /api/v1/predict              POST /api/v1/explain              POST /api/v1/analysis
       │                                  │                                │
       ▼                                  ▼                                ▼
 PCOSInput (20 campos)     features + diagnóstico      PCOSInput (20 campos)
       │                   + probabilidade                      │
       ▼                         │                               ▼
 predictor.py              llm_explainer.py          predict + explain (una única chamada)
   Regressão Logística       Prompt Engineering          ↓
   (diagnóstico,            + LLM Integration       AnalysisOutput
    probabilidade,              ↓                   (diagnosis, probability,
    top contribuições)      Explicação clínica      confidence, explanation,
                            em linguagem natural    risk_factors, insights,
                                                    top_contributing_features)

                    LLM Providers:
                ┌───────────────────────────────────────┐
                │ OpenAI  Anthropic  Groq  Gemini  Ollama
                │ GPT-4o  Claude    Llama  Flash   Local
                └───────────────────────────────────────┘
```

**Três fluxos disponíveis:**

- **`/predict`** — Apenas diagnóstico com contribuições de features
- **`/explain`** — Apenas explicação clínica (requer resultado de predição)
- **`/analysis`** — Predição + Explicação em uma única chamada (mais conveniente)

### Estrutura do Projeto

```
diagnostico-medico-api/
├── .github/workflows/
│   └── pipeline.yml                # CI/CD: lint → test → build → push-ecr → deploy-fargate
├── terraform/                      # Infrastructure as Code (AWS Fargate)
│   ├── main.tf                     # VPC, subnets, security groups, backend
│   ├── ecr.tf                      # Docker image registry
│   ├── ecs.tf                      # Fargate cluster, tasks, service
│   ├── alb.tf                      # Load balancer and target groups
│   ├── autoscaling.tf              # Auto-scaling policies
│   ├── variables.tf, outputs.tf    # Configuration and outputs
│   └── terraform.*.tfvars          # Environment configs (dev/prod)
├── src/app/
│   ├── main.py                     # FastAPI — cria a app e registra rotas
│   ├── core/
│   │   ├── config.py               # Configurações via variáveis de ambiente
│   │   └── dependencies.py         # Injeção de dependências
│   ├── api/v1/                     # Rotas: predict, explain, analysis
│   ├── domain/                     # Modelos de domínio + mapeamento de features
│   ├── services/
│   │   ├── predictor.py            # Carregamento do modelo + predição com SHAP values
│   │   └── llm_explainer.py        # Prompt engineering + orquestração LLM
│   └── infrastructure/
│       ├── model_registry.py       # Carregamento do artefato joblib
│       └── llm/
│           ├── base.py             # Protocolo abstrato LLMProvider
│           ├── openai_provider.py, anthropic_provider.py, groq_provider.py, ...
│           └── factory.py          # Cria provider conforme LLM_PROVIDER
├── models/
│   └── pcos_model.joblib           # Artefato pré-construído do modelo
├── tests/
│   ├── api/test_predict_api.py     # Endpoints predict/explain/optimize
│   └── unit/                       # predictor, explainer, factory, GA
├── Dockerfile                      # Container image (multi-stage)
├── .dockerignore                   # Docker build optimization
├── Makefile                        # Convenience commands
├── .env.example                    # Environment template
├── mocks.md                        # Payloads mock para testes
├── pyproject.toml                  # Python project config
└── README.md                       # Este arquivo
```

### Modelo de ML

| Atributo                 | Valor                                                                                                                  |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Dataset                  | [PCOS Without Infertility — Kaggle](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos) |
| Algoritmo                | Regressão Logística (`class_weight='balanced'`)                                                                        |
| Features                 | Top 20 por correlação absoluta com o target                                                                            |
| Explicabilidade          | SHAP values + Interpretação via LLM                                                                                    |
| AUC-ROC (test set)       | ~0.95                                                                                                                  |
| Recall (classe positiva) | ~0.92                                                                                                                  |

As 20 features selecionadas incluem: número de folículos, AMH, padrão do ciclo menstrual, IMC, sintomas hiperandrogênicos (hirsutismo, acantose, acne) e marcadores laboratoriais.

---

## Quick Start

### Pré-requisitos

- **Python 3.12+**
- **Chave de API do provedor LLM** escolhido (OpenAI, Anthropic, Groq, Gemini, ou Ollama local)

### Instalação

```bash
# Clonar repositório
git clone <repo-url>
cd diagnostico-medico-api

# Instalar dependências
pip install -e ".[dev]"
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Provedor LLM: openai | anthropic | groq | gemini | ollama
# Padrão em container Docker: groq
# Padrão em desenvolvimento local: openai
LLM_PROVIDER=groq
# Fallbacks opcionais, em ordem, caso o provider primário falhe
LLM_FALLBACK_PROVIDERS=openai,gemini,ollama

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# Groq (recomendado — rápido e gratuito dentro de limites)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Google Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash

# Caminho para o artefato do modelo
MODEL_PATH=models/pcos_model.joblib

# PostHog (opcional)
POSTHOG_ENABLED=false
POSTHOG_API_KEY=seu_api_key
```

### Executar a API

```bash
uvicorn app.main:app --reload
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

> **Nota sobre LLM Provider**: Se nenhum `.env` for criado, a API usará `openai` como padrão (mas sem chave, endpoints `/explain` e `/analysis` retornarão erro). Em container Docker, o padrão é `groq`. Configure `LLM_PROVIDER` conforme necessário.

---

## Endpoints

Todas as rotas de negócio ficam sob o prefixo `/api/v1`.

### `GET /health`

Health check da API.

```json
{ "status": "ok", "version": "1.0.0" }
```

### `POST /api/v1/predict/`

Recebe os 20 campos clínicos e retorna a predição com explicabilidade SHAP.

**Request:**

```json
{
  "follicle_no_r": 12,
  "follicle_no_l": 10,
  "skin_darkening": 1,
  "hair_growth": 1,
  "weight_gain": 1,
  "cycle": 4,
  "fast_food": 1,
  "pimples": 0,
  "amh": 7.5,
  "bmi": 27.0,
  "cycle_length": 4,
  "hair_loss": 0,
  "age": 28,
  "hip": 40,
  "avg_f_size_l": 16.0,
  "marriage_status": 3.0,
  "endometrium": 9.0,
  "avg_f_size_r": 17.0,
  "pulse_rate": 74,
  "hb": 11.5
}
```

> Campos binários: `0` = Não, `1` = Sim. Campo `cycle`: `2` = Regular, `4` = Irregular.

**Response:**

```json
{
  "diagnosis": 1,
  "probability": 0.87,
  "confidence": "Alta",
  "model_version": "1.0.0",
  "top_contributing_features": [
    {
      "feature": "num__Follicle No. (R)",
      "contribution": 1.3123,
      "direction": "positiva"
    },
    {
      "feature": "num__Cycle(R/I)",
      "contribution": 0.6091,
      "direction": "positiva"
    },
    {
      "feature": "bin__hair growth(Y/N)",
      "contribution": 0.585,
      "direction": "positiva"
    },
    {
      "feature": "bin__Skin darkening (Y/N)",
      "contribution": 0.5542,
      "direction": "positiva"
    },
    {
      "feature": "num__Follicle No. (L)",
      "contribution": 0.4782,
      "direction": "positiva"
    }
  ]
}
```

Retorna `503` se o artefato do modelo não estiver disponível.

### `POST /api/v1/explain/`

Recebe o resultado da predição e gera a interpretação clínica via LLM.

**Request:**

```json
{
  "features": { "BMI": 27.0, "AMH(ng/mL)": 7.5, "Follicle No. (R)": 12 },
  "diagnosis": 1,
  "probability": 0.87
}
```

> **Validação de features:** é obrigatório enviar **pelo menos 15 das 20 features clínicas conhecidas** (nomes originais das colunas). Menos que isso retorna `400`.

**Response:**

```json
{
  "explanation": "O modelo de triagem indica resultado POSITIVO para SOP com probabilidade de 87%, sustentado principalmente pelo elevado número de folículos ovarianos e pelo padrão de ciclo irregular — achados consistentes com os critérios de Rotterdam...",
  "risk_factors": ["obesidade", "resistência insulínica", "hirsutismo"],
  "insights": [
    "solicitar perfil hormonal completo",
    "avaliar glicemia de jejum e insulina basal"
  ]
}
```

Retorna `502` se o provedor LLM falhar ou devolver formato inesperado.

### `POST /api/v1/analysis/`

**Novo endpoint** que combina `/predict` + `/explain` em uma única chamada. Ideal para fluxos que precisam de diagnóstico + explicação clínica simultaneamente.

**Request:** Mesmo formato de `/predict` (20 campos clínicos)

```json
{
  "follicle_no_r": 12,
  "follicle_no_l": 10,
  "skin_darkening": 1,
  "hair_growth": 1,
  "weight_gain": 1,
  "cycle": 4,
  "fast_food": 1,
  "pimples": 0,
  "amh": 7.5,
  "bmi": 27.0,
  "cycle_length": 4,
  "hair_loss": 0,
  "age": 28,
  "hip": 40,
  "avg_f_size_l": 16.0,
  "marriage_status": 3.0,
  "endometrium": 9.0,
  "avg_f_size_r": 17.0,
  "pulse_rate": 74,
  "hb": 11.5
}
```

**Response:** Combina dados de `/predict` com explicação LLM

```json
{
  "diagnosis": "positivo",
  "probability": 0.87,
  "confidence": "Alta",
  "explanation": "O modelo de triagem indica resultado POSITIVO para SOP com probabilidade de 87%, sustentado principalmente pelo elevado número de folículos ovarianos...",
  "risk_factors": ["obesidade", "resistência insulínica", "hirsutismo"],
  "insights": [
    "solicitar perfil hormonal completo",
    "avaliar glicemia de jejum"
  ],
  "top_contributing_features": [
    {
      "feature": "num__Follicle No. (R)",
      "contribution": 1.3123,
      "direction": "positiva"
    },
    {
      "feature": "num__Cycle(R/I)",
      "contribution": 0.6091,
      "direction": "positiva"
    }
  ]
}
```

---

**Integração LLM — agnóstica ao provedor**: basta alterar `LLM_PROVIDER` no `.env` para trocar entre OpenAI, Anthropic, Groq, Gemini e Ollama sem mudar nenhuma linha de código.

| `LLM_PROVIDER` | Provedor               | Custo              | Requer                    |
| -------------- | ---------------------- | ------------------ | ------------------------- |
| `openai`       | GPT-4o-mini            | API paga           | `OPENAI_API_KEY`          |
| `anthropic`    | Claude Haiku           | API paga           | `ANTHROPIC_API_KEY`       |
| `groq`         | Llama 3.1 8B           | Gratuito (limites) | `GROQ_API_KEY`            |
| `gemini`       | Gemini 2.0 Flash       | API paga           | `GEMINI_API_KEY`          |
| `ollama`       | LLaMA / Falcon (local) | Gratuito           | Ollama rodando localmente |

Para alta disponibilidade nos endpoints `/explain` e `/analysis`, configure
`LLM_FALLBACK_PROVIDERS` com uma lista separada por vírgulas. A API tenta
`LLM_PROVIDER` primeiro e, se a chamada ao modelo falhar, tenta cada fallback na
ordem configurada.

---

## Desenvolvimento Local

### Testes

```bash
pytest --cov=app --cov-report=term-missing
```

Os testes utilizam mocks para o provedor LLM e para o registro de modelo — não é necessário ter API keys. O teste de `/predict` usa o artefato `models/pcos_model.joblib` versionado.

| Arquivo                          | O que testa                                                     |
| -------------------------------- | --------------------------------------------------------------- |
| `tests/api/test_predict_api.py`  | Endpoints predict/explain/analysis, validação 422, erro 503/502 |
| `tests/api/test_analysis_api.py` | Endpoint analysis (predict + explain combinado)                 |
| `tests/unit/test_predictor.py`   | Lógica de predição, SHAP values, confiança                      |
| `tests/unit/test_explainer.py`   | Construção do prompt, parsing do JSON                           |
| `tests/unit/test_llm_factory.py` | Seleção de provider (openai, anthropic, groq, gemini, ollama)   |

### Linting

```bash
ruff check .
ruff format .
```

### Docker Local

```bash
# Build
docker build -t diagnostico-medico-api .

# Executar
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  diagnostico-medico-api

# Test
curl http://localhost:8000/health
```

### Makefile

Comandos convenientes:

```bash
make help              # Show all available commands
make lint              # Run linters
make test              # Run tests
make docker-build      # Build Docker image
make docker-run        # Run Docker locally
make terraform-init    # Initialize Terraform
make terraform-plan    # Plan infrastructure
make terraform-apply   # Deploy infrastructure
```

---

## CI/CD Pipeline

O pipeline `.github/workflows/pipeline.yml` roda automaticamente em todo push/PR:

### Stages Automáticos (todo push)

| Stage           | Trigger   | O que faz                                |
| --------------- | --------- | ---------------------------------------- |
| **Lint**        | todo push | Ruff: verifica estilo e erros            |
| **Test**        | após lint | pytest com relatório de cobertura        |
| **Build Image** | após test | Build da imagem Docker (local, sem push) |

### Stages Manuais (workflow_dispatch)

| Stage          | Trigger              | O que faz                          |
| -------------- | -------------------- | ---------------------------------- |
| **Push ECR**   | manual via GitHub UI | Build + Tag + Push para AWS ECR    |
| **Deploy ECS** | manual via GitHub UI | Update ECS service com nova imagem |

### Fluxo de Trabalho

**Desenvolvimento Normal:**

```bash
git push origin feature-branch
# ✅ Automático: lint + test + build
```

**Pronto para Deploy:**

1. GitHub Actions → CI/CD Pipeline → **Run workflow**
2. Branch: `main`
3. Action: `push` (ECR only) ou `full` (ECR + ECS)
4. **Run workflow**

A autenticação com AWS usa **OIDC** (sem secrets de longa duração). Configure `AWS_ROLE_TO_ASSUME` nos secrets do repositório.

Para detalhes completos sobre setup e cenários, veja a documentação em `.github/workflows/pipeline.yml`.

---

## Deployment (AWS Fargate)

### Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    AWS Account                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              VPC (10.0.0.0/16)               │   │
│  │                                              │   │
│  │  ┌────────────────────────────────────────┐ │   │
│  │  │     Public Subnets (x2)                │ │   │
│  │  │  ┌─────────────────────────────────┐  │ │   │
│  │  │  │  Application Load Balancer      │  │ │   │
│  │  │  │  (port 80/443)                  │  │ │   │
│  │  │  └─────────────────────────────────┘  │ │   │
│  │  │           │                           │ │   │
│  │  │  ┌────────┴─────────┐                 │ │   │
│  │  │  │   NAT Gateways   │                 │ │   │
│  │  │  └────────┬─────────┘                 │ │   │
│  │  └────────────────────────────────────────┘ │   │
│  │                    │                         │   │
│  │  ┌────────────────┴────────────────────┐   │   │
│  │  │   Private Subnets (x2)              │   │   │
│  │  │  ┌────────────────────────────┐    │   │   │
│  │  │  │  ECS Fargate Tasks (x2+)   │    │   │   │
│  │  │  │  ┌──────────────────────┐  │    │   │   │
│  │  │  │  │  FastAPI Container   │  │    │   │   │
│  │  │  │  │  (Port 8000)          │  │    │   │   │
│  │  │  │  │  - Auto Scaling       │  │    │   │   │
│  │  │  │  └──────────────────────┘  │    │   │   │
│  │  │  └────────────────────────────┘    │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  ECR Repository (Docker Images)              │   │
│  │  - Image Scanning enabled                    │   │
│  │  - Lifecycle policies                        │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  CloudWatch                                  │   │
│  │  - Log Group: /ecs/diagnostico-medico-api    │   │
│  │  - Metrics: CPU, Memory, Requests            │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Pré-requisitos

1. **AWS Account** com permissões para criar VPC, ECR, ECS, ALB, CloudWatch, IAM
2. **Local Tools**: Terraform >= 1.0, AWS CLI v2, Docker, Git
3. **AWS Credentials**: `aws configure` ou `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`

### Setup Terraform

```bash
# 1. Initialize Terraform
cd terraform
terraform init

# 2. Plan the Infrastructure
terraform plan -out=tfplan

# 3. Apply
terraform apply tfplan

# 4. Get Outputs
terraform output
```

Key outputs:

- `ecr_repository_url` — URL para fazer push de imagens
- `application_url` — URL pública da API
- `ecs_cluster_name`, `ecs_service_name` — Para deployments manuais

Configuração LLM no Terraform:

- `llm_provider` define o provider primário.
- `llm_fallback_providers` define fallbacks em ordem, separados por vírgula.
- Para cada provider com API key em `llm_provider` ou `llm_fallback_providers`,
  inclua o secret correspondente em `secrets_to_create` e preencha o valor no
  AWS Secrets Manager antes de subir a task ECS.

### Docker Image Management

**Build and Push Manually:**

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t diagnostico-medico-api:v1.0 .

# Tag for ECR
docker tag diagnostico-medico-api:v1.0 \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/diagnostico-medico-api:v1.0

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/diagnostico-medico-api:v1.0
```

**Test Image Locally:**

```bash
docker build -t diagnostico-medico-api:latest .
docker run -p 8000:8000 diagnostico-medico-api:latest
curl http://localhost:8000/health
```

### Manual Deployment (ECS)

```bash
# Update ECS service
aws ecs update-service \
  --cluster diagnostico-medico-api-cluster \
  --service diagnostico-medico-api-service \
  --force-new-deployment \
  --region us-east-1

# Wait for deployment
aws ecs wait services-stable \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service \
  --region us-east-1
```

### Auto Scaling

A service escala automaticamente baseada em três métricas:

1. **CPU Utilization**: Target 70%
2. **Memory Utilization**: Target 80%
3. **ALB Request Count**: Target 1000 requests/target/minute

Modificar em `terraform/autoscaling.tf`:

```bash
cd terraform
terraform apply
```

Scaling limits:

- **Dev**: 1-2 tasks
- **Prod**: 3-10 tasks

### Monitoramento e Logs

**View Logs:**

```bash
aws logs tail /ecs/diagnostico-medico-api --follow
```

**Monitor ECS Service:**

```bash
aws ecs describe-services \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service
```

**CloudWatch Metrics:**

- `ECS:ServiceCount` — Number of running tasks
- `ALB:RequestCount` — Total requests to API
- `ALB:TargetResponseTime` — Response time
- `ECS:CPUUtilization` — Container CPU usage
- `ECS:MemoryUtilization` — Container memory usage

### HTTPS/SSL Configuration

1. Get an SSL certificate from AWS Certificate Manager (ACM)
2. Uncomment the HTTPS listener in `terraform/alb.tf`
3. Add HTTP to HTTPS redirect
4. Apply terraform: `terraform apply`

### Rollback

```bash
aws ecs update-service \
  --cluster diagnostico-medico-api-cluster \
  --service diagnostico-medico-api-service \
  --task-definition diagnostico-medico-api:PREVIOUS_VERSION \
  --region us-east-1
```

### Cleanup

```bash
cd terraform
terraform destroy
```

**Warning**: This action cannot be undone.

### Troubleshooting

**Tasks not starting:**

```bash
aws ecs describe-task-definition --task-definition diagnostico-medico-api
aws ecs describe-services \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service \
  --query 'services[0].events'
```

**Image not found in ECR:**

```bash
aws ecr describe-images --repository-name diagnostico-medico-api --region us-east-1
```

**Application not responding:**

```bash
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:...
aws ec2 describe-security-groups --filters "Name=group-name,Values=diagnostico-medico-api*"
```

---

## Monitoramento

### CloudWatch (Infraestrutura)

AWS CloudWatch monitora métricas da infraestrutura:

- CPU, memória, disk usage dos containers
- Network I/O
- ECS task count e health

Acesse via AWS Console → CloudWatch → Logs/Metrics.

### PostHog (Eventos de Negócio)

PostHog captura eventos da aplicação:

**Setup:**

```env
POSTHOG_ENABLED=true
POSTHOG_API_KEY=seu_api_key
```

**Eventos Capturados:**

| Evento             | Properties                                               |
| ------------------ | -------------------------------------------------------- |
| `api_request`      | endpoint, method, status_code, duration_ms               |
| `model_prediction` | model_name, duration_ms, status, error                   |
| `llm_request`      | provider, model, duration_ms, tokens_used, status, error |
| `health_check`     | timestamp                                                |

**Criar Dashboards:**

1. PostHog → Insights → New Insight
2. Selecionar evento (ex: `api_request`)
3. Agrupar/filtrar conforme necessário

**Exemplos de Análises:**

| Análise                       | Evento             | Métrica                         |
| ----------------------------- | ------------------ | ------------------------------- |
| Taxa de sucesso de previsões  | `model_prediction` | Count (status=success)          |
| Performance média             | `api_request`      | Average duration_ms             |
| Distribuição de providers LLM | `llm_request`      | Count grouped by provider       |
| Erros por endpoint            | `api_request`      | Count filtered by status >= 400 |

### Integração CloudWatch + PostHog

| Métrica           | CloudWatch | PostHog |
| ----------------- | ---------- | ------- |
| CPU/Memória       | ✅         | —       |
| Network I/O       | ✅         | —       |
| HTTP Requests     | —          | ✅      |
| Response Time     | —          | ✅      |
| Error Rate        | —          | ✅      |
| Model Performance | —          | ✅      |
| LLM Usage         | —          | ✅      |

---

## FAQ / Troubleshooting

### Geral

**P: Como escolher entre os provedores LLM?**
A:

- **Groq** (recomendado): Rápido, gratuito com limites, ideal para produção
- **OpenAI**: Melhor qualidade, custo mais alto
- **Anthropic**: Ótima alternativa confiável, custo moderado
- **Gemini**: Bom custo-benefício
- **Ollama**: Desenvolvimento local, gratuito

Basta mudar `LLM_PROVIDER` no `.env`.

**P: Qual é o padrão se não configurar LLM_PROVIDER?**
A:

- **Em código/desenvolvimento local**: `openai` (mas requer `OPENAI_API_KEY`)
- **Em container Docker**: `groq` (requer `GROQ_API_KEY`)

Para evitar erros, sempre configure `LLM_PROVIDER` e a chave correspondente no `.env`.

**P: Qual é a diferença entre `/predict`, `/explain` e `/analysis`?**
A:

- **`/predict`**: Retorna apenas diagnóstico + contribuições de features
- **`/explain`**: Retorna apenas explicação clínica (requer resultado de `/predict`)
- **`/analysis`**: Retorna diagnóstico + explicação em uma única chamada (mais conveniente)

**P: Posso usar a API sem um provedor LLM?**
A: Sim. `/api/v1/predict` funciona independentemente. `/api/v1/explain` e `/api/v1/analysis` retornam 502 se nenhum provedor estiver configurado.

### Deployment

**P: A infraestrutura está cara?**
A: Dev (~$50/mês), Prod (~$130/mês). Use Fargate Spot para economizar 70%.

**P: Como escalar o serviço?**
A: Auto-scaling está ativado. Para ajustar limites, edite `terraform/autoscaling.tf` e rode `terraform apply`.

**P: Como fazer rollback?**
A: Use `aws ecs update-service` com a task definition anterior, ou redeploy via GitHub Actions.

### CI/CD

**P: Qual é a diferença entre push e deploy?**
A: `push` = build + upload para ECR. `deploy` = atualizar ECS service. `full` = ambos.

**P: O build falha sem infraestrutura?**
A: Não. Lint/test/build rodam sempre. Push/deploy falham gracefully se infra não existir.

**P: Como configurar múltiplos ambientes?**
A: Use branches diferentes (staging, main) com workflows separados ou reuse `terraform.*.tfvars`.

### Testes

**P: Como rodar testes sem API keys?**
A: Testes usam mocks para LLM e modelo. Só execute `pytest --cov=app`.

**P: Qual é a cobertura esperada?**
A: Alvo é 80%+ para rotas críticas. Verifique com `pytest --cov-report=html`.

### Monitoramento

**P: Os eventos do PostHog estão demorando a aparecer?**
A: Normal. PostHog tem latência de ingestão (~30s). Não afeta a API.

**P: Como criar alertas?**
A: PostHog não tem alertas nativo. Use CloudWatch para isso, ou exporte eventos para uma ferramenta de alerting.

---

## Próximas Leituras

- **mocks.md** — Payloads prontos para testar endpoints
- **.github/workflows/pipeline.yml** — Configuração detalhada do CI/CD
- **terraform/\*.tf** — Infrastructure as Code (AWS Fargate)
- **pyproject.toml** — Dependências e configuração do projeto
