from app.core.dependencies import get_llm_provider
from app.infrastructure.llm.base import LLMResponse

_PAYLOAD_VALIDO = {
    "features": {
        "Age (yrs)": 28,
        "BMI": 24.5,
        "Follicle No. (R)": 8,
        "Follicle No. (L)": 6,
        "Skin darkening (Y/N)": 1,
        "hair growth(Y/N)": 1,
        "Weight gain(Y/N)": 0,
        "AMH(ng/mL)": 4.2,
        "Cycle(R/I)": 2,
        "Fast food (Y/N)": 1,
        "Pimples(Y/N)": 0,
        "Hair loss(Y/N)": 0,
        "Hb(g/dl)": 12.5,
        "Pulse rate(bpm) ": 72,
    },
    "diagnosis": 1,
    "probability": 0.85,
}


class TestExplainEndpoint:
    def test_explain_com_mock_retorna_200(self, client, override_deps):
        response = client.post("/api/v1/explain/", json=_PAYLOAD_VALIDO)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "risk_factors" in data
        assert "insights" in data

    def test_explain_com_mock_retorna_texto(self, client, override_deps):
        response = client.post("/api/v1/explain/", json=_PAYLOAD_VALIDO)
        data = response.json()
        assert len(data["explanation"]) > 0
        assert isinstance(data["risk_factors"], list)
        assert isinstance(data["insights"], list)

    def test_explain_com_diagnosis_negativo(self, client, override_deps):
        payload = _PAYLOAD_VALIDO.copy()
        payload["diagnosis"] = 0
        payload["probability"] = 0.15
        response = client.post("/api/v1/explain/", json=payload)
        assert response.status_code == 200

    def test_explain_sem_features_retorna_422(self, client, override_deps):
        response = client.post(
            "/api/v1/explain/",
            json={"diagnosis": 1, "probability": 0.8},
        )
        assert response.status_code == 422

    def test_explain_sem_diagnosis_retorna_422(self, client, override_deps):
        response = client.post(
            "/api/v1/explain/",
            json={"features": {"Age (yrs)": 28}, "probability": 0.8},
        )
        assert response.status_code == 422

    def test_explain_campos_extra_ignorados(self, client, override_deps):
        payload = _PAYLOAD_VALIDO.copy()
        payload["extra"] = "campo ignorado"
        response = client.post("/api/v1/explain/", json=payload)
        assert response.status_code == 200

    def test_explain_menos_de_10_features_retorna_400(self, client, override_deps):
        payload = {
            "features": {"BMI": 24.5, "Age (yrs)": 28},
            "diagnosis": 1,
            "probability": 0.85,
        }
        response = client.post("/api/v1/explain/", json=payload)
        assert response.status_code == 400

    def test_explain_features_desconhecidas_retorna_400(self, client, override_deps):
        payload = _PAYLOAD_VALIDO.copy()
        payload["features"] = {"feature_invalida": 1.0}
        for k in _PAYLOAD_VALIDO["features"]:
            payload["features"][k] = _PAYLOAD_VALIDO["features"][k]
        response = client.post("/api/v1/explain/", json=payload)
        assert response.status_code == 400

    def test_explain_502_quando_llm_falha(self, app, client):
        class _BrokenProvider:
            provider_name = "broken/test"

            def generate(self, system_prompt, user_prompt):
                raise RuntimeError("API timeout")

        app.dependency_overrides[get_llm_provider] = lambda: _BrokenProvider()
        try:
            response = client.post("/api/v1/explain/", json=_PAYLOAD_VALIDO)
            assert response.status_code == 502
        finally:
            app.dependency_overrides.pop(get_llm_provider, None)

    def test_explain_200_quando_llm_retorna_json_com_markdown(self, app, client):
        class _FakeProvider:
            provider_name = "fake/test"

            def generate(self, system_prompt, user_prompt):
                return LLMResponse(
                    text=(
                        '```json\n{"explanation": "Probabilidade elevada de SOP.", '
                        '"risk_factors": ["obesidade", "hirsutismo"], '
                        '"insights": ["solicitar perfil hormonal"]}\n```'
                    ),
                    tokens_used=50,
                )

        app.dependency_overrides[get_llm_provider] = lambda: _FakeProvider()
        try:
            response = client.post("/api/v1/explain/", json=_PAYLOAD_VALIDO)
            assert response.status_code == 200
            data = response.json()
            assert data["explanation"] == "Probabilidade elevada de SOP."
            assert data["risk_factors"] == ["obesidade", "hirsutismo"]
            assert data["insights"] == ["solicitar perfil hormonal"]
        finally:
            app.dependency_overrides.pop(get_llm_provider, None)
