def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_predict_endpoint_returns_500_when_no_model(client):
    response = client.post(
        "/api/v1/predict/",
        json={
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
    )
    assert response.status_code == 503
    assert "Model not loaded" in response.text


def test_predict_validates_input(client):
    response = client.post(
        "/api/v1/predict/",
        json={"invalid": "data"},
    )
    assert response.status_code == 422


def test_optimize_endpoint_returns_200(client):
    response = client.post(
        "/api/v1/optimize/",
        json={
            "population_size": 20,
            "generations": 5,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "best_params" in data
    assert "fitness_history" in data
