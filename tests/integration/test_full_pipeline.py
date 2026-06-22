class TestFullPipeline:
    """Teste de integração do fluxo completo: health → predict → explain → optimize."""

    def test_health_entao_predict_entao_explain(self, client, override_deps):
        # 1. Health check
        health = client.get("/health")
        assert health.status_code == 200

        # 2. Predict
        predict_payload = {
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
        predict = client.post("/api/v1/predict/", json=predict_payload)
        assert predict.status_code == 200
        pred_data = predict.json()

        explain_payload = {
            "features": predict_payload,
            "diagnosis": pred_data["diagnosis"],
            "probability": pred_data["probability"],
        }
        explain = client.post("/api/v1/explain/", json=explain_payload)
        assert explain.status_code == 200
        expl_data = explain.json()
        assert len(expl_data["explanation"]) > 0

    def test_optimize_entao_predict(self, client, override_deps):
        optimize = client.post(
            "/api/v1/optimize/",
            json={
                "population_size": 20,
                "generations": 5,
                "mutation_rate": 0.1,
                "crossover_rate": 0.8,
            },
        )
        assert optimize.status_code == 200
        opt_data = optimize.json()
        assert "best_params" in opt_data

        # 2. Predict (independente, apenas verifica se a API ainda funciona)
        predict = client.post(
            "/api/v1/predict/",
            json={
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
            },
        )
        assert predict.status_code == 200

    def test_todos_endpoints_respondem(self, client, override_deps):
        endpoints = [
            ("GET", "/health", None),
            (
                "POST",
                "/api/v1/predict/",
                {
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
                },
            ),
            (
                "POST",
                "/api/v1/predict/top20",
                {
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
                },
            ),
            (
                "POST",
                "/api/v1/optimize/",
                {
                    "population_size": 30,
                    "generations": 10,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.8,
                },
            ),
            (
                "POST",
                "/api/v1/explain/",
                {
                    "features": {"Age (yrs)": 28},
                    "diagnosis": 1,
                    "probability": 0.85,
                },
            ),
        ]
        for method, path, body in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json=body)
            assert (
                response.status_code == 200
            ), f"{method} {path} retornou {response.status_code}"
