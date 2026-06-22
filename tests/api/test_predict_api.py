import pytest


class TestHealthEndpoint:
    """Testes para o endpoint GET /health."""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, client):
        response = client.get("/health")
        assert response.json()["version"] == "1.0.0"


class TestPredictEndpoint:
    """Testes para o endpoint POST /api/v1/predict/."""

    PAYLOAD_VALIDO = {
        "age": 28,
        "bmi": 24.5,
        "follicle_no_r": 8,
        "follicle_no_l": 6,
        "skin_darkening": 1,
        "hair_growth": 1,
        "weight_gain": 0,
        "amh": 4.2,
        "cycle_r_i": 2,
        "fast_food": 1,
    }

    def test_predict_sem_modelo_retorna_503(self, client):
        response = client.post("/api/v1/predict/", json=self.PAYLOAD_VALIDO)
        assert response.status_code == 503
        assert "Model not loaded" in response.text

    def test_predict_input_invalido_retorna_422(self, client):
        response = client.post("/api/v1/predict/", json={"invalido": "dados"})
        assert response.status_code == 422

    def test_predict_campos_faltando_retorna_422(self, client):
        payload = {"age": 28, "bmi": 24.5}
        response = client.post("/api/v1/predict/", json=payload)
        assert response.status_code == 422

    def test_predict_com_mock_retorna_200(self, client, override_deps):
        response = client.post("/api/v1/predict/", json=self.PAYLOAD_VALIDO)
        assert response.status_code == 200
        data = response.json()
        assert "diagnosis" in data
        assert "probability" in data
        assert "model_version" in data

    def test_predict_com_mock_diagnosis_valor(self, client, override_deps):
        response = client.post("/api/v1/predict/", json=self.PAYLOAD_VALIDO)
        data = response.json()
        assert data["diagnosis"] in (0, 1)
        assert 0.0 <= data["probability"] <= 1.0


class TestPredictTop20Endpoint:
    """Testes para o endpoint POST /api/v1/predict/top20."""

    PAYLOAD_VALIDO = {
        "age": 30,
        "bmi": 22.0,
        "follicle_no_r": 10,
        "follicle_no_l": 5,
        "skin_darkening": 0,
        "hair_growth": 0,
        "weight_gain": 0,
        "amh": 3.0,
        "cycle_r_i": 1,
        "fast_food": 0,
    }

    def test_predict_top20_sem_modelo_retorna_503(self, client):
        response = client.post("/api/v1/predict/top20", json=self.PAYLOAD_VALIDO)
        assert response.status_code == 503

    def test_predict_top20_com_mock_retorna_200(self, client, override_deps):
        response = client.post("/api/v1/predict/top20", json=self.PAYLOAD_VALIDO)
        assert response.status_code == 200
        data = response.json()
        assert "diagnosis" in data
        assert "probability" in data
