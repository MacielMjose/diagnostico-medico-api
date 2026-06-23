# Diagnóstico Médico API — SOP/PCOS

API de suporte diagnóstico para **Síndrome dos Ovários Policísticos (SOP/PCOS)** desenvolvida como parte do Tech Challenge — Fase 2 do programa IADT.

Combina um modelo de **Regressão Logística** treinado em dados clínicos com **explicabilidade SHAP** e **interpretação em linguagem natural via LLM**, permitindo que médicos recebam não apenas um resultado numérico, mas uma análise clínica contextualizada.

---

## Arquitetura

```
POST /diagnose
       │
       ▼
 PatientData (20 campos clínicos)
       │
       ├─► pcos_classifier.py   →  Regressão Logística + SHAP
       │       (scikit-learn)         (probabilidade, top 5 fatores)
       │
       └─► interpreter.py       →  Prompt Engineering + LLM
               (langauge model)        (interpretação clínica em PT-BR)
                     │
             ┌───────┴────────┐
         OpenAI          Anthropic       Ollama (local)
         GPT-4o-mini     Claude Haiku    LLaMA / Falcon
```

### Estrutura do projeto

```
diagnostico-medico-api/
├── src/minha_api/
│   ├── config.py                   # Configurações via variáveis de ambiente
│   ├── schemas.py                  # Modelos Pydantic (request / response)
│   ├── main.py                     # FastAPI — rotas
│   ├── models/
│   │   └── pcos_classifier.py      # Carregamento do modelo + predição + SHAP
│   └── services/
│       ├── interpreter.py          # Prompt engineering + orquestração LLM
│       └── llm/
│           ├── base.py             # Protocolo abstrato LLMProvider
│           ├── openai_provider.py
│           ├── anthropic_provider.py
│           ├── ollama_provider.py
│           └── factory.py          # Cria provider conforme LLM_PROVIDER
├── scripts/
│   └── train_model.py              # Treina e salva o artefato do modelo
├── models/
│   └── pcos_model.joblib           # Artefato gerado pelo script (não versionado)
├── tests/
│   ├── test_main.py
│   ├── test_classifier.py
│   └── test_interpreter.py
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

- Python 3.11+
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
# Provedor LLM: openai | anthropic | ollama
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
uvicorn minha_api.main:app --reload
```

A documentação interativa fica disponível em `http://localhost:8000/swagger`.

---

## Endpoints

### `GET /health`

```json
{"status": "healthy"}
```

### `POST /diagnose`

Recebe dados clínicos de uma paciente e retorna diagnóstico + interpretação LLM.

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
  "diagnosis": true,
  "probability": 0.87,
  "confidence": "Alta",
  "top_contributing_features": [
    { "feature": "num__Follicle No. (R)", "contribution": 1.3123, "direction": "positiva" },
    { "feature": "num__Cycle(R/I)",       "contribution": 0.6091, "direction": "positiva" },
    { "feature": "bin__hair growth(Y/N)", "contribution": 0.5850, "direction": "positiva" },
    { "feature": "bin__Skin darkening (Y/N)", "contribution": 0.5542, "direction": "positiva" },
    { "feature": "num__Follicle No. (L)", "contribution": 0.4782, "direction": "positiva" }
  ],
  "interpretation": "O modelo de triagem indica resultado POSITIVO para SOP com probabilidade de 87%, sustentado principalmente pelo elevado número de folículos ovarianos bilateralmente (12 à direita e 10 à esquerda) e pelo padrão de ciclo irregular — achados consistentes com os critérios de Rotterdam...",
  "disclaimer": "Este resultado é apenas uma ferramenta de apoio diagnóstico e não substitui avaliação médica especializada."
}
```

---

## Integração LLM

A integração é **agnóstica ao provedor**: basta alterar `LLM_PROVIDER` no `.env` para trocar entre OpenAI, Anthropic e Ollama sem mudar nenhuma linha de código.

| `LLM_PROVIDER` | Provedor | Custo | Requer |
|---|---|---|---|
| `openai` | GPT-4o-mini | API paga | `OPENAI_API_KEY` |
| `anthropic` | Claude Haiku | API paga | `ANTHROPIC_API_KEY` |
| `gemini` | Gemini 2.0 Flash | API paga | `GEMINI_API_KEY` |
| `ollama` | LLaMA / Falcon (local) | Gratuito | Ollama rodando localmente |

### Prompt Engineering

O `interpreter.py` aplica duas camadas de prompt:

- **System prompt** — define uma persona de especialista em endocrinologia reprodutiva com regras rígidas: estrutura em 3 parágrafos, máximo de 250 palavras, terminologia clínica precisa, resultado tratado como probabilidade (nunca certeza).
- **User prompt** — inclui resultado do modelo, top 5 fatores com contribuição SHAP e direção (↑ favorece SOP / ↓ reduz probabilidade), e resumo clínico completo da paciente.

**Degradação graciosa:** se o LLM estiver indisponível (sem chave, timeout, etc.), o endpoint ainda responde com o diagnóstico numérico e uma mensagem de fallback — a API nunca retorna erro por causa do LLM.

---

## Testes

```bash
pytest --cov=minha_api --cov-report=term-missing
```

Os testes utilizam mocks para o modelo e para o provedor LLM — não é necessário ter o artefato treinado nem API keys para rodar a suíte.

| Arquivo | O que testa |
|---|---|
| `test_main.py` | Endpoints FastAPI, validação de payload, erros 422/503 |
| `test_classifier.py` | Lógica de confiança, estrutura do resultado, erro sem modelo |
| `test_interpreter.py` | Construção dos prompts, chamada ao LLM, fallback em caso de falha |

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
