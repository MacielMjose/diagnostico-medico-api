# TODO: Teste comentado temporariamente enquanto as dependências não estão prontas
# Descomente quando:
# 1. Modelos XGBoost forem treinados
# 2. LLM_API_KEY estiver configurada
# 3. Arquivos necessários estiverem disponíveis



# def _make_dummy_artifacts():
#     pipeline = make_pipeline(StandardScaler(), LogisticRegression())
#     X = np.random.randn(20, 5)
#     y = np.random.randint(0, 2, 20)
#     pipeline.fit(X, y)
#     return {
#         "pipeline": pipeline,
#         "explainer": None,
#         "feature_names": ["f1", "f2", "f3", "f4", "f5"],
#         "top_features": ["f1", "f2", "f3", "f4", "f5"],
#     }


# class TestModelRegistry:
#     """Testes para o ModelRegistry (carregamento do artefato do disco)."""

#     def test_load_artifacts_returns_none_when_not_found(self, tmp_path):
#         registry = ModelRegistry(str(tmp_path / "nonexistent.joblib"))
#         result = registry.load_artifacts()
#         assert result is None

#     def test_load_artifacts_returns_dict_when_found(self, tmp_path):
#         path = tmp_path / "model.joblib"
#         artifacts = _make_dummy_artifacts()
#         joblib.dump(artifacts, path)

#         registry = ModelRegistry(str(path))
#         result = registry.load_artifacts()
#         assert result is not None
#         assert "pipeline" in result
#         assert "feature_names" in result
#         assert "top_features" in result
#         assert hasattr(result["pipeline"], "predict")

#     def test_load_artifacts_caches_result(self, tmp_path):
#         path = tmp_path / "model.joblib"
#         artifacts = _make_dummy_artifacts()
#         joblib.dump(artifacts, path)

#         registry = ModelRegistry(str(path))
#         result1 = registry.load_artifacts()
#         result2 = registry.load_artifacts()
#         assert result1 is result2
