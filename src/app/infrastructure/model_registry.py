from functools import lru_cache
from pathlib import Path

import joblib
import structlog
from sklearn.linear_model import LogisticRegression

logger = structlog.get_logger()


class ModelRegistry:
    """Carrega o modelo de classificação de PCOS.

    O artefato é o próprio estimador scikit-learn (``LogisticRegression``),
    treinado diretamente sobre as features brutas (mesmas colunas de
    ``FEATURE_COLUMN_MAP``, sem pipeline de pré-processamento e sem
    explainer SHAP embutido).
    """

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)

    @lru_cache(maxsize=1)
    def load_artifacts(self) -> LogisticRegression | None:
        logger.info("model_loading", path=str(self.model_path))

        if not self.model_path.exists():
            logger.error(
                "model_load_failed", path=str(self.model_path), reason="file_not_found"
            )
            return None

        model = joblib.load(self.model_path)
        logger.info(
            "model_loaded",
            path=str(self.model_path),
            model_type=type(model).__name__,
            n_features=getattr(model, "n_features_in_", None),
        )
        return model
