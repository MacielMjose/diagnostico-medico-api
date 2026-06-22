import json
from functools import lru_cache
from pathlib import Path

import joblib


class ModelRegistry:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)

    @lru_cache(maxsize=5)
    def load_pipeline(self, name: str):
        path = self.model_path / f"{name}.pkl"
        if not path.exists():
            return None
        return joblib.load(path)

    def load_features_top20(self) -> list:
        path = self.model_path / "selected_features.json"
        if not path.exists():
            return []
        with open(path) as f:
            return json.load(f)

    def list_available(self) -> list:
        return [p.stem for p in self.model_path.glob("*.pkl")]
