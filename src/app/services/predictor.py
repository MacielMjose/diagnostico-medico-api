import pandas as pd
import structlog

from app.domain.exceptions import InvalidFeaturesError, ModelNotLoadedError
from app.domain.features import FEATURE_COLUMN_MAP, FEATURE_LABELS, FeatureValidator
from app.domain.models import FeatureContribution, PCOSPrediction
from app.infrastructure.model_registry import ModelRegistry

logger = structlog.get_logger()

_MODEL_VERSION = "2.0.0"
_CONFIDENCE_HIGH = 0.80
_CONFIDENCE_MED = 0.60

# FEATURE_LABELS usa nomes com prefixo do ColumnTransformer antigo
# (ex.: "num__Follicle No. (R)"). O novo modelo trabalha direto com o nome
# bruto da coluna (ex.: "Follicle No. (R)"), então derivamos um mapa sem
# prefixo para reaproveitar os rótulos em PT-BR já existentes.
_RAW_FEATURE_LABELS: dict[str, str] = {
    name.split("__", 1)[-1]: label for name, label in FEATURE_LABELS.items()
}


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
        FeatureValidator.validate_no_negative(features, InvalidFeaturesError)
        FeatureValidator.validate_binary_only(features, InvalidFeaturesError)

        logger.info("prediction_started", features_count=len(features))

        model = self.registry.load_artifacts()
        if model is None:
            logger.error("prediction_failed", reason="model_not_loaded")
            raise ModelNotLoadedError("Model not loaded")

        top_features: list[str] = list(model.feature_names_in_)

        patient_row = {FEATURE_COLUMN_MAP[k]: v for k, v in features.items()}
        X = pd.DataFrame([patient_row])[top_features]

        probability = float(model.predict_proba(X)[0, 1])
        diagnosis = int(probability >= 0.5)

        # O modelo atual é uma LogisticRegression treinada direto sobre as
        # features brutas, sem pipeline de pré-processamento nem explainer
        # SHAP embutido. Por ser um modelo linear (fit_intercept=False), a
        # contribuição exata de cada feature para o log-odds da predição é
        # coeficiente * valor — dispensa a necessidade de um SHAP explainer.
        coefficients = model.coef_[0]
        raw_values = X.iloc[0].to_numpy()
        contributions = [
            FeatureContribution(
                feature=_RAW_FEATURE_LABELS.get(name, name),
                contribution=round(float(coef * value), 4),
                direction="positiva" if coef * value > 0 else "negativa",
            )
            for name, coef, value in zip(top_features, coefficients, raw_values)
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
