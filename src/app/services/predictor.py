from app.domain.models import PCOSPrediction
from app.domain.exceptions import ModelNotLoadedError
from app.infrastructure.model_registry import ModelRegistry


class PredictorService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def predict(self, features: dict) -> PCOSPrediction:
        pipeline = self.registry.load_pipeline("logistic_regression")
        if pipeline is None:
            raise ModelNotLoadedError("Model not loaded")
        proba = pipeline.predict_proba([list(features.values())])[0]
        diagnosis = int(proba[1] >= 0.5)
        return PCOSPrediction(
            diagnosis=diagnosis,
            probability=float(proba[1]),
            model_version="1.0.0",
        )

    def predict_top20(self, features: dict) -> PCOSPrediction:
        pipeline = self.registry.load_pipeline("logistic_regression_top20")
        if pipeline is None:
            raise ModelNotLoadedError("Top20 model not loaded")
        proba = pipeline.predict_proba([list(features.values())])[0]
        diagnosis = int(proba[1] >= 0.5)
        return PCOSPrediction(
            diagnosis=diagnosis,
            probability=float(proba[1]),
            model_version="1.0.0",
        )
