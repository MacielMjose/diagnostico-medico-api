import json

import anyio
import structlog

from app.domain.exceptions import LLMRequestError
from app.domain.features import readable_feature
from app.domain.models import Explanation
from app.infrastructure.llm.base import LLMProvider, LLMResponse

logger = structlog.get_logger()

_SYSTEM_PROMPT = (
    "Você é um assistente clínico especializado em endocrinologia reprodutiva "
    "e Síndrome dos Ovários Policísticos (SOP/PCOS). Seu papel é interpretar "
    "resultados de modelos de machine learning e traduzi-los em linguagem "
    "clínica clara e acionável para médicos especialistas.\n\n"
    "Diretrizes obrigatórias:\n"
    "- Use terminologia médica precisa e português do Brasil.\n"
    "- Baseie-se exclusivamente nos dados fornecidos — não especule.\n"
    "- Apresente o diagnóstico como probabilidade — nunca como certeza absoluta.\n"
    "- Ressalte que o modelo é ferramenta de triagem, não substitui avaliação "
    "especializada.\n\n"
    "Responda EXCLUSIVAMENTE com um objeto JSON válido, sem texto antes ou "
    "depois, no formato:\n"
    "{\n"
    '  "explanation": "Interpretação clínica em 2-3 parágrafos curtos (máx. 250 '
    'palavras): resultado, fatores determinantes e próximos passos clínicos.",\n'
    '  "risk_factors": ["fator de risco 1", "fator de risco 2"],\n'
    '  "insights": ["recomendação acionável 1", "recomendação acionável 2"]\n'
    "}"
)


class LLMExplainerService:
    def __init__(self, client: LLMProvider):
        self.client = client

    def _build_prompt(self, features: dict, diagnosis: int, probability: float) -> str:
        diagnosis_str = "POSITIVO para SOP" if diagnosis else "NEGATIVO para SOP"
        features_block = "\n".join(
            f"  • {readable_feature(name)}: {value}" for name, value in features.items()
        )
        return (
            f"## Resultado do modelo de triagem — SOP\n\n"
            f"**Diagnóstico:** {diagnosis_str}\n"
            f"**Probabilidade estimada:** {probability:.1%}\n\n"
            f"**Dados / fatores determinantes:**\n{features_block}\n\n"
            "Com base nesses dados, forneça a interpretação clínica estruturada "
            "conforme suas diretrizes."
        )

    def _parse(self, raw: str) -> Explanation:
        text = raw.strip()
        # Remove cercas de código markdown, se presentes (```json ... ```).
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[len("json") :]
            text = text.strip()
        data = json.loads(text)
        return Explanation(
            text=str(data["explanation"]),
            risk_factors=list(data.get("risk_factors", [])),
            insights=list(data.get("insights", [])),
        )

    async def explain(
        self, features: dict, diagnosis: int, probability: float
    ) -> tuple[Explanation, int | None]:
        provider_name = self.client.provider_name
        logger.info(
            "llm_explanation_started",
            provider=provider_name,
            diagnosis=diagnosis,
            probability=probability,
        )

        prompt = self._build_prompt(features, diagnosis, probability)
        try:
            llm_response: LLMResponse = await anyio.to_thread.run_sync(
                self.client.generate, _SYSTEM_PROMPT, prompt
            )
        except Exception as exc:
            logger.error(
                "llm_explanation_failed",
                provider=provider_name,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            raise LLMRequestError(
                "Falha ao gerar explicação via LLM. Verifique a configuração do "
                "provedor (LLM_PROVIDER e chaves de API)."
            ) from exc

        try:
            result = self._parse(llm_response.text)
            logger.info(
                "llm_explanation_completed",
                provider=provider_name,
                response_length=len(result.text),
                risk_factors_count=len(result.risk_factors),
                insights_count=len(result.insights),
                tokens_used=llm_response.tokens_used,
            )
            return result, llm_response.tokens_used
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.error(
                "llm_explanation_parse_failed",
                provider=provider_name,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            raise LLMRequestError(
                "O provedor LLM retornou uma resposta em formato inesperado."
            ) from exc
