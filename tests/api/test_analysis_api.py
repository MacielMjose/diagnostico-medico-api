from unittest.mock import AsyncMock

from app.core.dependencies import get_explainer, get_model_registry
from app.domain.exceptions import LLMRequestError
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


class TestAnalysisEndpoint:
    def test_analysis_com_mock_retorna_200(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        assert response.status_code == 200

    def test_analysis_resposta_positivo(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        data = response.json()
        assert data["diagnosis"] in ("positivo", "negativo")

    def test_analysis_inclui_probabilidade(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        data = response.json()
        assert 0.0 <= data["probability"] <= 1.0

    def test_analysis_inclui_confidence(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        data = response.json()
        assert data["confidence"] in ("Alta", "Média", "Baixa")

    def test_analysis_inclui_explanation(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        data = response.json()
        assert len(data["explanation"]) > 0
        assert isinstance(data["risk_factors"], list)
        assert isinstance(data["insights"], list)

    def test_analysis_inclui_top_features(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        data = response.json()
        assert isinstance(data["top_contributing_features"], list)

    def test_analysis_campos_invalidos_retorna_422(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json={"invalido": "dados"})
        assert response.status_code == 422

    def test_analysis_campos_faltando_retorna_422(self, client, override_deps):
        payload = {"age": 28, "bmi": 24.5}
        response = client.post("/api/v1/analysis/", json=payload)
        assert response.status_code == 422

    def test_analysis_503_quando_modelo_nao_carregado(self, app, client):
        app.dependency_overrides[get_model_registry] = lambda: ModelRegistry(
            "models/__inexistente__.joblib"
        )
        try:
            response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
            assert response.status_code == 503
        finally:
            app.dependency_overrides.pop(get_model_registry, None)

    def test_analysis_502_quando_explain_falha(self, app, client, override_deps):
        mock_broken = AsyncMock()
        mock_broken.explain.side_effect = LLMRequestError("LLM error")
        app.dependency_overrides[get_explainer] = lambda: mock_broken
        try:
            response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
            assert response.status_code == 502
        finally:
            app.dependency_overrides.pop(get_explainer, None)
