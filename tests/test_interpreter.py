from unittest.mock import MagicMock, patch

import pytest

from minha_api.schemas import FeatureContribution, PatientData
from minha_api.services.interpreter import _build_user_prompt, _readable_feature, interpret


_PATIENT = PatientData(
    follicle_no_r=12,
    follicle_no_l=10,
    skin_darkening=1,
    hair_growth=1,
    weight_gain=1,
    cycle=4,
    fast_food=1,
    pimples=0,
    amh=7.5,
    bmi=27.0,
    cycle_length=4,
    hair_loss=0,
    age=28,
    hip=40,
    avg_f_size_l=16.0,
    marriage_status=3.0,
    endometrium=9.0,
    avg_f_size_r=17.0,
    pulse_rate=74,
    hb=11.5,
)

_PREDICTION = {
    "diagnosis": True,
    "probability": 0.87,
    "confidence": "Alta",
    "top_contributing_features": [
        FeatureContribution(feature="num__Follicle No. (R)", contribution=1.3, direction="positiva"),
        FeatureContribution(feature="bin__hair growth(Y/N)", contribution=0.58, direction="positiva"),
    ],
    "shap_dict": {},
}


def test_readable_feature_known():
    assert _readable_feature("num__Follicle No. (R)") == "Número de folículos (ovário direito)"


def test_readable_feature_unknown():
    assert _readable_feature("unknown__feature") == "unknown__feature"


def test_build_user_prompt_contains_key_info():
    prompt = _build_user_prompt(_PATIENT, _PREDICTION)
    assert "POSITIVO para SOP" in prompt
    assert "87.0%" in prompt
    assert "Alta" in prompt
    assert "Hirsutismo" in prompt
    assert "Acantose nigricans" in prompt


def test_build_user_prompt_negative():
    neg_prediction = {**_PREDICTION, "diagnosis": False, "probability": 0.12}
    prompt = _build_user_prompt(_PATIENT, neg_prediction)
    assert "NEGATIVO para SOP" in prompt
    assert "12.0%" in prompt


def test_interpret_calls_llm_provider():
    mock_provider = MagicMock()
    mock_provider.generate.return_value = "Interpretação gerada pelo LLM."

    with patch("minha_api.services.interpreter._get_provider", return_value=mock_provider):
        result = interpret(_PATIENT, _PREDICTION)

    assert result == "Interpretação gerada pelo LLM."
    mock_provider.generate.assert_called_once()
    system_prompt, user_prompt = mock_provider.generate.call_args[0]
    assert "SOP" in system_prompt
    assert "POSITIVO" in user_prompt


def test_interpret_graceful_degradation_on_llm_failure():
    mock_provider = MagicMock()
    mock_provider.generate.side_effect = Exception("API timeout")

    with patch("minha_api.services.interpreter._get_provider", return_value=mock_provider):
        result = interpret(_PATIENT, _PREDICTION)

    assert "positivo" in result.lower()
    assert "87.0%" in result
    assert "LLM" in result


def test_factory_raises_for_unknown_provider():
    from minha_api.services.llm.factory import create_llm_provider
    from minha_api.config import settings

    with patch.object(settings, "llm_provider", "gpt99"):
        with pytest.raises(ValueError, match="não suportado"):
            create_llm_provider()


def test_factory_creates_gemini_provider():
    from minha_api.services.llm.factory import create_llm_provider
    from minha_api.services.llm.gemini_provider import GeminiProvider
    from minha_api.config import settings

    with (
        patch.object(settings, "llm_provider", "gemini"),
        patch.object(settings, "gemini_api_key", "fake-key"),
        patch("minha_api.services.llm.gemini_provider.genai.Client"),
    ):
        provider = create_llm_provider()

    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name.startswith("gemini/")
