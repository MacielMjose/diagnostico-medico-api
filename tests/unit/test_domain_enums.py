from app.domain.enums import DiagnosisStatus, ModelType


class TestDiagnosisStatus:
    """Testes para o enum DiagnosisStatus (resultado do diagnóstico)."""

    def test_negative_value(self):
        assert DiagnosisStatus.NEGATIVE.value == 0

    def test_positive_value(self):
        assert DiagnosisStatus.POSITIVE.value == 1

    def test_negative_name(self):
        assert DiagnosisStatus.NEGATIVE.name == "NEGATIVE"

    def test_positive_name(self):
        assert DiagnosisStatus.POSITIVE.name == "POSITIVE"


class TestModelType:
    """Testes para o enum ModelType (tipos de modelo ML)."""

    def test_logistic_regression(self):
        assert ModelType.LOGISTIC_REGRESSION.value == "logistic_regression"

    def test_random_forest(self):
        assert ModelType.RANDOM_FOREST.value == "random_forest"

    def test_xgboost(self):
        assert ModelType.XGBOOST.value == "xgboost"

    def test_all_models_available(self):
        models = list(ModelType)
        assert len(models) == 3
        names = [m.value for m in models]
        assert "logistic_regression" in names
        assert "random_forest" in names
        assert "xgboost" in names
