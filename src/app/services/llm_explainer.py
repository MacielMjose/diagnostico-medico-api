from app.domain.models import Explanation
from app.infrastructure.llm_client import LLMClient


class LLMExplainerService:
    def __init__(self, client: LLMClient):
        self.client = client

    def _build_prompt(
        self, features: dict, diagnosis: int, probability: float
    ) -> str:
        return (
            f"Você é um endocrinologista. Paciente com os seguintes dados: {features}. "
            f"Diagnóstico do modelo: {'PCOS' if diagnosis else 'Normal'} "
            f"com {probability:.1%} de confiança. "
            f"Explique os fatores de risco e forneça insights acionáveis."
        )

    async def explain(
        self, features: dict, diagnosis: int, probability: float
    ) -> Explanation:
        prompt = self._build_prompt(features, diagnosis, probability)
        response = await self.client.chat(prompt)
        return Explanation(
            text=response,
            risk_factors=["obesidade", "resistencia insulinica"],
            insights=["recomendar dieta"],
        )
