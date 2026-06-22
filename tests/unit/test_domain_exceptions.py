import pytest

from app.domain.exceptions import (
    InvalidFeaturesError,
    LLMRequestError,
    ModelNotLoadedError,
)


class TestModelNotLoadedError:
    """Testes para a exceção ModelNotLoadedError."""

    def test_exception_is_raised(self):
        with pytest.raises(ModelNotLoadedError):
            raise ModelNotLoadedError("Modelo não encontrado")

    def test_exception_message(self):
        with pytest.raises(ModelNotLoadedError) as exc_info:
            raise ModelNotLoadedError("Modelo XGBoost não carregado")
        assert "XGBoost" in str(exc_info.value)


class TestInvalidFeaturesError:
    """Testes para a exceção InvalidFeaturesError."""

    def test_exception_is_raised(self):
        with pytest.raises(InvalidFeaturesError):
            raise InvalidFeaturesError("Features inválidas")

    def test_exception_message(self):
        with pytest.raises(InvalidFeaturesError) as exc_info:
            raise InvalidFeaturesError("Campo 'age' é obrigatório")
        assert "age" in str(exc_info.value)


class TestLLMRequestError:
    """Testes para a exceção LLMRequestError."""

    def test_exception_is_raised(self):
        with pytest.raises(LLMRequestError):
            raise LLMRequestError("Erro na requisição LLM")

    def test_exception_message(self):
        with pytest.raises(LLMRequestError) as exc_info:
            raise LLMRequestError("API key inválida")
        assert "API key" in str(exc_info.value)
