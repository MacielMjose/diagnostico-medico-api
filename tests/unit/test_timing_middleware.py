import time

from fastapi import FastAPI
from starlette.testclient import TestClient

from app.monitoring.middleware import TimingMiddleware


class TestTimingMiddleware:
    def _make_app(self):
        app = FastAPI()
        app.add_middleware(TimingMiddleware)

        @app.get("/fast")
        async def fast():
            return {"ok": True}

        @app.get("/slow")
        async def slow():
            time.sleep(0.05)
            return {"ok": True}

        return app

    def test_middleware_adds_process_time_header(self):
        app = self._make_app()
        client = TestClient(app)
        response = client.get("/fast")
        assert "X-Process-Time" in response.headers

    def test_process_time_is_positive_float(self):
        app = self._make_app()
        client = TestClient(app)
        response = client.get("/fast")
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0

    def test_process_time_increases_with_slower_endpoint(self):
        app = self._make_app()
        client = TestClient(app)
        fast = client.get("/fast")
        slow = client.get("/slow")
        fast_time = float(fast.headers["X-Process-Time"])
        slow_time = float(slow.headers["X-Process-Time"])
        assert slow_time > fast_time

    def test_middleware_does_not_break_response(self):
        app = self._make_app()
        client = TestClient(app)
        response = client.get("/fast")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
