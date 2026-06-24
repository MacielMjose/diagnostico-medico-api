from unittest.mock import MagicMock

import numpy as np
import pytest

from app.domain.exceptions import ModelNotLoadedError
from app.services.predictor import PredictorService, _confidence_label

_TOP_FEATURES = [
    "Follicle No. (R)",
    "Follicle No. (L)",
    "Skin darkening (Y/N)",
    "hair growth(Y/N)",
    "Weight gain(Y/N)",
    "Cycle(R/I)",
    "Fast food (Y/N)",
    "Pimples(Y/N)",
    "AMH(ng/mL)",
    "BMI",
    "Cycle length(days)",
    "Hair loss(Y/N)",
    " Age (yrs)",
    "Hip(inch)",
    "Avg. F size (L) (mm)",
    "Marraige Status (Yrs)",
    "Endometrium (mm)",
    "Avg. F size (R) (mm)",
    "Pulse rate(bpm) ",
    "Hb(g/dl)",
]
_FEATURE_NAMES = [f"num__f{i}" for i in range(20)]

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


def _fake_artifacts():
    pipeline = MagicMock()
    pipeline.predict_proba.return_value = np.array([[0.13, 0.87]])
    pipeline.named_steps = {"preprocessor": MagicMock()}
    pipeline.named_steps["preprocessor"].transform.return_value = np.zeros((1, 20))

    explainer = MagicMock()
    shap_out = MagicMock()
    shap_out.values = np.array([np.linspace(-1, 1, 20)])
    explainer.return_value = shap_out

    return {
        "pipeline": pipeline,
        "explainer": explainer,
        "feature_names": _FEATURE_NAMES,
        "top_features": _TOP_FEATURES,
    }


class TestPredictorService:
    """Testes para o PredictorService (predição de diagnóstico)."""

    def test_predict_returns_prediction_with_top5(self):
        registry = MagicMock()
        registry.load_artifacts.return_value = _fake_artifacts()

        result = PredictorService(registry).predict(_PATIENT)

        assert result.diagnosis == 1
        assert result.probability == pytest.approx(0.87)
        assert result.confidence == "Alta"
        assert len(result.top_contributing_features) == 5

    def test_predict_raises_when_model_missing(self):
        registry = MagicMock()
        registry.load_artifacts.return_value = None

        with pytest.raises(ModelNotLoadedError):
            PredictorService(registry).predict(_PATIENT)


def test_confidence_labels():
    assert _confidence_label(0.95) == "Alta"
    assert _confidence_label(0.70) == "Média"
    assert _confidence_label(0.52) == "Baixa"
