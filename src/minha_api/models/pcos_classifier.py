import logging
import pathlib
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from minha_api.config import settings
from minha_api.schemas import FeatureContribution

logger = logging.getLogger(__name__)

_CONFIDENCE_HIGH = 0.80
_CONFIDENCE_MED = 0.60


def _confidence_label(probability: float) -> str:
    dist_from_boundary = abs(probability - 0.5)
    if dist_from_boundary >= (_CONFIDENCE_HIGH - 0.5):
        return "Alta"
    if dist_from_boundary >= (_CONFIDENCE_MED - 0.5):
        return "Média"
    return "Baixa"


@lru_cache(maxsize=1)
def _load_artifacts() -> dict:
    path = pathlib.Path(settings.model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em '{path}'. "
            "Execute 'python scripts/train_model.py' para treinar e salvar o modelo."
        )
    return joblib.load(path)


def predict(patient_row: dict) -> dict:
    artifacts = _load_artifacts()
    pipeline = artifacts["pipeline"]
    explainer = artifacts["explainer"]
    feature_names: list[str] = artifacts["feature_names"]
    top_features: list[str] = artifacts["top_features"]

    X = pd.DataFrame([patient_row])[top_features]

    probability = float(pipeline.predict_proba(X)[0, 1])
    diagnosis = probability >= 0.5

    X_transformed = pipeline.named_steps["preprocessor"].transform(X)
    shap_values = explainer(X_transformed).values[0]

    contributions = [
        FeatureContribution(
            feature=name,
            contribution=round(float(val), 4),
            direction="positiva" if val > 0 else "negativa",
        )
        for name, val in zip(feature_names, shap_values)
    ]
    top_5 = sorted(contributions, key=lambda x: abs(x.contribution), reverse=True)[:5]

    return {
        "diagnosis": diagnosis,
        "probability": round(probability, 4),
        "confidence": _confidence_label(probability),
        "top_contributing_features": top_5,
        "shap_dict": dict(zip(feature_names, [float(v) for v in shap_values])),
    }
