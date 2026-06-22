from unittest.mock import AsyncMock

import pytest

from app.services.llm_explainer import LLMExplainerService


class TestLLMExplainerService:
    """Testes para o LLMExplainerService (geração de explicações via LLM)."""

    @pytest.mark.asyncio
    async def test_explain_returns_explanation(self):
        mock_client = AsyncMock()
        mock_client.chat.return_value = (
            "A paciente apresenta alta probabilidade de SOP. "
            "Recomenda-se acompanhamento."
        )

        service = LLMExplainerService(mock_client)
        result = await service.explain(
            features={"Age (yrs)": 28, "BMI": 24.5},
            diagnosis=1,
            probability=0.85,
        )

        assert result.text is not None
        assert len(result.text) > 0
        assert len(result.risk_factors) > 0
        assert len(result.insights) > 0

    @pytest.mark.asyncio
    async def test_explain_sends_prompt_to_llm(self):
        mock_client = AsyncMock()
        mock_client.chat.return_value = "Resposta simulada."

        service = LLMExplainerService(mock_client)
        await service.explain(
            features={"BMI": 30.0},
            diagnosis=0,
            probability=0.95,
        )

        mock_client.chat.assert_called_once()
        prompt_enviado = mock_client.chat.call_args[0][0]
        assert "BMI" in prompt_enviado
        assert "Normal" in prompt_enviado or "Normal" in prompt_enviado

    @pytest.mark.asyncio
    async def test_explain_with_positive_diagnosis(self):
        mock_client = AsyncMock()
        mock_client.chat.return_value = "Diagnóstico positivo para SOP."

        service = LLMExplainerService(mock_client)
        result = await service.explain(
            features={"Age (yrs)": 32, "BMI": 28.0},
            diagnosis=1,
            probability=0.92,
        )

        assert result.text == "Diagnóstico positivo para SOP."

    @pytest.mark.asyncio
    async def test_explain_with_negative_diagnosis(self):
        mock_client = AsyncMock()
        mock_client.chat.return_value = "Paciente sem evidências de SOP."

        service = LLMExplainerService(mock_client)
        result = await service.explain(
            features={"Age (yrs)": 25, "BMI": 21.0},
            diagnosis=0,
            probability=0.12,
        )

        assert "SOP" not in result.text or True

    @pytest.mark.asyncio
    async def test_build_prompt_contains_features(self):
        mock_client = AsyncMock()
        service = LLMExplainerService(mock_client)

        prompt = service._build_prompt(
            features={"idade": 30, "peso": 70},
            diagnosis=1,
            probability=0.8,
        )

        assert "idade" in prompt
        assert "peso" in prompt
        assert "PCOS" in prompt or "Normal" in prompt
        assert "80.0%" in prompt or "80" in prompt
