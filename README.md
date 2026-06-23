# Diagnóstico Médico API — SOP/PCOS

API de suporte diagnóstico para **Síndrome dos Ovários Policísticos (SOP/PCOS)** desenvolvida como parte do Tech Challenge — Fase 2 do programa IADT.

Combina um modelo de **Regressão Logística** treinado em dados clínicos com **explicabilidade SHAP** e **interpretação em linguagem natural via LLM**, permitindo que médicos recebam não apenas um resultado numérico, mas uma análise clínica contextualizada.

---

## Arquitetura

```
POST /api/v1/predict              POST /api/v1/explain
       │                                  │
       ▼                                  ▼
 PCOSInput (20 campos clínicos)    features + diagnóstico + probabilidade
       │                                  │
       ▼                                  ▼
 predictor.py                      llm_explainer.py
   Regressão Logística + SHAP        Prompt Engineering + LLM
   (probabilidade, top 5 fatores)    (interpretação clínica em JSON)
                                           │
                              ┌────────────┼─────────────┐
                          OpenAI      Anthropic    Ollama (local)    Gemini
                          GPT-4o-mini Claude Haiku LLaMA / Falcon    2.0 Flash
```

O fluxo é em duas chamadas: o cliente obtém a predição em `/api/v1/predict` e,
opcionalmente, envia o resultado para `/api/v1/explain` para receber a
interpretação clínica gerada por LLM.

### Estrutura do projeto

```
diagnostico-medico-api/
├── src/app/
│   ├── main.py                     # FastAPI — cria a app e registra rotas
│   ├── core/
│   │   ├── config.py               # Configurações via variáveis de ambiente
│   │   └── dependencies.py         # Injeção de dependências (predictor, LLM)
│   ├── api/v1/                     # Rotas: predict, explain, optimize, ultrasound
│   ├── domain/                     # Modelos de domínio + mapeamento de features
│   ├── services/
│   │   ├── predictor.py            # Carregamento do modelo + predição + SHAP
│   │   └── llm_explainer.py        # Prompt engineering + orquestração LLM
│   └── infrastructure/
│       ├── model_registry.py       # Carregamento do artefato joblib
│       └── llm/
│           ├── base.py             # Protocolo abstrato LLMProvider
│           ├── openai_provider.py
│           ├── anthropic_provider.py
│           ├── ollama_provider.py
│           ├── gemini_provider.py
│           └── factory.py          # Cria provider conforme LLM_PROVIDER
├── scripts/
│   └── train_model.py              # Treina e salva o artefato do modelo
├── models/
│   └── pcos_model.joblib           # Artefato gerado pelo script (não versionado)
├── tests/
│   ├── api/test_predict_api.py        # Endpoints predict / explain / optimize
│   └── unit/                          # predictor, explainer, factory LLM, GA
├── pcos_logistic_regression_top20.ipynb   # Notebook de exploração / referência
└── pyproject.toml
```

---

## Modelo de ML

| Atributo | Valor |
|---|---|
| Dataset | [PCOS Without Infertility — Kaggle](https://www.kaggle.com/datasets/prasoonkottarathil/polycystic-ovary-syndrome-pcos) |
| Algoritmo | Regressão Logística (`class_weight='balanced'`) |
| Features | Top 20 por correlação absoluta com o target |
| Explicabilidade | SHAP `LinearExplainer` |
| AUC-ROC (test set) | ~0.95 |
| Recall (classe positiva) | ~0.92 |

As 20 features selecionadas incluem: número de folículos, AMH, padrão do ciclo menstrual, IMC, sintomas hiperandrogênicos (hirsutismo, acantose, acne) e marcadores laboratoriais.

---

## Configuração

### Pré-requisitos

- Python 3.12+
- Credenciais Kaggle (`~/.kaggle/kaggle.json` ou variáveis `KAGGLE_USERNAME` / `KAGGLE_KEY`)
- Chave de API do provedor LLM escolhido

### Instalação

```bash
# Dependências da API
pip install -e ".[dev]"

# Dependências de treinamento (kaggle, openpyxl)
pip install -e ".[training]"
```

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Provedor LLM: openai | anthropic | ollama | gemini
LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# Google Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash

# Ollama (modelos locais — não requer chave)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Caminho para o artefato do modelo
MODEL_PATH=models/pcos_model.joblib
```

---

## Treinamento do modelo

Execute uma vez antes de subir a API:

```bash
python scripts/train_model.py
```

O script baixa o dataset do Kaggle, treina a Regressão Logística com as Top 20 features e salva o artefato em `models/pcos_model.joblib`.

---

## Executando a API

```bash
uvicorn app.main:app --reload
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

---

## Endpoints

Todas as rotas de negócio ficam sob o prefixo `/api/v1`.

### `GET /health`

```json
{"status": "ok", "version": "1.0.0"}
```

### `POST /api/v1/predict/`

Recebe os 20 campos clínicos e retorna a predição com explicabilidade SHAP.

**Request body:**

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
    { "feature": "num__Follicle No. (R)", "contribution": 1.3123, "direction": "positiva" },
    { "feature": "num__Cycle(R/I)",       "contribution": 0.6091, "direction": "positiva" },
    { "feature": "bin__hair growth(Y/N)", "contribution": 0.5850, "direction": "positiva" },
    { "feature": "bin__Skin darkening (Y/N)", "contribution": 0.5542, "direction": "positiva" },
    { "feature": "num__Follicle No. (L)", "contribution": 0.4782, "direction": "positiva" }
  ]
}
```

Retorna `503` se o artefato do modelo não estiver disponível.

### `POST /api/v1/explain/`

Recebe o resultado da predição e gera a interpretação clínica via LLM.

**Request body:**

```json
{
  "features": { "BMI": 27.0, "AMH(ng/mL)": 7.5, "Follicle No. (R)": 12 },
  "diagnosis": 1,
  "probability": 0.87
}
```

**Response:**

```json
{
  "explanation": "O modelo de triagem indica resultado POSITIVO para SOP com probabilidade de 87%, sustentado principalmente pelo elevado número de folículos ovarianos e pelo padrão de ciclo irregular — achados consistentes com os critérios de Rotterdam...",
  "risk_factors": ["obesidade", "resistência insulínica", "hirsutismo"],
  "insights": ["solicitar perfil hormonal completo", "avaliar glicemia de jejum e insulina basal"]
}
```

Retorna `502` se o provedor LLM falhar ou devolver formato inesperado.

> Há ainda as rotas `POST /api/v1/optimize/` (otimização genética de
> hiperparâmetros) e `POST /api/v1/ultrasound/predict` (upload de imagem).

---

## Integração LLM

A integração é **agnóstica ao provedor**: basta alterar `LLM_PROVIDER` no `.env` para trocar entre OpenAI, Anthropic, Ollama e Gemini sem mudar nenhuma linha de código. A seleção é feita por `infrastructure/llm/factory.py`, que instancia o provider correspondente; todos implementam a interface `LLMProvider`.

| `LLM_PROVIDER` | Provedor | Custo | Requer |
|---|---|---|---|
| `openai` | GPT-4o-mini | API paga | `OPENAI_API_KEY` |
| `anthropic` | Claude Haiku | API paga | `ANTHROPIC_API_KEY` |
| `gemini` | Gemini 2.0 Flash | API paga | `GEMINI_API_KEY` |
| `ollama` | LLaMA / Falcon (local) | Gratuito | Ollama rodando localmente |

### Prompt Engineering

O `llm_explainer.py` aplica duas camadas de prompt:

- **System prompt** — define uma persona de especialista em endocrinologia reprodutiva com regras rígidas: terminologia clínica precisa, resultado tratado como probabilidade (nunca certeza) e ressalva de que o modelo é ferramenta de triagem. Exige resposta **exclusivamente em JSON** com os campos `explanation`, `risk_factors` e `insights`.
- **User prompt** — inclui o diagnóstico, a probabilidade estimada e os fatores/dados fornecidos no request.

**Tratamento de falha:** se o provedor LLM estiver indisponível (sem chave, timeout) ou devolver um JSON inválido, o endpoint `/api/v1/explain` retorna **HTTP 502**. A predição (`/api/v1/predict`) é independente e continua funcionando mesmo sem LLM configurado.

---

## Testes

```bash
pytest --cov=app --cov-report=term-missing
```

Os testes utilizam mocks para o provedor LLM e para o registro de modelo — não é necessário ter API keys para rodar a suíte. O teste de `/predict` usa o artefato `models/pcos_model.joblib` versionado no repositório.

| Arquivo | O que testa |
|---|---|
| `tests/api/test_predict_api.py` | Endpoints predict/explain/optimize, validação 422, erro 503 (sem modelo) e 502 (falha LLM) |
| `tests/unit/test_predictor.py` | Lógica de confiança, estrutura do resultado, erro sem modelo |
| `tests/unit/test_explainer.py` | Construção do prompt, parsing do JSON e erro em caso de falha |
| `tests/unit/test_llm_factory.py` | Seleção de provedor e erro para provedor inválido |
| `tests/unit/test_genetic_operators.py` | Operadores do otimizador genético |

---

## Docker

```bash
# Build local
docker build -t diagnostico-medico-api .

# Executar (com modelo montado e variáveis de ambiente)
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  diagnostico-medico-api
```

---

## CI/CD

O pipeline `.github/workflows/pipeline.yml` roda automaticamente em todo push:

| Stage | Trigger | O que faz |
|---|---|---|
| **Lint** | todo push | Ruff: verifica estilo e erros |
| **Test** | após lint | pytest com relatório de cobertura |
| **Build Image** | após test | Build e push da imagem para AWS ECR |
| **Deploy** | push na `main` | Atualiza serviço no AWS ECS Fargate |

A autenticação com AWS usa OIDC (sem secrets de longa duração). Configure `AWS_ROLE_TO_ASSUME` nos secrets do repositório.

---

## Próximos passos (Módulo 3)

- Integração com dados textuais (anamnese livre) para enriquecer o contexto do LLM
- Avaliação sistemática da qualidade das interpretações geradas (BLEU, relevância clínica, revisão especialista)
- Endpoint de feedback médico para logging das interpretações e refinamento de prompts
