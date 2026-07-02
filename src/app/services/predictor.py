import pandas as pd
import structlog

from app.domain.exceptions import ModelNotLoadedError
from app.domain.features import FEATURE_COLUMN_MAP
from app.domain.models import FeatureContribution, PCOSPrediction
from app.infrastructure.model_registry import ModelRegistry

logger = structlog.get_logger()

_MODEL_VERSION = "1.0.0"
_CONFIDENCE_HIGH = 0.80
_CONFIDENCE_MED = 0.60


def _confidence_label(probability: float) -> str:
    dist_from_boundary = abs(probability - 0.5)
    if dist_from_boundary >= (_CONFIDENCE_HIGH - 0.5):
        return "Alta"
    if dist_from_boundary >= (_CONFIDENCE_MED - 0.5):
        return "Média"
    return "Baixa"


class PredictorService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def predict(self, features: dict) -> PCOSPrediction:
        logger.info("prediction_started", features_count=len(features))

        artifacts = self.registry.load_artifacts()
        if artifacts is None:
            logger.error("prediction_failed", reason="model_not_loaded")
            raise ModelNotLoadedError("Model not loaded")

        pipeline = artifacts["pipeline"]
        explainer = artifacts["explainer"]
        feature_names: list[str] = artifacts["feature_names"]
        top_features: list[str] = artifacts["top_features"]

        patient_row = {FEATURE_COLUMN_MAP[k]: v for k, v in features.items()}
        X = pd.DataFrame([patient_row])[top_features]

        probability = float(pipeline.predict_proba(X)[0, 1])
        diagnosis = int(probability >= 0.5)

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
        top_5 = sorted(contributions, key=lambda c: abs(c.contribution), reverse=True)[
            :5
        ]

        logger.info(
            "prediction_completed",
            diagnosis=diagnosis,
            probability=round(probability, 4),
            confidence=_confidence_label(probability),
            model_version=_MODEL_VERSION,
        )

        return PCOSPrediction(
            diagnosis=diagnosis,
            probability=round(probability, 4),
            model_version=_MODEL_VERSION,
            confidence=_confidence_label(probability),
            top_contributing_features=top_5,
        )
