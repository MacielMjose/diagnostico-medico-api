from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from minha_api.models.pcos_classifier import _confidence_label, predict
from minha_api.schemas import FeatureContribution


def test_confidence_high_positive():
    assert _confidence_label(0.90) == "Alta"


def test_confidence_high_negative():
    assert _confidence_label(0.05) == "Alta"


def test_confidence_medium():
    assert _confidence_label(0.70) == "Média"
    assert _confidence_label(0.35) == "Média"


def test_confidence_low():
    assert _confidence_label(0.51) == "Baixa"
    assert _confidence_label(0.49) == "Baixa"


def _make_shap_values(n_features: int, value: float = 0.5):
    mock = MagicMock()
    mock.values = np.full((1, n_features), value)
    return mock


def _build_mock_artifacts(top_features: list[str], feature_names: list[str]):
    pipeline = MagicMock()
    pipeline.predict_proba.return_value = np.array([[0.13, 0.87]])
    pipeline.named_steps = {
        "preprocessor": MagicMock(transform=MagicMock(return_value=np.zeros((1, len(feature_names)))))
    }

    explainer = MagicMock()
    explainer.return_value = _make_shap_values(len(feature_names))

    return {
        "pipeline": pipeline,
        "explainer": explainer,
        "feature_names": feature_names,
        "top_features": top_features,
    }


def test_predict_returns_expected_structure():
    top_features = ["Follicle No. (R)", "Follicle No. (L)", "Cycle(R/I)"]
    feature_names = ["num__Follicle No. (R)", "num__Follicle No. (L)", "num__Cycle(R/I)"]
    artifacts = _build_mock_artifacts(top_features, feature_names)

    patient_row = {"Follicle No. (R)": 12.0, "Follicle No. (L)": 10.0, "Cycle(R/I)": 4.0}

    with patch("minha_api.models.pcos_classifier._load_artifacts", return_value=artifacts):
        result = predict(patient_row)

    assert result["diagnosis"] is True
    assert 0.0 <= result["probability"] <= 1.0
    assert result["confidence"] in ("Alta", "Média", "Baixa")
    assert isinstance(result["top_contributing_features"], list)
    assert all(isinstance(f, FeatureContribution) for f in result["top_contributing_features"])
    assert len(result["top_contributing_features"]) <= 5


def test_predict_raises_if_model_missing():
    with patch(
        "minha_api.models.pcos_classifier._load_artifacts",
        side_effect=FileNotFoundError("Modelo não encontrado"),
    ):
        with pytest.raises(FileNotFoundError):
            predict({"Follicle No. (R)": 5.0})
