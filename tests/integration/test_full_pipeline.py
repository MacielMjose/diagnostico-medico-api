# _VALID_PATIENT = {
#     "follicle_no_r": 12,
#     "follicle_no_l": 10,
#     "skin_darkening": 1,
#     "hair_growth": 1,
#     "weight_gain": 1,
#     "cycle": 4,
#     "fast_food": 1,
#     "pimples": 0,
#     "amh": 7.5,
#     "bmi": 27.0,
#     "cycle_length": 4,
#     "hair_loss": 0,
#     "age": 28,
#     "hip": 40,
#     "avg_f_size_l": 16.0,
#     "marriage_status": 3.0,
#     "endometrium": 9.0,
#     "avg_f_size_r": 17.0,
#     "pulse_rate": 74,
#     "hb": 11.5,
# }


# class TestFullPipeline:
#     """Teste de integraÃ§Ã£o do fluxo completo: health â†’ predict â†’ explain â†’ optimize."""

#     def test_health_entao_predict_entao_explain(self, client, override_deps):
#         health = client.get("/health")
#         assert health.status_code == 200

#         predict = client.post("/api/v1/predict/", json=_VALID_PATIENT)
#         assert predict.status_code == 200
#         pred_data = predict.json()

#         explain = client.post(
#             "/api/v1/explain/",
#             json={
#                 "features": _VALID_PATIENT,
#                 "diagnosis": pred_data["diagnosis"],
#                 "probability": pred_data["probability"],
#             },
#         )
#         assert explain.status_code == 200
#         expl_data = explain.json()
#         assert len(expl_data["explanation"]) > 0

#     def test_optimize_entao_predict(self, client, override_deps):
#         optimize = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": 20,
#                 "generations": 5,
#                 "mutation_rate": 0.1,
#                 "crossover_rate": 0.8,
#             },
#         )
#         assert optimize.status_code == 200
#         opt_data = optimize.json()
#         assert "best_params" in opt_data

#         predict = client.post("/api/v1/predict/", json=_VALID_PATIENT)
#         assert predict.status_code == 200

#     def test_todos_endpoints_respondem(self, client, override_deps):
#         endpoints = [
#             ("GET", "/health", None),
#             ("POST", "/api/v1/predict/", _VALID_PATIENT),
#             (
#                 "POST",
#                 "/api/v1/optimize/",
#                 {
#                     "population_size": 30,
#                     "generations": 10,
#                     "mutation_rate": 0.1,
#                     "crossover_rate": 0.8,
#                 },
#             ),
#             (
#                 "POST",
#                 "/api/v1/explain/",
#                 {
#                     "features": {"BMI": 27.0},
#                     "diagnosis": 1,
#                     "probability": 0.85,
#                 },
#             ),
#         ]
#         for method, path, body in endpoints:
#             if method == "GET":
#                 response = client.get(path)
#             else:
#                 response = client.post(path, json=body)
#             assert response.status_code == 200, (
#                 f"{method} {path} retornou {response.status_code}"
#             )
