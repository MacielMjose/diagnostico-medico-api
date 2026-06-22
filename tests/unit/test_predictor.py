from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.domain.exceptions import ModelNotLoadedError
from app.services.predictor import PredictorService


def _build_dummy_pipeline():
    pipeline = make_pipeline(StandardScaler(), LogisticRegression())
    X = np.random.randn(50, 10)
    y = np.random.randint(0, 2, 50)
    pipeline.fit(X, y)
    return pipeline


class TestPredictorService:
    """Testes para o PredictorService (predição de diagnóstico)."""

    def test_predict_returns_pcos_prediction(self):
        pipeline = _build_dummy_pipeline()
        mock_registry = MagicMock()
        mock_registry.load_pipeline.return_value = pipeline

        service = PredictorService(mock_registry)
        features = {
            "Age (yrs)": 28.0,
            "BMI": 24.5,
            "Follicle No. (R)": 8.0,
            "Follicle No. (L)": 6.0,
            "Skin darkening (Y/N)": 1,
            "hair growth(Y/N)": 1,
            "Weight gain(Y/N)": 0,
            "AMH(ng/mL)": 4.2,
            "Cycle(R/I)": 2,
            "Fast food (Y/N)": 1,
        }
        result = service.predict(features)
        assert result.diagnosis in (0, 1)
        assert 0.0 <= result.probability <= 1.0
        assert result.model_version == "1.0.0"

    def test_predict_raises_when_model_not_found(self):
        mock_registry = MagicMock()
        mock_registry.load_pipeline.return_value = None

        service = PredictorService(mock_registry)
        with pytest.raises(ModelNotLoadedError, match="Model not loaded"):
            service.predict({"feature1": 1.0})

    def test_predict_top20_returns_prediction(self):
        pipeline = _build_dummy_pipeline()
        mock_registry = MagicMock()
        mock_registry.load_pipeline.return_value = pipeline

        service = PredictorService(mock_registry)
        features = {
            "Age (yrs)": 30.0,
            "BMI": 22.0,
            "Follicle No. (R)": 10.0,
            "Follicle No. (L)": 5.0,
            "Skin darkening (Y/N)": 0,
            "hair growth(Y/N)": 0,
            "Weight gain(Y/N)": 0,
            "AMH(ng/mL)": 3.0,
            "Cycle(R/I)": 1,
            "Fast food (Y/N)": 0,
        }
        result = service.predict_top20(features)
        assert result.diagnosis in (0, 1)
        assert result.model_version == "1.0.0"

    def test_predict_top20_raises_when_model_not_found(self):
        mock_registry = MagicMock()
        mock_registry.load_pipeline.return_value = None

        service = PredictorService(mock_registry)
        with pytest.raises(ModelNotLoadedError, match="Top20 model not loaded"):
            service.predict_top20({"feature1": 1.0})

    def _build_10_features(self):
        return {
            "Age (yrs)": 28.0,
            "BMI": 24.5,
            "Follicle No. (R)": 8.0,
            "Follicle No. (L)": 6.0,
            "Skin darkening (Y/N)": 1,
            "hair growth(Y/N)": 1,
            "Weight gain(Y/N)": 0,
            "AMH(ng/mL)": 4.2,
            "Cycle(R/I)": 2,
            "Fast food (Y/N)": 1,
        }

    def test_predict_loads_logistic_regression_model(self):
        mock_registry = MagicMock()
        mock_registry.load_pipeline.return_value = _build_dummy_pipeline()

        service = PredictorService(mock_registry)
        service.predict(self._build_10_features())
        mock_registry.load_pipeline.assert_called_with("logistic_regression")

    def test_predict_top20_loads_top20_model(self):
        mock_registry = MagicMock()
        mock_registry.load_pipeline.return_value = _build_dummy_pipeline()

        service = PredictorService(mock_registry)
        service.predict_top20(self._build_10_features())
        mock_registry.load_pipeline.assert_called_with("logistic_regression_top20")
