# PCOS Diagnosis API

API para diagnóstico de Síndrome do Ovário Policístico (SOP) usando Machine Learning, com otimização por Algoritmos Genéticos e interpretação via LLM.

## Stack

- **API**: FastAPI + Uvicorn
- **ML**: scikit-learn, XGBoost
- **Otimização**: Algoritmo Genético personalizado
- **LLM**: OpenAI GPT-4 (via httpx)
- **Monitoramento**: Prometheus, structlog
- **Infra**: Docker, Terraform (AWS ECS Fargate)
- **CI/CD**: GitHub Actions

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/predict/` | Predição com todas as features |
| `POST` | `/api/v1/predict/top20` | Predição com top 20 features |
| `POST` | `/api/v1/ultrasound/predict` | Classificação de imagem de ultrassom |
| `POST` | `/api/v1/optimize/` | Otimização de hiperparâmetros via AG |
| `POST` | `/api/v1/explain/` | Explicação do diagnóstico via LLM |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

## Estrutura

```
src/
├── app/
│   ├── api/v1/          # Rotas FastAPI
│   │   ├── predict/     # Predição de diagnóstico
│   │   ├── ultrasound/  # Classificação de imagem
│   │   ├── optimize/    # Algoritmo genético
│   │   └── explain/     # Explicação via LLM
│   ├── core/            # Config, dependências, logging
│   ├── domain/          # Modelos, enums, exceções
│   ├── infrastructure/  # ModelRegistry, LLMClient
│   ├── services/        # Predictor, GeneticOptimizer, LLMExplainer
│   └── monitoring/      # Métricas Prometheus, middleware
```

## Setup rápido

```bash
pip install -e ".[dev]"

# Rodar a API
uvicorn app.main:app --reload --port 8000

# Testar
pytest --cov=app
```

## Testes

99 testes, 95% de cobertura. Três camadas:

- **unit/** — testa funções e classes isoladamente (mocks)
- **api/** — testa os endpoints HTTP com cliente de teste
- **integration/** — testa fluxos completos

```bash
pytest                           # rodar todos
pytest tests/unit/               # só unitários
pytest tests/api/                # só API
pytest --cov=app                 # com cobertura
pytest -v                        # verbose (nomes dos testes)
```

## Docker

```bash
docker build -t diagnostico-medico-api .
docker run -p 8000:8000 diagnostico-medico-api
```

## Deploy (AWS ECS Fargate)

Terraform em `terraform/` provisiona VPC, cluster ECS, ALB, auto-scaling. CI/CD em `.github/workflows/pipeline.yml` faz lint → test → build → push → deploy.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Variáveis de ambiente

| Variável | Default | Descrição |
|---|---|---|
| `MODEL_PATH` | `./models` | Caminho dos modelos treinados |
| `LLM_API_KEY` | `""` | Chave da API OpenAI |
| `LLM_MODEL` | `gpt-4` | Modelo LLM |
| `LOG_LEVEL` | `INFO` | Nível de logging |
| `MAX_IMAGE_SIZE_MB` | `10` | Tamanho máximo de imagem (MB) |
