from fastapi import FastAPI

app = FastAPI(title="Minha API", version="0.1.0", docs_url="/swagger")


@app.get("/")
def root():
    return {"status": "ok", "message": "API funcionando!"}


@app.get("/health")
def health():
    return {"status": "healthy"}
