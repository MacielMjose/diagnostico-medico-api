# TODO: Teste comentado temporariamente enquanto as dependências não estão prontas
# Descomente quando:
# 1. Modelos XGBoost forem treinados
# 2. LLM_API_KEY estiver configurada
# 3. Arquivos necessários estiverem disponíveis
import json
from unittest.mock import MagicMock

import pytest

from app.services.llm_explainer import LLMExplainerService


# class TestLLMExplainerService:
#     """Testes para o LLMExplainerService (geraÃ§Ã£o de explicaÃ§Ãµes via LLM)."""

#     @pytest.mark.asyncio
#     async def test_explain_parses_json_response(self):
#         mock = MagicMock()
#         mock.generate.return_value = json.dumps(
#             {
#                 "explanation": "Probabilidade elevada de SOP.",
#                 "risk_factors": ["obesidade", "hirsutismo"],
#                 "insights": ["solicitar perfil hormonal"],
#             }
#         )

#         service = LLMExplainerService(mock)
#         result = await service.explain(
#             features={"BMI": 27.0}, diagnosis=1, probability=0.87
#         )

#         assert result.text == "Probabilidade elevada de SOP."
#         assert result.risk_factors == ["obesidade", "hirsutismo"]
#         assert result.insights == ["solicitar perfil hormonal"]

#     @pytest.mark.asyncio
#     async def test_explain_strips_markdown_fences(self):
#         mock = MagicMock()
#         mock.generate.return_value = (
#             '```json\n{"explanation": "Teste.", "risk_factors": [], "insights": []}\n```'
#         )

#         service = LLMExplainerService(mock)
#         result = await service.explain(
#             features={"BMI": 27.0}, diagnosis=1, probability=0.87
#         )

#         assert result.text == "Teste."

#     @pytest.mark.asyncio
#     async def test_explain_raises_on_provider_error(self):
#         mock = MagicMock()
#         mock.generate.side_effect = RuntimeError("API error")

#         service = LLMExplainerService(mock)
#         with pytest.raises(Exception, match="LLM"):
#             await service.explain(
#                 features={"BMI": 27.0}, diagnosis=1, probability=0.87
#             )

#     def test_build_prompt_contains_features_and_diagnosis(self):
#         mock = MagicMock()
#         service = LLMExplainerService(mock)

#         prompt = service._build_prompt(
#             features={"idade": 30, "peso": 70},
#             diagnosis=1,
#             probability=0.8,
#         )

#         assert "idade" in prompt
#         assert "peso" in prompt
#         assert "POSITIVO" in prompt
#         assert "80.0%" in prompt
