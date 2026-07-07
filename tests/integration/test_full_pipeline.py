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


class TestFullPipeline:
    def test_health_entao_predict_entao_explain(self, client, override_deps):
        health = client.get("/health")
        assert health.status_code == 200

        predict = client.post("/api/v1/predict/", json=_VALID_PATIENT)
        assert predict.status_code == 200
        pred_data = predict.json()

        explain = client.post(
            "/api/v1/explain/",
            json={
                "features": {
                    "Age (yrs)": 28,
                    "BMI": 24.5,
                    "AMH(ng/mL)": 4.2,
                    "Cycle(R/I)": 2,
                    "Fast food (Y/N)": 1,
                    "Follicle No. (R)": 8,
                    "Follicle No. (L)": 6,
                    "Skin darkening (Y/N)": 1,
                    "hair growth(Y/N)": 1,
                    "Weight gain(Y/N)": 0,
                    "Pimples(Y/N)": 0,
                    "Hair loss(Y/N)": 0,
                    "Hb(g/dl)": 12.5,
                    "Pulse rate(bpm) ": 72,
                },
                "diagnosis": pred_data["diagnosis"],
                "probability": pred_data["probability"],
            },
        )
        assert explain.status_code == 200
        expl_data = explain.json()
        assert len(expl_data["explanation"]) > 0

    def test_analysis_completo(self, client, override_deps):
        response = client.post("/api/v1/analysis/", json=_VALID_PATIENT)
        assert response.status_code == 200
        data = response.json()
        assert data["diagnosis"] in ("positivo", "negativo")
        assert 0.0 <= data["probability"] <= 1.0
        assert len(data["explanation"]) > 0
        assert len(data["top_contributing_features"]) > 0

    def test_todos_endpoints_respondem(self, client, override_deps):
        endpoints = [
            ("GET", "/health", None),
            ("POST", "/api/v1/predict/", _VALID_PATIENT),
            (
                "POST",
                "/api/v1/explain/",
                {
                    "features": {
                        "Age (yrs)": 28,
                        "BMI": 24.5,
                        "AMH(ng/mL)": 4.2,
                        "Cycle(R/I)": 2,
                        "Fast food (Y/N)": 1,
                        "Follicle No. (R)": 8,
                        "Follicle No. (L)": 6,
                        "Skin darkening (Y/N)": 1,
                        "hair growth(Y/N)": 1,
                        "Weight gain(Y/N)": 0,
                        "Pimples(Y/N)": 0,
                        "Hair loss(Y/N)": 0,
                        "Hb(g/dl)": 12.5,
                        "Pulse rate(bpm) ": 72,
                    },
                    "diagnosis": 1,
                    "probability": 0.85,
                },
            ),
            ("POST", "/api/v1/analysis/", _VALID_PATIENT),
        ]
        for method, path, body in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json=body)
            assert response.status_code == 200, (
                f"{method} {path} retornou {response.status_code}"
            )
