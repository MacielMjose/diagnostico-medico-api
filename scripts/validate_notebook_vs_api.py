"""
Valida que as predições da API batem com as predições diretas pelo pipeline
(equivalente ao que o notebook faz).

Pré-requisito: modelo já treinado.
    python scripts/train_model.py

Execução:
    python scripts/validate_notebook_vs_api.py

O que é validado
─────────────────
Para cada linha do dataset original:
  1. "Caminho notebook" → pipeline.predict_proba(linha_bruta)
  2. "Caminho API"      → converte para PatientData → to_dataframe_row() → predict()

Se os dois caminhos produzirem a mesma probabilidade (diferença < 1e-6),
o mapeamento de campos e o pipeline estão corretos.
"""

import os
import pathlib
import sys

# Permite importar o pacote app sem instalar
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import joblib
import kagglehub
import pandas as pd

from app.domain.features import FEATURE_COLUMN_MAP
from app.infrastructure.model_registry import ModelRegistry
from app.services.predictor import PredictorService

MODEL_PATH = pathlib.Path("models/pcos_model.joblib")

# Mapeamento inverso: nome de coluna do dataset → campo do PatientData
COLUMN_TO_FIELD = {col: field for field, col in FEATURE_COLUMN_MAP.items()}


def load_dataset() -> pd.DataFrame:
    print("Baixando dataset do Kaggle...")
    path = kagglehub.dataset_download(
        "prasoonkottarathil/polycystic-ovary-syndrome-pcos"
    )
    df = pd.read_excel(
        os.path.join(path, "PCOS_data_without_infertility.xlsx"),
        sheet_name="Full_new",
    )

    # Mesma limpeza do train_model.py
    df.drop(
        columns=["Unnamed: 44", "Sl. No", "Patient File No."],
        inplace=True,
        errors="ignore",
    )
    df["Marraige Status (Yrs)"] = df["Marraige Status (Yrs)"].fillna(
        df["Marraige Status (Yrs)"].mean()
    )
    moda_ff = int(df["Fast food (Y/N)"].mode()[0])
    df["Fast food (Y/N)"] = df["Fast food (Y/N)"].fillna(moda_ff)
    for col in ["II    beta-HCG(mIU/mL)", "AMH(ng/mL)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())
    df = pd.get_dummies(df, columns=["Blood Group"], drop_first=True, dtype=int)
    df.drop(
        columns=["Weight (Kg)", "FSH(mIU/mL)", "Waist(inch)"],
        inplace=True,
        errors="ignore",
    )

    return df


def row_to_features(row: pd.Series, top_features: list[str]) -> dict[str, float]:
    """Converte uma linha do dataset no dict de features que a API receberia."""
    fields = {}
    for col in top_features:
        field_name = COLUMN_TO_FIELD.get(col)
        if field_name is None:
            raise KeyError(f"Coluna '{col}' não tem mapeamento em FEATURE_COLUMN_MAP")
        fields[field_name] = float(row[col])
    return fields


def validate(n_samples: int = 20) -> None:
    if not MODEL_PATH.exists():
        print(f"ERRO: modelo não encontrado em '{MODEL_PATH}'.")
        print("Execute primeiro: python scripts/train_model.py")
        sys.exit(1)

    artifacts = joblib.load(MODEL_PATH)
    pipeline = artifacts["pipeline"]
    top_features: list[str] = artifacts["top_features"]

    predictor = PredictorService(ModelRegistry(str(MODEL_PATH)))

    df = load_dataset()

    # Usa uma amostra aleatória fixada para reprodutibilidade
    sample = (
        df[top_features + ["PCOS (Y/N)"]].dropna().sample(n=n_samples, random_state=42)
    )

    print(f"\nComparando {n_samples} linhas — notebook pipeline vs API predict()\n")
    print(
        "Nota: a API arredonda para 4 casas decimais — comparação usa round(notebook, 4).\n"
    )
    print(
        f"{'#':>3}  {'Real':>5}  {'Notebook':>10}  {'Rounded':>10}  {'API':>10}  {'Δ':>9}  Status"
    )
    print("─" * 68)

    mismatches = 0
    for i, (idx, row) in enumerate(sample.iterrows(), start=1):
        real_label = int(row["PCOS (Y/N)"])

        # ── Caminho 1: direto pelo pipeline (como o notebook faz) ──────────
        notebook_prob = float(
            pipeline.predict_proba(pd.DataFrame([row])[top_features])[0, 1]
        )
        notebook_rounded = round(notebook_prob, 4)

        # ── Caminho 2: via API (features → PredictorService.predict) ──────
        features = row_to_features(row, top_features)
        api_result = predictor.predict(features)
        api_prob = api_result.probability

        # Compara após o mesmo arredondamento que o predict() aplica internamente
        delta = abs(notebook_rounded - api_prob)
        status = "OK" if delta < 1e-6 else f"DIVERGIU ({delta:.2e})"
        if delta >= 1e-6:
            mismatches += 1

        print(
            f"{i:>3}  {real_label:>5}  {notebook_prob:>10.6f}  {notebook_rounded:>10.4f}"
            f"  {api_prob:>10.4f}  {delta:>9.2e}  {status}"
        )

    print("─" * 60)
    if mismatches == 0:
        print(f"\nRESULTADO: todos os {n_samples} casos batem perfeitamente.")
    else:
        print(
            f"\nRESULTADO: {mismatches} caso(s) com divergência — verifique o mapeamento de colunas."
        )
        sys.exit(1)

    # ── Métricas agregadas da amostra ─────────────────────────────────────
    print("\nMétricas na amostra:")
    y_true = sample["PCOS (Y/N)"].astype(int).tolist()
    y_pred_notebook = [
        int(pipeline.predict_proba(pd.DataFrame([row])[top_features])[0, 1] >= 0.5)
        for _, row in sample.iterrows()
    ]
    acertos = sum(p == r for p, r in zip(y_pred_notebook, y_true))
    print(
        f"  Acurácia na amostra ({n_samples} casos): {acertos}/{n_samples} = {acertos / n_samples:.1%}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Valida notebook vs API")
    parser.add_argument(
        "--n", type=int, default=20, help="Número de linhas a comparar (padrão: 20)"
    )
    args = parser.parse_args()
    validate(n_samples=args.n)
