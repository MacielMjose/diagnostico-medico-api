import json
from unittest.mock import AsyncMock, MagicMock, patch

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.domain.models import Explanation, FeatureContribution, PCOSPrediction
from app.infrastructure.llm.base import LLMResponse
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
def dummy_logistic_model():
    rng = np.random.RandomState(42)
    X = rng.randn(100, 5)
    y = rng.randint(0, 2, 100)
    model = LogisticRegression()
    model.fit(X, y)
    return model


@pytest.fixture
def mock_predictor():
    mock = MagicMock()
    mock.predict.return_value = PCOSPrediction(
        diagnosis=1,
        probability=0.85,
        model_version="2.0.0",
        confidence="Alta",
        top_contributing_features=[
            FeatureContribution(feature="AMH", contribution=0.45, direction="positiva"),
            FeatureContribution(feature="IMC", contribution=0.23, direction="positiva"),
        ],
    )
    return mock


@pytest.fixture
def mock_explainer():
    mock = AsyncMock()
    mock.explain.return_value = (
        Explanation(
            text="A paciente apresenta alta probabilidade de SOP. "
            "Os principais fatores de risco incluem ciclo irregular e ganho de peso. "
            "Recomenda-se acompanhamento endocrinológico.",
            risk_factors=[
                "Ciclo menstrual irregular",
                "Ganho de peso",
                "AMH elevado",
            ],
            insights=[
                "Sugerir teste de tolerância à glicose",
                "Avaliar perfil hormonal completo",
                "Recomendar acompanhamento nutricional",
            ],
        ),
        150,
    )
    return mock


@pytest.fixture
def mock_llm_client():
    mock = AsyncMock()
    mock.chat.return_value = LLMResponse(
        text="Com base nos dados, a paciente possui alta probabilidade de SOP. "
        "Fatores como ciclo irregular e ganho de peso são indicadores relevantes.",
        tokens_used=50,
    )
    return mock


@pytest.fixture
def override_deps(app, mock_predictor, mock_explainer):
    from app.core.dependencies import (
        get_explainer,
        get_llm_provider,
        get_model_registry,
        get_predictor,
    )

    app.dependency_overrides[get_predictor] = lambda: mock_predictor
    app.dependency_overrides[get_explainer] = lambda: mock_explainer

    mock_registry = MagicMock()
    mock_registry.load_artifacts.return_value = None
    app.dependency_overrides[get_model_registry] = lambda: mock_registry

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = LLMResponse(
        text="Resposta simulada da LLM.", tokens_used=42
    )
    app.dependency_overrides[get_llm_provider] = lambda: mock_llm

    yield

    app.dependency_overrides.clear()
