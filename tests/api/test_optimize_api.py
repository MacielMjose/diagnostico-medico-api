# TODO: Teste comentado temporariamente enquanto as dependências não estão prontas
# Descomente quando:
# 1. Modelos XGBoost forem treinados
# 2. LLM_API_KEY estiver configurada
# 3. Arquivos necessários estiverem disponíveis


# class TestOptimizeEndpoint:
#     """Testes para o endpoint POST /api/v1/optimize/."""

#     def test_optimize_com_mock_retorna_200(self, client, override_deps):
#         response = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": 30,
#                 "generations": 10,
#                 "mutation_rate": 0.1,
#                 "crossover_rate": 0.8,
#             },
#         )
#         assert response.status_code == 200
#         data = response.json()
#         assert "best_params" in data
#         assert "fitness_history" in data
#         assert "comparison" in data

#     def test_optimize_com_mock_retorna_estrutura_correta(self, client, override_deps):
#         response = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": 50,
#                 "generations": 20,
#                 "mutation_rate": 0.05,
#                 "crossover_rate": 0.8,
#             },
#         )
#         data = response.json()
#         assert isinstance(data["best_params"], dict)
#         assert isinstance(data["fitness_history"], list)
#         assert isinstance(data["comparison"], dict)

#     def test_optimize_populacao_minima(self, client, override_deps):
#         response = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": 10,
#                 "generations": 1,
#                 "mutation_rate": 0.0,
#                 "crossover_rate": 0.0,
#             },
#         )
#         assert response.status_code == 200

#     def test_optimize_populacao_negativa_retorna_422(self, client):
#         response = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": -5,
#                 "generations": 10,
#                 "mutation_rate": 0.1,
#                 "crossover_rate": 0.8,
#             },
#         )
#         assert response.status_code == 422

#     def test_optimize_mutation_rate_acima_do_maximo_retorna_422(self, client):
#         response = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": 50,
#                 "generations": 10,
#                 "mutation_rate": 1.5,
#                 "crossover_rate": 0.8,
#             },
#         )
#         assert response.status_code == 422

#     def test_optimize_model_type_invalido(self, client):
#         response = client.post(
#             "/api/v1/optimize/",
#             json={
#                 "population_size": 50,
#                 "generations": 10,
#                 "mutation_rate": 0.1,
#                 "crossover_rate": 0.8,
#                 "model_type": "modelo_inexistente",
#             },
#         )
#         assert response.status_code == 200

#     def test_optimize_campos_brigatorio_usam_defaults(self, client, override_deps):
#         """Todos os campos do GeneticConfig tÃªm valor default, entÃ£o {} deve funcionar."""
#         response = client.post("/api/v1/optimize/", json={})
#         assert response.status_code == 200
#         data = response.json()
#         assert "best_params" in data
