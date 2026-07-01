"""
Treina o modelo de diagnóstico de SOP e salva os artefatos em models/pcos_model.joblib.

Requer dependências do grupo [training]:
    pip install -e ".[training]"

Requer credenciais Kaggle configuradas (KAGGLE_USERNAME + KAGGLE_KEY ou ~/.kaggle/kaggle.json).
"""

import os
import pathlib

import joblib
import kagglehub
import pandas as pd
import shap
import structlog
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logger = structlog.get_logger()

RANDOM_STATE = 42
N_TOP_FEATURES = 20
OUTPUT_PATH = pathlib.Path("models/pcos_model.joblib")

BINARY_COLS_REF = [
    "Pregnant(Y/N)",
    "Weight gain(Y/N)",
    "hair growth(Y/N)",
    "Skin darkening (Y/N)",
    "Hair loss(Y/N)",
    "Pimples(Y/N)",
    "Fast food (Y/N)",
    "Reg.Exercise(Y/N)",
    "Blood Group_12",
    "Blood Group_13",
    "Blood Group_14",
    "Blood Group_15",
    "Blood Group_16",
    "Blood Group_17",
    "Blood Group_18",
]


def load_and_clean() -> pd.DataFrame:
    logger.info("dataset_download_started")
    path = kagglehub.dataset_download(
        "prasoonkottarathil/polycystic-ovary-syndrome-pcos"
    )
    df = pd.read_excel(
        os.path.join(path, "PCOS_data_without_infertility.xlsx"),
        sheet_name="Full_new",
    )
    logger.info("dataset_loaded", original_shape=df.shape)

    df.drop(columns=["Unnamed: 44"], inplace=True, errors="ignore")
    df.drop(columns=["Sl. No", "Patient File No."], inplace=True, errors="ignore")

    df["Marraige Status (Yrs)"] = df["Marraige Status (Yrs)"].fillna(
        df["Marraige Status (Yrs)"].mean()
    )
    moda_ff = int(df["Fast food (Y/N)"].mode()[0])
    df["Fast food (Y/N)"] = df["Fast food (Y/N)"].fillna(moda_ff)

    for col in ["II    beta-HCG(mIU/mL)", "AMH(ng/mL)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    df = pd.get_dummies(df, columns=["Blood Group"], drop_first=True, dtype=int)

    # Remove features redundantes por alta correlação (>0.8)
    df.drop(
        columns=["Weight (Kg)", "FSH(mIU/mL)", "Waist(inch)"],
        inplace=True,
        errors="ignore",
    )

    assert df.isnull().sum().sum() == 0, "Valores nulos remanescentes!"
    logger.info("dataset_cleaned", cleaned_shape=df.shape)
    return df


def select_top_features(df: pd.DataFrame) -> list[str]:
    corr = df.corr(numeric_only=True)["PCOS (Y/N)"].abs()
    top = (
        corr.drop("PCOS (Y/N)")
        .sort_values(ascending=False)
        .head(N_TOP_FEATURES)
        .index.tolist()
    )
    logger.info("top_features_selected", top_features=top)
    return top


def build_pipeline(top_features: list[str]) -> ColumnTransformer:
    binary_cols = [c for c in top_features if c in BINARY_COLS_REF]
    num_cols = [c for c in top_features if c not in BINARY_COLS_REF]

    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    return ColumnTransformer(
        [
            ("num", num_pipeline, num_cols),
            ("bin", "passthrough", binary_cols),
        ]
    )


def train(df: pd.DataFrame, top_features: list[str]) -> dict:
    X = df[top_features]
    y = df["PCOS (Y/N)"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    preprocessor = build_pipeline(top_features)

    pipe = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    pipe.fit(X_train, y_train)

    # Avaliação rápida
    from sklearn.metrics import roc_auc_score

    y_proba = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    logger.info("model_trained", auc_roc_test=round(auc, 4))

    # SHAP — LinearExplainer com dados de treino transformados
    x_train_transformed = pipe.named_steps["preprocessor"].transform(X_train)
    feature_names = pipe.named_steps["preprocessor"].get_feature_names_out().tolist()

    explainer = shap.LinearExplainer(
        pipe.named_steps["model"],
        x_train_transformed,
        feature_names=feature_names,
    )

    return {
        "pipeline": pipe,
        "explainer": explainer,
        "feature_names": feature_names,
        "top_features": top_features,
        "auc_test": auc,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = load_and_clean()
    top_features = select_top_features(df)
    artifacts = train(df, top_features)

    joblib.dump(artifacts, OUTPUT_PATH)
    logger.info("artifacts_saved", path=str(OUTPUT_PATH))
    logger.info("training_completed")


if __name__ == "__main__":
    main()
