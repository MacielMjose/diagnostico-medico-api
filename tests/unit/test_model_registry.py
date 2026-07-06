import joblib
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

from app.infrastructure.model_registry import ModelRegistry


class TestModelRegistry:
    @pytest.fixture
    def dummy_model(self, tmp_path):
        rng = np.random.RandomState(42)
        X = rng.randn(50, 5)
        y = rng.randint(0, 2, 50)
        model = LogisticRegression()
        model.fit(X, y)
        path = tmp_path / "model.joblib"
        joblib.dump(model, path)
        return str(path)

    def test_load_artifacts_returns_model_when_found(self, dummy_model):
        registry = ModelRegistry(dummy_model)
        model = registry.load_artifacts()
        assert model is not None
        assert isinstance(model, LogisticRegression)

    def test_load_artifacts_model_has_predict_proba(self, dummy_model):
        registry = ModelRegistry(dummy_model)
        model = registry.load_artifacts()
        X = np.random.randn(1, 5)
        proba = model.predict_proba(X)
        assert proba.shape == (1, 2)

    def test_load_artifacts_returns_none_when_not_found(self):
        registry = ModelRegistry("models/nonexistent.joblib")
        result = registry.load_artifacts()
        assert result is None

    def test_load_artifacts_caches_result(self, dummy_model):
        registry = ModelRegistry(dummy_model)
        result1 = registry.load_artifacts()
        result2 = registry.load_artifacts()
        assert result1 is result2
