from functools import lru_cache
from pathlib import Path

import joblib
import structlog

logger = structlog.get_logger()


class ModelRegistry:
    """Carrega o artefato serializado do modelo PCOS.

    O artefato é um dict com as chaves:
      - ``pipeline``: sklearn Pipeline (preprocessor + model)
      - ``explainer``: SHAP explainer ajustado ao espaço transformado
      - ``feature_names``: nomes das colunas após o pré-processamento
      - ``top_features``: colunas originais esperadas como entrada
    """

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)

    @lru_cache(maxsize=1)
    def load_artifacts(self) -> dict | None:
        logger.info("model_loading", path=str(self.model_path))

        if not self.model_path.exists():
            logger.error("model_load_failed", path=str(self.model_path), reason="file_not_found")
            return None

        artifact = joblib.load(self.model_path)
        logger.info(
            "model_loaded",
            path=str(self.model_path),
            artifact_keys=list(artifact.keys()),
        )
        return artifact
