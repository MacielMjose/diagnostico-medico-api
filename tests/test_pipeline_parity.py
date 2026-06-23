"""
Verifica que o caminho da API (PatientData → to_dataframe_row → predict)
produz a mesma probabilidade que chamar pipeline.predict_proba() diretamente.

Não depende do Kaggle nem do modelo treinado — gera um dataset sintético,
treina um pipeline idêntico ao de produção e compara os dois caminhos.
"""

import shap
import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from unittest.mock import patch

from minha_api.schemas import FEATURE_COLUMN_MAP, PatientData

# Top 20 features na mesma ordem do notebook
TOP_FEATURES = [
    "Follicle No. (R)",
    "Follicle No. (L)",
    "Skin darkening (Y/N)",
    "hair growth(Y/N)",
    "Weight gain(Y/N)",
    "Cycle(R/I)",
    "Fast food (Y/N)",
    "Pimples(Y/N)",
    "AMH(ng/mL)",
    "BMI",
    "Cycle length(days)",
    "Hair loss(Y/N)",
    " Age (yrs)",
    "Hip(inch)",
    "Avg. F size (L) (mm)",
    "Marraige Status (Yrs)",
    "Endometrium (mm)",
    "Avg. F size (R) (mm)",
    "Pulse rate(bpm) ",
    "Hb(g/dl)",
]

BINARY_COLS = [
    "Skin darkening (Y/N)",
    "hair growth(Y/N)",
    "Weight gain(Y/N)",
    "Fast food (Y/N)",
    "Pimples(Y/N)",
    "Hair loss(Y/N)",
]
NUM_COLS = [c for c in TOP_FEATURES if c not in BINARY_COLS]

COL_TO_FIELD = {v: k for k, v in FEATURE_COLUMN_MAP.items()}


def _make_synthetic_dataset(n: int = 100, seed: int = 0) -> pd.DataFrame:
    """Gera dataset sintético com ranges clínicos realistas."""
    rng = np.random.default_rng(seed)
    col_ranges = {
        "Follicle No. (R)":      (1, 20),
        "Follicle No. (L)":      (1, 20),
        "Cycle(R/I)":            (2, 4),
        "AMH(ng/mL)":            (0.5, 15),
        "BMI":                   (18, 40),
        "Cycle length(days)":    (2, 8),
        " Age (yrs)":            (18, 45),
        "Hip(inch)":             (30, 55),
        "Avg. F size (L) (mm)":  (10, 25),
        "Marraige Status (Yrs)": (0, 20),
        "Endometrium (mm)":      (4, 15),
        "Avg. F size (R) (mm)":  (10, 25),
        "Pulse rate(bpm) ":      (55, 100),
        "Hb(g/dl)":              (9, 15),
    }
    data = {col: rng.uniform(lo, hi, n) for col, (lo, hi) in col_ranges.items()}
    for col in BINARY_COLS:
        data[col] = rng.integers(0, 2, n)
    return pd.DataFrame(data)


def _build_pipeline() -> Pipeline:
    num_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    preprocessor = ColumnTransformer([
        ("num", num_pipe, NUM_COLS),
        ("bin", "passthrough", BINARY_COLS),
    ])
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=500, class_weight="balanced")),
        ],
        memory=None,
    )


def _row_to_patient(row: pd.Series) -> PatientData:
    return PatientData(**{COL_TO_FIELD[col]: float(row[col]) for col in TOP_FEATURES})


@pytest.fixture(scope="module")
def trained_artifacts():
    rng = np.random.default_rng(0)
    x_train = _make_synthetic_dataset(n=120)
    y_train = rng.integers(0, 2, len(x_train))

    pipeline = _build_pipeline()
    pipeline.fit(x_train, y_train)

    feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out().tolist()

    x_train_transformed = pipeline.named_steps["preprocessor"].transform(x_train)
    explainer = shap.LinearExplainer(
        pipeline.named_steps["model"],
        x_train_transformed,
        feature_names=feature_names,
    )

    return {
        "pipeline": pipeline,
        "explainer": explainer,
        "feature_names": feature_names,
        "top_features": TOP_FEATURES,
    }


def test_api_path_matches_direct_pipeline(trained_artifacts):
    """
    Para 10 linhas sintéticas, compara:
      A) pipeline.predict_proba(linha) — abordagem direta (notebook)
      B) PatientData → to_dataframe_row() → predict() — abordagem API

    As probabilidades devem ser idênticas (diferença < 1e-6).
    """
    x_sample = _make_synthetic_dataset(n=10, seed=99)

    from minha_api.models.pcos_classifier import _load_artifacts, predict

    _load_artifacts.cache_clear()

    with patch(
        "minha_api.models.pcos_classifier._load_artifacts",
        return_value=trained_artifacts,
    ):
        _load_artifacts.cache_clear()

        for _, row in x_sample.iterrows():
            # Caminho A: direto pelo pipeline (como o notebook faz)
            notebook_prob = float(
                trained_artifacts["pipeline"].predict_proba(
                    pd.DataFrame([row])[TOP_FEATURES]
                )[0, 1]
            )

            # Caminho B: via PatientData + mapeamento de campos (como a API faz)
            patient = _row_to_patient(row)
            api_result = predict(patient.to_dataframe_row())
            api_prob = api_result["probability"]

            # predict() arredonda para 4 casas decimais — comparamos após o mesmo arredondamento
            assert abs(round(notebook_prob, 4) - api_prob) < 1e-6, (
                f"Divergência detectada: notebook={notebook_prob:.8f} "
                f"(arredondado={round(notebook_prob, 4)}), "
                f"api={api_prob:.8f}, delta={abs(round(notebook_prob, 4) - api_prob):.2e}"
            )


def test_column_map_is_complete():
    """Todas as Top 20 features têm mapeamento em FEATURE_COLUMN_MAP."""
    mapped_cols = set(FEATURE_COLUMN_MAP.values())
    for col in TOP_FEATURES:
        assert col in mapped_cols, f"Coluna '{col}' não tem mapeamento em FEATURE_COLUMN_MAP"


def test_column_map_has_no_duplicates():
    """Não pode haver dois campos apontando para a mesma coluna."""
    cols = list(FEATURE_COLUMN_MAP.values())
    assert len(cols) == len(set(cols)), "FEATURE_COLUMN_MAP tem colunas duplicadas"
