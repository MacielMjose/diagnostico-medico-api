import json
from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.infrastructure.model_registry import ModelRegistry


def _make_dummy_pipeline():
    pipeline = make_pipeline(StandardScaler(), LogisticRegression())
    X = np.random.randn(20, 5)
    y = np.random.randint(0, 2, 20)
    pipeline.fit(X, y)
    return pipeline


class TestModelRegistry:
    """Testes para o ModelRegistry (carregamento de modelos do disco)."""

    def test_load_pipeline_returns_none_when_not_found(self, tmp_path):
        registry = ModelRegistry(str(tmp_path))
        result = registry.load_pipeline("nonexistent")
        assert result is None

    def test_load_pipeline_returns_pipeline_when_found(self, tmp_path):
        pipeline = _make_dummy_pipeline()
        joblib.dump(pipeline, tmp_path / "logistic_regression.pkl")

        registry = ModelRegistry(str(tmp_path))
        result = registry.load_pipeline("logistic_regression")
        assert result is not None
        assert hasattr(result, "predict")
        assert hasattr(result, "predict_proba")

    def test_load_pipeline_caches_result(self, tmp_path):
        pipeline = _make_dummy_pipeline()
        joblib.dump(pipeline, tmp_path / "model.pkl")

        registry = ModelRegistry(str(tmp_path))
        result1 = registry.load_pipeline("model")
        result2 = registry.load_pipeline("model")
        assert result1 is result2

    def test_load_features_top20_returns_list(self, tmp_path):
        features = ["Age (yrs)", "BMI", "Follicle No. (R)"]
        with open(tmp_path / "selected_features.json", "w") as f:
            json.dump(features, f)

        registry = ModelRegistry(str(tmp_path))
        result = registry.load_features_top20()
        assert result == features
        assert len(result) == 3

    def test_load_features_top20_returns_empty_when_not_found(self, tmp_path):
        registry = ModelRegistry(str(tmp_path))
        result = registry.load_features_top20()
        assert result == []

    def test_list_available_returns_model_names(self, tmp_path):
        for name in ["model_a", "model_b", "model_c"]:
            pipeline = _make_dummy_pipeline()
            joblib.dump(pipeline, tmp_path / f"{name}.pkl")

        registry = ModelRegistry(str(tmp_path))
        available = registry.list_available()
        assert sorted(available) == sorted(["model_a", "model_b", "model_c"])

    def test_list_available_returns_empty_when_no_models(self, tmp_path):
        registry = ModelRegistry(str(tmp_path))
        assert registry.list_available() == []

    def test_load_features_top20_file_not_json(self, tmp_path):
        with open(tmp_path / "selected_features.json", "w") as f:
            f.write("not valid json")

        registry = ModelRegistry(str(tmp_path))
        with pytest.raises(json.JSONDecodeError):
            registry.load_features_top20()
