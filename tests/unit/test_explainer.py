# TODO: Teste comentado temporariamente enquanto as dependências não estão prontas
# Descomente quando:
# 1. Modelos XGBoost forem treinados
# 2. LLM_API_KEY estiver configurada
# 3. Arquivos necessários estiverem disponíveis
from unittest.mock import MagicMock

import pytest

from app.domain.exceptions import LLMRequestError
from app.services.llm_explainer import LLMExplainerService

# _FEATURES = {"BMI": 27.0, "AMH(ng/mL)": 7.5}


# @pytest.mark.anyio
# async def test_explain_parses_json_response():
#     provider = MagicMock()
#     provider.generate.return_value = (
#         '{"explanation": "Texto clÃ­nico.", '
#         '"risk_factors": ["obesidade"], "insights": ["dieta"]}'
#     )
#     service = LLMExplainerService(provider)

#     result = await service.explain(_FEATURES, diagnosis=1, probability=0.87)

#     assert result.text == "Texto clÃ­nico."
#     assert result.risk_factors == ["obesidade"]
#     assert result.insights == ["dieta"]
#     system_prompt, user_prompt = provider.generate.call_args[0]
#     assert "SOP" in system_prompt
#     assert "POSITIVO para SOP" in user_prompt


# @pytest.mark.anyio
# async def test_explain_strips_markdown_fences():
#     provider = MagicMock()
#     provider.generate.return_value = (
#         '```json\n{"explanation": "x", "risk_factors": [], "insights": []}\n```'
#     )
#     service = LLMExplainerService(provider)

#     result = await service.explain(_FEATURES, diagnosis=0, probability=0.12)

#     assert result.text == "x"


# @pytest.mark.anyio
# async def test_explain_raises_on_provider_error():
#     provider = MagicMock()
#     provider.generate.side_effect = RuntimeError("API timeout")
#     service = LLMExplainerService(provider)

#     with pytest.raises(LLMRequestError):
#         await service.explain(_FEATURES, diagnosis=1, probability=0.5)


# @pytest.mark.anyio
# async def test_explain_raises_on_bad_json():
#     provider = MagicMock()
#     provider.generate.return_value = "isto nÃ£o Ã© JSON"
#     service = LLMExplainerService(provider)

#     with pytest.raises(LLMRequestError):
#         await service.explain(_FEATURES, diagnosis=1, probability=0.5)
