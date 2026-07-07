from app.domain.models import Explanation, PCOSPrediction


class TestPCOSPrediction:
    """Testes para o modelo PCOSPrediction (resultado da predição)."""

    def test_create_prediction_positive(self):
        pred = PCOSPrediction(diagnosis=1, probability=0.85, model_version="1.0.0")
        assert pred.diagnosis == 1
        assert pred.probability == 0.85
        assert pred.model_version == "1.0.0"

    def test_create_prediction_negative(self):
        pred = PCOSPrediction(diagnosis=0, probability=0.15, model_version="1.0.0")
        assert pred.diagnosis == 0
        assert pred.probability == 0.15

    def test_prediction_diagnosis_is_int(self):
        pred = PCOSPrediction(diagnosis=1, probability=0.9, model_version="1.0.0")
        assert isinstance(pred.diagnosis, int)

    def test_prediction_probability_is_float(self):
        pred = PCOSPrediction(diagnosis=0, probability=0.5, model_version="1.0.0")
        assert isinstance(pred.probability, float)

    def test_prediction_edge_probabilities(self):
        pred_min = PCOSPrediction(diagnosis=0, probability=0.0, model_version="1.0.0")
        pred_max = PCOSPrediction(diagnosis=1, probability=1.0, model_version="1.0.0")
        assert 0.0 <= pred_min.probability <= 1.0
        assert 0.0 <= pred_max.probability <= 1.0


class TestExplanation:
    """Testes para o modelo Explanation (explicação gerada por LLM)."""

    def test_create_explanation(self):
        expl = Explanation(
            text="Diagnóstico positivo para SOP.",
            risk_factors=["Obesidade", "Ciclo irregular"],
            insights=["Buscar endocrinologista"],
        )
        assert "SOP" in expl.text
        assert len(expl.risk_factors) == 2
        assert len(expl.insights) == 1

    def test_empty_risk_factors(self):
        expl = Explanation(text="Normal", risk_factors=[], insights=[])
        assert expl.risk_factors == []
        assert expl.insights == []

    def test_multiple_insights(self):
        expl = Explanation(
            text="Recomendações:",
            risk_factors=["Fator A"],
            insights=["Insight 1", "Insight 2", "Insight 3"],
        )
        assert len(expl.insights) == 3
