# Minha API

Exemplo de API Python com pipeline CI/CD no GitHub Actions.

## Estrutura

```
projeto-python/
├── src/
│   └── minha_api/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── .github/
│   └── workflows/
│       └── pipeline.yml   ← pipeline CI/CD
└── pyproject.toml
```

## Pipeline

| Stage | Quando roda | O que faz |
|---|---|---|
| **lint** | todo push | Ruff: verifica estilo e erros |
| **test** | após lint | pytest com relatório de cobertura |
| **build** | após test | Gera `.whl` e `.tar.gz` |
| **publish** | push na `main` | Publica no PyPI via Trusted Publisher |

## Rodar localmente

```bash
# Entrar na pasta do projeto (onde está o pyproject.toml)
cd projeto-python

pip install -e ".[dev]"

# lint
ruff check .

# testes
pytest --cov=minha_api

# rodar a API
uvicorn minha_api.main:app --reload
```

## Configurar Trusted Publisher no PyPI

1. Acesse https://pypi.org/manage/account/publishing/
2. Adicione o repositório GitHub com o workflow `pipeline.yml`
3. Não é necessário nenhum secret — a autenticação é automática via OIDC
