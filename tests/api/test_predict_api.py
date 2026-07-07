from app.core.dependencies import get_model_registry
from app.infrastructure.model_registry import ModelRegistry

_VALID_PATIENT = {
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


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, client):
        response = client.get("/health")
        assert response.json()["version"] == "1.0.0"


class TestPredictValidation:
    """Testes de validação do endpoint POST /api/v1/predict/."""

    def test_predict_input_invalido_retorna_422(self, client):
        response = client.post("/api/v1/predict/", json={"invalido": "dados"})
        assert response.status_code == 422

    def test_predict_campos_faltando_retorna_422(self, client):
        payload = {"age": 28, "bmi": 24.5}
        response = client.post("/api/v1/predict/", json=payload)
        assert response.status_code == 422

    def test_predict_follicle_no_r_negativo_retorna_422(self, client):
        payload = {**_VALID_PATIENT, "follicle_no_r": -1}
        response = client.post("/api/v1/predict/", json=payload)
        assert response.status_code == 422

    def test_predict_follicle_no_l_negativo_retorna_422(self, client):
        payload = {**_VALID_PATIENT, "follicle_no_l": -5}
        response = client.post("/api/v1/predict/", json=payload)
        assert response.status_code == 422

    def test_predict_cycle_invalido_retorna_422(self, client):
        payload = {**_VALID_PATIENT, "cycle": 3}
        response = client.post("/api/v1/predict/", json=payload)
        assert response.status_code == 422

    def test_predict_campos_com_valores_invalidos_retorna_422(self, client):
        payload = _VALID_PATIENT.copy()
        payload["age"] = -1
        response = client.post("/api/v1/predict/", json=payload)
        assert response.status_code == 422


class TestPredictEndpoint:
    """Testes do endpoint predict com dependências mockadas."""

    def test_predict_com_mock_retorna_200(self, client, override_deps):
        response = client.post("/api/v1/predict/", json=_VALID_PATIENT)
        assert response.status_code == 200
        data = response.json()
        assert "diagnosis" in data
        assert "probability" in data
        assert "model_version" in data
        assert "confidence" in data
        assert "top_contributing_features" in data

    def test_predict_com_mock_diagnosis_valor(self, client, override_deps):
        response = client.post("/api/v1/predict/", json=_VALID_PATIENT)
        data = response.json()
        assert data["diagnosis"] in (0, 1)
        assert 0.0 <= data["probability"] <= 1.0
        assert data["confidence"] in ("Alta", "Média", "Baixa")

    def test_predict_returns_503_when_no_model(self, app, client):
        app.dependency_overrides[get_model_registry] = lambda: ModelRegistry(
            "models/__inexistente__.joblib"
        )
        try:
            response = client.post("/api/v1/predict/", json=_VALID_PATIENT)
            assert response.status_code == 503
            assert "Model not loaded" in response.text
        finally:
            app.dependency_overrides.pop(get_model_registry, None)

    def test_predict_com_mock_confidence_presente(self, client, override_deps):
        response = client.post("/api/v1/predict/", json=_VALID_PATIENT)
        data = response.json()
        assert data["confidence"] in ("Alta", "Média", "Baixa")

    def test_predict_com_mock_top_features_list(self, client, override_deps):
        response = client.post("/api/v1/predict/", json=_VALID_PATIENT)
        data = response.json()
        assert isinstance(data["top_contributing_features"], list)


class TestExplainValidation:
    """Testes de validação do endpoint POST /api/v1/explain/."""

    def test_explain_feature_negativa_retorna_422(self, client, override_deps):
        response = client.post(
            "/api/v1/explain/",
            json={
                "features": {"BMI": -1},
                "diagnosis": 1,
                "probability": 0.87,
            },
        )
        assert response.status_code == 422
