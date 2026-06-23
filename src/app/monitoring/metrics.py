from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator().instrument()


def setup_metrics(app):
    instrumentator.expose(app)
