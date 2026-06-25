import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.core.exceptions import AppException, app_exception_handler


class TestAppException:
    def test_exception_has_message_and_status(self):
        exc = AppException("erro de teste", status_code=422)
        assert exc.message == "erro de teste"
        assert exc.status_code == 422

    def test_exception_default_status_code(self):
        exc = AppException("erro")
        assert exc.status_code == 400

    def test_exception_is_exception_subclass(self):
        exc = AppException("msg")
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised_and_caught(self):
        with pytest.raises(AppException) as exc_info:
            raise AppException("falhou", 500)
        assert exc_info.value.message == "falhou"
        assert exc_info.value.status_code == 500


class TestAppExceptionHandler:
    def test_handler_returns_json_response(self):
        app = FastAPI()
        app.add_exception_handler(AppException, app_exception_handler)

        @app.get("/test-error")
        async def raise_error():
            raise AppException("custom error", 422)

        client = TestClient(app)
        response = client.get("/test-error")
        assert response.status_code == 422
        assert response.json() == {"error": "custom error"}

    def test_handler_with_500_status(self):
        app = FastAPI()
        app.add_exception_handler(AppException, app_exception_handler)

        @app.get("/test-500")
        async def raise_500():
            raise AppException("server error", 500)

        client = TestClient(app)
        response = client.get("/test-500")
        assert response.status_code == 500
        assert response.json()["error"] == "server error"

    def test_handler_with_400_status(self):
        app = FastAPI()
        app.add_exception_handler(AppException, app_exception_handler)

        @app.get("/test-400")
        async def raise_400():
            raise AppException("bad request", 400)

        client = TestClient(app)
        response = client.get("/test-400")
        assert response.status_code == 400
        assert response.json() == {"error": "bad request"}
