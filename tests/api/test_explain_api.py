# TODO: Teste comentado temporariamente enquanto as dependências não estão prontas
# Descomente quando:
# 1. Modelos XGBoost forem treinados
# 2. LLM_API_KEY estiver configurada
# 3. Arquivos necessários estiverem disponíveis


# class _FakeProvider:
#     provider_name = "fake/test"

#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         return (
#             '{"explanation": "Probabilidade elevada de SOP.", '
#             '"risk_factors": ["obesidade", "hirsutismo"], '
#             '"insights": ["solicitar perfil hormonal"]}'
#         )


# class TestExplainEndpoint:
#     """Testes para o endpoint POST /api/v1/explain/."""

#     PAYLOAD_VALIDO = {
#         "features": {
#             "Age (yrs)": 28,
#             "BMI": 24.5,
#             "Follicle No. (R)": 8,
#             "Follicle No. (L)": 6,
#             "Skin darkening (Y/N)": 1,
#             "hair growth(Y/N)": 1,
#             "Weight gain(Y/N)": 0,
#             "AMH(ng/mL)": 4.2,
#             "Cycle(R/I)": 2,
#             "Fast food (Y/N)": 1,
#         },
#         "diagnosis": 1,
#         "probability": 0.85,
#     }

#     def test_explain_com_mock_retorna_200(self, client, override_deps):
#         response = client.post("/api/v1/explain/", json=self.PAYLOAD_VALIDO)
#         assert response.status_code == 200
#         data = response.json()
#         assert "explanation" in data
#         assert "risk_factors" in data
#         assert "insights" in data

#     def test_explain_com_mock_retorna_texto(self, client, override_deps):
#         response = client.post("/api/v1/explain/", json=self.PAYLOAD_VALIDO)
#         data = response.json()
#         assert len(data["explanation"]) > 0
#         assert isinstance(data["risk_factors"], list)
#         assert isinstance(data["insights"], list)

#     def test_explain_com_diagnosis_negativo(self, client, override_deps):
#         payload = self.PAYLOAD_VALIDO.copy()
#         payload["diagnosis"] = 0
#         payload["probability"] = 0.15
#         response = client.post("/api/v1/explain/", json=payload)
#         assert response.status_code == 200

#     def test_explain_sem_features_retorna_422(self, app, client):
#         app.dependency_overrides[get_llm_provider] = lambda: _FakeProvider()
#         try:
#             response = client.post(
#                 "/api/v1/explain/",
#                 json={"diagnosis": 1, "probability": 0.8},
#             )
#             assert response.status_code == 422
#         finally:
#             app.dependency_overrides.pop(get_llm_provider, None)

#     def test_explain_sem_diagnosis_retorna_422(self, app, client):
#         app.dependency_overrides[get_llm_provider] = lambda: _FakeProvider()
#         try:
#             response = client.post(
#                 "/api/v1/explain/",
#                 json={"features": {"Age (yrs)": 28}, "probability": 0.8},
#             )
#             assert response.status_code == 422
#         finally:
#             app.dependency_overrides.pop(get_llm_provider, None)

#     def test_explain_campos_extra_ignorados(self, client, override_deps):
#         payload = self.PAYLOAD_VALIDO.copy()
#         payload["extra"] = "campo ignorado"
#         response = client.post("/api/v1/explain/", json=payload)
#         assert response.status_code == 200
