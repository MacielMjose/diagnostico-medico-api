import json
from unittest.mock import MagicMock

import pytest

from app.domain.exceptions import LLMRequestError
from app.infrastructure.llm.base import LLMResponse
from app.services.llm_explainer import LLMExplainerService


class TestLLMExplainerService:
    _FEATURES = {"BMI": 27.0, "AMH(ng/mL)": 7.5}

    @pytest.mark.asyncio
    async def test_explain_parses_json_response(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text=json.dumps(
                {
                    "explanation": "Probabilidade elevada de SOP.",
                    "risk_factors": ["obesidade", "hirsutismo"],
                    "insights": ["solicitar perfil hormonal"],
                }
            ),
            tokens_used=100,
        )

        service = LLMExplainerService(provider)
        result, tokens = await service.explain(
            features=self._FEATURES, diagnosis=1, probability=0.87
        )

        assert result.text == "Probabilidade elevada de SOP."
        assert result.risk_factors == ["obesidade", "hirsutismo"]
        assert result.insights == ["solicitar perfil hormonal"]
        assert tokens == 100

    @pytest.mark.asyncio
    async def test_explain_strips_markdown_fences(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text='```json\n{"explanation": "Teste.", "risk_factors": [], "insights": []}\n```',
            tokens_used=None,
        )

        service = LLMExplainerService(provider)
        result, _ = await service.explain(
            features=self._FEATURES, diagnosis=1, probability=0.87
        )

        assert result.text == "Teste."

    @pytest.mark.asyncio
    async def test_explain_raises_on_provider_error(self):
        provider = MagicMock()
        provider.generate.side_effect = RuntimeError("API error")

        service = LLMExplainerService(provider)
        with pytest.raises(LLMRequestError, match="Falha ao gerar explicação via LLM"):
            await service.explain(
                features=self._FEATURES, diagnosis=1, probability=0.87
            )

    @pytest.mark.asyncio
    async def test_explain_raises_on_bad_json(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text="isto não é JSON", tokens_used=None
        )

        service = LLMExplainerService(provider)
        with pytest.raises(LLMRequestError, match="formato inesperado"):
            await service.explain(
                features=self._FEATURES, diagnosis=1, probability=0.87
            )

    def test_build_prompt_contains_features_and_diagnosis(self):
        provider = MagicMock()
        service = LLMExplainerService(provider)

        prompt = service._build_prompt(
            features={"idade": 30, "peso": 70},
            diagnosis=1,
            probability=0.8,
        )

        assert "idade" in prompt
        assert "peso" in prompt
        assert "POSITIVO" in prompt
        assert "80.0%" in prompt

    @pytest.mark.asyncio
    async def test_explain_empty_risk_factors_and_insights(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text=json.dumps(
                {
                    "explanation": "Sem fatores de risco.",
                    "risk_factors": [],
                    "insights": [],
                }
            ),
            tokens_used=50,
        )

        service = LLMExplainerService(provider)
        result, tokens = await service.explain(
            features=self._FEATURES, diagnosis=0, probability=0.12
        )

        assert result.text == "Sem fatores de risco."
        assert result.risk_factors == []
        assert result.insights == []
        assert tokens == 50

    @pytest.mark.asyncio
    async def test_explain_tokens_used_none(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text=json.dumps(
                {
                    "explanation": "Nenhum token.",
                    "risk_factors": [],
                    "insights": [],
                }
            ),
            tokens_used=None,
        )

        service = LLMExplainerService(provider)
        result, tokens = await service.explain(
            features=self._FEATURES, diagnosis=1, probability=0.95
        )

        assert tokens is None

    @pytest.mark.asyncio
    async def test_explain_raises_on_missing_explanation_key(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text=json.dumps({"risk_factors": [], "insights": []}),
            tokens_used=10,
        )

        service = LLMExplainerService(provider)
        with pytest.raises(LLMRequestError, match="formato inesperado"):
            await service.explain(
                features=self._FEATURES, diagnosis=1, probability=0.87
            )

    @pytest.mark.asyncio
    async def test_explain_probability_zero(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text=json.dumps(
                {
                    "explanation": "Risco mínimo.",
                    "risk_factors": [],
                    "insights": [],
                }
            ),
            tokens_used=20,
        )

        service = LLMExplainerService(provider)
        result, _ = await service.explain(
            features=self._FEATURES, diagnosis=0, probability=0.0
        )

        assert result.text == "Risco mínimo."

    @pytest.mark.asyncio
    async def test_explain_probability_one(self):
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            text=json.dumps(
                {
                    "explanation": "Altíssima probabilidade.",
                    "risk_factors": ["obesidade"],
                    "insights": ["urgente"],
                }
            ),
            tokens_used=30,
        )

        service = LLMExplainerService(provider)
        result, _ = await service.explain(
            features=self._FEATURES, diagnosis=1, probability=1.0
        )

        assert result.text == "Altíssima probabilidade."

    def test_build_prompt_with_negative_diagnosis(self):
        provider = MagicMock()
        service = LLMExplainerService(provider)

        prompt = service._build_prompt(
            features={"BMI": 22.0},
            diagnosis=0,
            probability=0.15,
        )

        assert "NEGATIVO para SOP" in prompt
        assert "15.0%" in prompt
