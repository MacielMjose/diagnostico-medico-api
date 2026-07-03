"""Mapeamentos de features clínicas usados na predição e na interpretação."""

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


class FeatureValidator:
    """Validações reutilizáveis de features entre schema HTTP e serviços."""

    BINARY_FEATURES = {
        "skin_darkening",
        "hair_growth",
        "weight_gain",
        "fast_food",
        "pimples",
        "hair_loss",
    }

    @staticmethod
    def validate_no_negative(features: dict, raise_exc: type[Exception] = ValueError) -> None:
        for key, val in features.items():
            if val < 0:
                raise raise_exc(
                    f"Feature '{key}' recebeu valor negativo ({val}). "
                    "Todas as features devem ser não-negativas."
                )

    @staticmethod
    def validate_binary_only(features: dict, raise_exc: type[Exception] = ValueError) -> None:
        for key, val in features.items():
            if key in FeatureValidator.BINARY_FEATURES and val not in (0, 1):
                raise raise_exc(
                    f"Feature binária '{key}' deve ser 0 ou 1, recebeu {val}."
                )
