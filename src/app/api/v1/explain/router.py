from fastapi import APIRouter, Depends

from app.api.v1.explain.schemas import ExplainInput, ExplainOutput
from app.core.dependencies import get_explainer
from app.services.llm_explainer import LLMExplainerService

router = APIRouter()


@router.post("/", response_model=ExplainOutput)
async def explain(
    input_data: ExplainInput,
    explainer: LLMExplainerService = Depends(get_explainer),
):
    result = await explainer.explain(
        features=input_data.features,
        diagnosis=input_data.diagnosis,
        probability=input_data.probability,
    )
    return ExplainOutput(
        explanation=result.text,
        risk_factors=result.risk_factors,
        insights=result.insights,
    )
