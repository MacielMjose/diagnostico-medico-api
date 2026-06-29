import json
from unittest.mock import AsyncMock, MagicMock, patch

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.domain.models import Explanation, OptimizationResult, PCOSPrediction
from app.main import create_app


@pytest.fixture(autouse=True)
def mock_aws_and_posthog():
    with patch(
        "app.infrastructure.secrets_manager.get_secret_or_env",
        return_value="test_api_key",
    ):
        with patch("app.monitoring.posthog.get_posthog_client", return_value=None):
            with patch("app.monitoring.posthog.capture_event"):
                with patch("app.monitoring.posthog.capture_request"):
                    with patch("app.monitoring.posthog.capture_prediction"):
                        with patch("app.monitoring.posthog.capture_llm_request"):
                            yield


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def dummy_model_path(tmp_path):
    path = tmp_path / "models"
    path.mkdir()
    return path


@pytest.fixture
def dummy_pipeline():
    pipeline = make_pipeline(StandardScaler(), LogisticRegression())
    X = np.random.randn(100, 10)
    y = np.random.randint(0, 2, 100)
    pipeline.fit(X, y)
    return pipeline


@pytest.fixture
def save_dummy_pipeline(dummy_model_path, dummy_pipeline):
    def _save(name):
        filepath = dummy_model_path / f"{name}.pkl"
        joblib.dump(dummy_pipeline, filepath)
        return filepath

    return _save


@pytest.fixture
def dummy_features_top20(dummy_model_path):
    path = dummy_model_path / "selected_features.json"
    features = ["Age (yrs)", "BMI", "Follicle No. (R)"]
    with open(path, "w") as f:
        json.dump(features, f)
    return features


@pytest.fixture
def mock_predictor():
    mock = MagicMock()
    mock.predict.return_value = PCOSPrediction(
        diagnosis=1, probability=0.85, model_version="1.0.0"
    )
    return mock


@pytest.fixture
def mock_optimizer():
    mock = MagicMock()
    mock.run.return_value = OptimizationResult(
        best_params={"learning_rate": 0.05, "max_depth": 6},
        fitness_history=[0.75, 0.80, 0.85, 0.88, 0.90],
        comparison={
            "original_accuracy": 0.82,
            "optimized_accuracy": 0.90,
            "improvement": "+9.8%",
        },
    )
    return mock


@pytest.fixture
def mock_explainer():
    mock = AsyncMock()
    mock.explain.return_value = Explanation(
        text="A paciente apresenta alta probabilidade de SOP. "
        "Os principais fatores de risco incluem ciclo irregular e ganho de peso. "
        "Recomenda-se acompanhamento endocrinológico.",
        risk_factors=[
            "Ciclo menstrual irregular (Cycle(R/I)=2)",
            "Ganho de peso (Weight gain(Y/N)=1)",
            "AMH elevado (AMH(ng/mL)=4.2)",
        ],
        insights=[
            "Sugerir teste de tolerância à glicose",
            "Avaliar perfil hormonal completo",
            "Recomendar acompanhamento nutricional",
        ],
    )
    return mock


@pytest.fixture
def mock_llm_client():
    mock = AsyncMock()
    mock.chat.return_value = (
        "Com base nos dados, a paciente possui alta probabilidade de SOP. "
        "Fatores como ciclo irregular e ganho de peso são indicadores relevantes."
    )
    return mock


@pytest.fixture
def override_deps(app, mock_predictor, mock_optimizer, mock_explainer):
    from app.core.dependencies import (
        get_explainer,
        get_llm_provider,
        get_model_registry,
        get_optimizer,
        get_predictor,
    )

    app.dependency_overrides[get_predictor] = lambda: mock_predictor
    app.dependency_overrides[get_optimizer] = lambda: mock_optimizer
    app.dependency_overrides[get_explainer] = lambda: mock_explainer

    mock_registry = MagicMock()
    mock_registry.load_artifacts.return_value = None
    app.dependency_overrides[get_model_registry] = lambda: mock_registry

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Resposta simulada da LLM."
    app.dependency_overrides[get_llm_provider] = lambda: mock_llm

    yield

    app.dependency_overrides.clear()
