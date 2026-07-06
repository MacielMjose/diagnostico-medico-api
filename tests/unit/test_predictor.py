import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from app.domain.exceptions import ModelNotLoadedError
from app.domain.features import FEATURE_COLUMN_MAP
from app.domain.models import PCOSPrediction
from app.infrastructure.model_registry import ModelRegistry
from app.services.predictor import PredictorService, _confidence_label


class TestConfidenceLabel:
    def test_alta_para_prob_acima_80(self):
        assert _confidence_label(0.95) == "Alta"
        assert _confidence_label(0.80) == "Alta"

    def test_media_para_prob_entre_60_e_80(self):
        assert _confidence_label(0.70) == "Média"
        assert _confidence_label(0.60) == "Média"

    def test_baixa_para_prob_abaixo_60(self):
        assert _confidence_label(0.52) == "Baixa"
        assert _confidence_label(0.55) == "Baixa"


class TestPredictorService:
    _PATIENT = {
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
        "hb": 11.5,
    }

    @pytest.fixture
    def trained_model(self, tmp_path):
        rng = np.random.RandomState(42)
        n = 100
        feature_names = list(FEATURE_COLUMN_MAP.values())
        X = pd.DataFrame(rng.randn(n, len(feature_names)), columns=feature_names)
        y = rng.randint(0, 2, n)
        model = LogisticRegression()
        model.fit(X, y)

        path = tmp_path / "model.joblib"
        import joblib

        joblib.dump(model, path)
        return str(path)

    def test_predict_returns_pcos_prediction(self, trained_model):
        predictor = PredictorService(ModelRegistry(trained_model))
        result = predictor.predict(self._PATIENT)
        assert isinstance(result, PCOSPrediction)
        assert result.diagnosis in (0, 1)
        assert 0.0 <= result.probability <= 1.0

    def test_predict_includes_confidence(self, trained_model):
        predictor = PredictorService(ModelRegistry(trained_model))
        result = predictor.predict(self._PATIENT)
        assert result.confidence in ("Alta", "Média", "Baixa")

    def test_predict_includes_top_features(self, trained_model):
        predictor = PredictorService(ModelRegistry(trained_model))
        result = predictor.predict(self._PATIENT)
        assert len(result.top_contributing_features) == 5

    def test_predict_top_features_have_direction(self, trained_model):
        predictor = PredictorService(ModelRegistry(trained_model))
        result = predictor.predict(self._PATIENT)
        for fc in result.top_contributing_features:
            assert fc.direction in ("positiva", "negativa")

    def test_predict_raises_when_model_not_loaded(self):
        registry = ModelRegistry("models/nonexistent.joblib")
        predictor = PredictorService(registry)
        with pytest.raises(ModelNotLoadedError):
            predictor.predict(self._PATIENT)

    def test_predict_uses_correct_model_version(self, trained_model):
        predictor = PredictorService(ModelRegistry(trained_model))
        result = predictor.predict(self._PATIENT)
        assert result.model_version == "2.0.0"
