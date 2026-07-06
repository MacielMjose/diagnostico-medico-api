# Payloads mock para testar a API

Base URL local: `http://localhost:8000` — rotas de negócio sob `/api/v1`.
Suba a API com `uvicorn app.main:app --reload`.

> As probabilidades abaixo foram geradas com o artefato `models/pcos_model.joblib`
> versionado no repositório. Pequenas variações podem ocorrer se o modelo for
> retreinado.

---

## `POST /api/v1/predict/`

20 campos clínicos. Binários: `0` = Não, `1` = Sim. `cycle`: `2` = Regular, `4` = Irregular.

### Caso A — perfil de alto risco (esperado: positivo)

```json
{
  "follicle_no_r": 15,
  "follicle_no_l": 14,
  "skin_darkening": 1,
  "hair_growth": 1,
  "weight_gain": 1,
  "cycle": 4,
  "fast_food": 1,
  "pimples": 1,
  "amh": 8.2,
  "bmi": 31.5,
  "cycle_length": 3,
  "hair_loss": 1,
  "age": 27,
  "hip": 42,
  "avg_f_size_l": 18.0,
  "marriage_status": 4.0,
  "endometrium": 9.5,
  "avg_f_size_r": 19.0,
  "pulse_rate": 76,
  "hb": 11.0
}
```

Saída esperada: `diagnosis: 1`, `probability ≈ 0.9999`, `confidence: "Alta"`.

```bash
curl -s -X POST http://localhost:8000/api/v1/predict/ \
  -H "Content-Type: application/json" \
  -d @- <<'JSON' | jq
{"follicle_no_r":15,"follicle_no_l":14,"skin_darkening":1,"hair_growth":1,"weight_gain":1,"cycle":4,"fast_food":1,"pimples":1,"amh":8.2,"bmi":31.5,"cycle_length":3,"hair_loss":1,"age":27,"hip":42,"avg_f_size_l":18.0,"marriage_status":4.0,"endometrium":9.5,"avg_f_size_r":19.0,"pulse_rate":76,"hb":11.0}
JSON
```

### Caso B — perfil de baixo risco (esperado: negativo)

```json
{
  "follicle_no_r": 5,
  "follicle_no_l": 4,
  "skin_darkening": 0,
  "hair_growth": 0,
  "weight_gain": 0,
  "cycle": 2,
  "fast_food": 0,
  "pimples": 0,
  "amh": 2.1,
  "bmi": 21.0,
  "cycle_length": 5,
  "hair_loss": 0,
  "age": 32,
  "hip": 36,
  "avg_f_size_l": 14.0,
  "marriage_status": 6.0,
  "endometrium": 8.0,
  "avg_f_size_r": 13.5,
  "pulse_rate": 72,
  "hb": 13.2
}
```

Saída esperada: `diagnosis: 0`, `probability ≈ 0.0181`, `confidence: "Alta"`.

```bash
curl -s -X POST http://localhost:8000/api/v1/predict/ \
  -H "Content-Type: application/json" \
  -d @- <<'JSON' | jq
{"follicle_no_r":5,"follicle_no_l":4,"skin_darkening":0,"hair_growth":0,"weight_gain":0,"cycle":2,"fast_food":0,"pimples":0,"amh":2.1,"bmi":21.0,"cycle_length":5,"hair_loss":0,"age":32,"hip":36,"avg_f_size_l":14.0,"marriage_status":6.0,"endometrium":8.0,"avg_f_size_r":13.5,"pulse_rate":72,"hb":13.2}
JSON
```

### Caso C — perfil intermediário (esperado: positivo, sintomas mistos)

```json
{
  "follicle_no_r": 9,
  "follicle_no_l": 8,
  "skin_darkening": 0,
  "hair_growth": 1,
  "weight_gain": 1,
  "cycle": 4,
  "fast_food": 1,
  "pimples": 0,
  "amh": 4.8,
  "bmi": 26.0,
  "cycle_length": 4,
  "hair_loss": 0,
  "age": 29,
  "hip": 39,
  "avg_f_size_l": 16.0,
  "marriage_status": 3.0,
  "endometrium": 8.5,
  "avg_f_size_r": 16.5,
  "pulse_rate": 74,
  "hb": 12.0
}
```

Saída esperada: `diagnosis: 1`, `probability ≈ 0.9545`, `confidence: "Alta"`.

```bash
curl -s -X POST http://localhost:8000/api/v1/predict/ \
  -H "Content-Type: application/json" \
  -d @- <<'JSON' | jq
{"follicle_no_r":9,"follicle_no_l":8,"skin_darkening":0,"hair_growth":1,"weight_gain":1,"cycle":4,"fast_food":1,"pimples":0,"amh":4.8,"bmi":26.0,"cycle_length":4,"hair_loss":0,"age":29,"hip":39,"avg_f_size_l":16.0,"marriage_status":3.0,"endometrium":8.5,"avg_f_size_r":16.5,"pulse_rate":74,"hb":12.0}
JSON
```

---

## `POST /api/v1/explain/`

Recebe o resultado da predição (`features` + `diagnosis` + `probability`) e
gera a interpretação clínica via LLM. **Requer um provedor LLM configurado**
(`LLM_PROVIDER` + chave no `.env`); sem isso, retorna `503`.

> **Validação de features:** é obrigatório enviar **pelo menos 15 das 20**
> features clínicas conhecidas (nomes originais das colunas). Menos que isso, ou
> nomes desconhecidos, retorna `400` com mensagem explicativa. Nomes são
> tolerantes a maiúsculas/minúsculas e espaços nas bordas.

Os exemplos abaixo reaproveitam os fatores de cada caso de predição.

### Explicação do Caso A (16 features — perfil de alto risco)

```json
{
  "features": {
    "Follicle No. (R)": 15,
    "Follicle No. (L)": 14,
    "Skin darkening (Y/N)": 1,
    "hair growth(Y/N)": 1,
    "Weight gain(Y/N)": 1,
    "Cycle(R/I)": 4,
    "Fast food (Y/N)": 1,
    "Pimples(Y/N)": 1,
    "AMH(ng/mL)": 8.2,
    "BMI": 31.5,
    "Cycle length(days)": 3,
    "Hair loss(Y/N)": 1,
    "Age (yrs)": 27,
    "Hip(inch)": 42,
    "Endometrium (mm)": 9.5,
    "Avg. F size (R) (mm)": 19.0
  },
  "diagnosis": 1,
  "probability": 0.9999
}
```

```bash
curl -s -X POST http://localhost:8000/api/v1/explain/ \
  -H "Content-Type: application/json" \
  -d '{"features":{"Follicle No. (R)":15,"Follicle No. (L)":14,"Skin darkening (Y/N)":1,"hair growth(Y/N)":1,"Weight gain(Y/N)":1,"Cycle(R/I)":4,"Fast food (Y/N)":1,"Pimples(Y/N)":1,"AMH(ng/mL)":8.2,"BMI":31.5,"Cycle length(days)":3,"Hair loss(Y/N)":1,"Age (yrs)":27,"Hip(inch)":42,"Endometrium (mm)":9.5,"Avg. F size (R) (mm)":19.0},"diagnosis":1,"probability":0.9999}' | jq
```

### Explicação do Caso B (15 features — perfil de baixo risco)

```json
{
  "features": {
    "Follicle No. (R)": 5,
    "Follicle No. (L)": 4,
    "Skin darkening (Y/N)": 0,
    "hair growth(Y/N)": 0,
    "Weight gain(Y/N)": 0,
    "Cycle(R/I)": 2,
    "Fast food (Y/N)": 0,
    "Pimples(Y/N)": 0,
    "AMH(ng/mL)": 2.1,
    "BMI": 21.0,
    "Cycle length(days)": 5,
    "Hair loss(Y/N)": 0,
    "Age (yrs)": 32,
    "Hip(inch)": 36,
    "Endometrium (mm)": 8.0
  },
  "diagnosis": 0,
  "probability": 0.0181
}
```

Resposta esperada (formato): `{ "explanation": "...", "risk_factors": [...], "insights": [...] }`.

### Erro — poucas features (esperado: `400`)

```json
{
  "features": {
    "AMH(ng/mL)": 8.2,
    "BMI": 31.5
  },
  "diagnosis": 1,
  "probability": 0.9999
}
```

Resposta esperada:

```json
{
  "error": "São necessárias pelo menos 15 das 20 features para gerar uma explicação fundamentada. Recebidas: 2. Envie as mesmas features usadas na predição (/predict) para que a interpretação reflita os fatores que realmente pesaram no resultado."
}
```

---

## `POST /api/v1/optimize/`

Otimização genética de hiperparâmetros (não depende do modelo nem de LLM).

```json
{
  "population_size": 20,
  "generations": 5,
  "mutation_rate": 0.1,
  "crossover_rate": 0.8
}
```

```bash
curl -s -X POST http://localhost:8000/api/v1/optimize/ \
  -H "Content-Type: application/json" \
  -d '{"population_size":20,"generations":5,"mutation_rate":0.1,"crossover_rate":0.8}' | jq
```

---

## `GET /health`

```bash
curl -s http://localhost:8000/health | jq
# {"status":"ok","version":"1.0.0"}
```
