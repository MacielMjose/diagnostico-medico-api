"""Mapeamentos de features clínicas usados na predição e na interpretação."""

from app.domain.exceptions import InvalidFeaturesError

# ... FEATURE_COLUMN_MAP ...

# ... FEATURE_LABELS ...

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
    def validate_no_negative(
        features: dict, raise_exc: type[Exception] = ValueError
    ) -> None:
        for key, val in features.items():
            if val < 0:
                raise raise_exc(
                    f"Feature '{key}' recebeu valor negativo ({val}). "
                    "Todas as features devem ser não-negativas."
                )

    @staticmethod
    def validate_binary_only(
        features: dict, raise_exc: type[Exception] = ValueError
    ) -> None:
        for key, val in features.items():
            if key in FeatureValidator.BINARY_FEATURES and val not in (0, 1):
                raise raise_exc(
                    f"Feature binária '{key}' deve ser 0 ou 1, recebeu {val}."
                )


# --- Validação de features do endpoint /explain -----------------------------

# Total de features clínicas conhecidas pelo modelo.
TOTAL_FEATURES = len(FEATURE_COLUMN_MAP)

# Mínimo de features exigidas para uma explicação clinicamente fundamentada.
MIN_EXPLAIN_FEATURES = 10

# Lookup normalizado (sem espaços nas bordas, minúsculo) → nome canônico.
_NORMALIZED_FEATURES: dict[str, str] = {
    name.strip().lower(): name for name in FEATURE_COLUMN_MAP.values()
}


def validate_explain_features(features: dict) -> None:
    """Garante que o /explain recebeu features válidas e em quantidade suficiente."""
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