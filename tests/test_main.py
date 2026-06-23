from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from minha_api.main import app
from minha_api.schemas import FeatureContribution

client = TestClient(app)

_PATIENT_PAYLOAD = {
    "follicle_no_r": 12,
    "follicle_no_l": 10,
    "skin_darkening": 1,
    "hair_growth": 1,
    "weight_gain": 1,
    "cycle": 4,
    "fast_food": 1,
    "pimples": 1,
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

_MOCK_PREDICTION = {
    "diagnosis": True,
    "probability": 0.87,
    "confidence": "Alta",
    "top_contributing_features": [
        FeatureContribution(feature="num__Follicle No. (R)", contribution=1.3, direction="positiva"),
        FeatureContribution(feature="num__Cycle(R/I)", contribution=0.6, direction="positiva"),
        FeatureContribution(feature="bin__hair growth(Y/N)", contribution=0.58, direction="positiva"),
        FeatureContribution(feature="bin__Skin darkening (Y/N)", contribution=0.55, direction="positiva"),
        FeatureContribution(feature="num__Follicle No. (L)", contribution=0.48, direction="positiva"),
    ],
    "shap_dict": {},
}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_diagnose_positive():
    with (
        patch("minha_api.main.predict", return_value=_MOCK_PREDICTION),
        patch("minha_api.main.interpret", return_value="Interpretação mock."),
    ):
        response = client.post("/diagnose", json=_PATIENT_PAYLOAD)

    assert response.status_code == 200
    data = response.json()
    assert data["diagnosis"] is True
    assert data["probability"] == 0.87
    assert data["confidence"] == "Alta"
    assert len(data["top_contributing_features"]) == 5
    assert "interpretation" in data
    assert "disclaimer" in data


def test_diagnose_negative():
    mock_negative = {**_MOCK_PREDICTION, "diagnosis": False, "probability": 0.12, "confidence": "Alta"}
    with (
        patch("minha_api.main.predict", return_value=mock_negative),
        patch("minha_api.main.interpret", return_value="Baixa probabilidade de SOP."),
    ):
        response = client.post("/diagnose", json=_PATIENT_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["diagnosis"] is False


def test_diagnose_model_not_found():
    with patch("minha_api.main.predict", side_effect=FileNotFoundError("Modelo não encontrado.")):
        response = client.post("/diagnose", json=_PATIENT_PAYLOAD)

    assert response.status_code == 503
    assert "Modelo não encontrado" in response.json()["detail"]


def test_diagnose_invalid_payload():
    bad_payload = {**_PATIENT_PAYLOAD, "skin_darkening": 5}  # deve ser 0 ou 1
    response = client.post("/diagnose", json=bad_payload)
    assert response.status_code == 422
