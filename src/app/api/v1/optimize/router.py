from fastapi import APIRouter, Depends

from app.api.v1.optimize.schemas import GeneticConfig, OptimizeOutput
from app.core.dependencies import get_optimizer
from app.services.genetic_optimizer import GeneticOptimizerService

router = APIRouter()


@router.post("/", response_model=OptimizeOutput)
async def optimize(
    config: GeneticConfig,
    optimizer: GeneticOptimizerService = Depends(get_optimizer),
):
    result = optimizer.run(config.model_dump())
    return OptimizeOutput(
        best_params=result.best_params,
        fitness_history=result.fitness_history,
        comparison=result.comparison,
    )
