"""Mapeamentos de features clínicas usados na predição e na interpretação."""

from app.domain.exceptions import InvalidFeaturesError

# Nomes de campos Python limpos → nomes originais das colunas do dataset
# (preservando o espaçamento original, exigido pelo ColumnTransformer do modelo).
FEATURE_COLUMN_MAP: dict[str, str] = {
    "follicle_no_r": "Follicle No. (R)",
    "follicle_no_l": "Follicle No. (L)",
    "skin_darkening": "Skin darkening (Y/N)",
    "hair_growth": "hair growth(Y/N)",
    "weight_gain": "Weight gain(Y/N)",
    "cycle": "Cycle(R/I)",
    "fast_food": "Fast food (Y/N)",
    "pimples": "Pimples(Y/N)",
    "amh": "AMH(ng/mL)",
    "bmi": "BMI",
    "cycle_length": "Cycle length(days)",
    "hair_loss": "Hair loss(Y/N)",
    "age": " Age (yrs)",
    "hip": "Hip(inch)",
    "avg_f_size_l": "Avg. F size (L) (mm)",
    "marriage_status": "Marraige Status (Yrs)",
    "endometrium": "Endometrium (mm)",
    "avg_f_size_r": "Avg. F size (R) (mm)",
    "pulse_rate": "Pulse rate(bpm) ",
    "hb": "Hb(g/dl)",
}

# Nomes internos (com prefixo do ColumnTransformer) → rótulo legível em PT-BR.
FEATURE_LABELS: dict[str, str] = {
    "num__Follicle No. (R)": "Número de folículos (ovário direito)",
    "num__Follicle No. (L)": "Número de folículos (ovário esquerdo)",
    "num__Cycle(R/I)": "Padrão do ciclo menstrual",
    "num__AMH(ng/mL)": "Hormônio Antimülleriano (AMH)",
    "num__BMI": "IMC",
    "num__Cycle length(days)": "Duração do ciclo",
    "num__ Age (yrs)": "Idade",
    "num__Hip(inch)": "Circunferência do quadril",
    "num__Avg. F size (L) (mm)": "Tamanho médio dos folículos (esq.)",
    "num__Marraige Status (Yrs)": "Anos de casamento",
    "num__Endometrium (mm)": "Espessura do endométrio",
    "num__Avg. F size (R) (mm)": "Tamanho médio dos folículos (dir.)",
    "num__Pulse rate(bpm) ": "Frequência cardíaca",
    "num__Hb(g/dl)": "Hemoglobina",
    "bin__Skin darkening (Y/N)": "Acantose nigricans",
    "bin__hair growth(Y/N)": "Hirsutismo",
    "bin__Weight gain(Y/N)": "Ganho de peso",
    "bin__Fast food (Y/N)": "Consumo de fast food",
    "bin__Pimples(Y/N)": "Acne",
    "bin__Hair loss(Y/N)": "Alopecia androgenética",
}


def readable_feature(name: str) -> str:
    return FEATURE_LABELS.get(name, name)


# --- Validação de features do endpoint /explain -----------------------------

# Total de features clínicas conhecidas pelo modelo.
TOTAL_FEATURES = len(FEATURE_COLUMN_MAP)

# Mínimo de features exigidas para uma explicação clinicamente fundamentada.
# Enviar menos empobrece a interpretação do LLM (ver /explain).
MIN_EXPLAIN_FEATURES = 10

# Lookup normalizado (sem espaços nas bordas, minúsculo) → nome canônico,
# para tolerar pequenas variações de digitação nos nomes das colunas.
_NORMALIZED_FEATURES: dict[str, str] = {
    name.strip().lower(): name for name in FEATURE_COLUMN_MAP.values()
}


def validate_explain_features(features: dict) -> None:
    """Garante que o /explain recebeu features válidas e em quantidade suficiente.

    Levanta ``InvalidFeaturesError`` (→ HTTP 400) com mensagem explicativa se
    houver nomes desconhecidos ou se menos de ``MIN_EXPLAIN_FEATURES`` features
    reconhecidas forem enviadas.
    """
    unknown = [k for k in features if k.strip().lower() not in _NORMALIZED_FEATURES]
    if unknown:
        raise InvalidFeaturesError(
            "Feature(s) não reconhecida(s): "
            f"{', '.join(repr(u) for u in unknown)}. "
            f"Use os nomes das {TOTAL_FEATURES} colunas clínicas conhecidas "
            f"(ex.: 'AMH(ng/mL)', 'BMI', 'Follicle No. (R)')."
        )

    recognized = {_NORMALIZED_FEATURES[k.strip().lower()] for k in features}
    if len(recognized) < MIN_EXPLAIN_FEATURES:
        raise InvalidFeaturesError(
            f"São necessárias pelo menos {MIN_EXPLAIN_FEATURES} das "
            f"{TOTAL_FEATURES} features para gerar uma explicação fundamentada. "
            f"Recebidas: {len(recognized)}. Envie as mesmas features usadas na "
            "predição (/predict) para que a interpretação reflita os fatores "
            "que realmente pesaram no resultado."
        )
