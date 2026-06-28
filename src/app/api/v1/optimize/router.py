import time

from fastapi import APIRouter, Depends

from app.api.v1.optimize.schemas import GeneticConfig, OptimizeOutput
from app.core.dependencies import get_optimizer
from app.monitoring.posthog import capture_event
from app.services.genetic_optimizer import GeneticOptimizerService

router = APIRouter()


@router.post("/", response_model=OptimizeOutput)
async def optimize(
    config: GeneticConfig,
    optimizer: GeneticOptimizerService = Depends(get_optimizer),
):
    start = time.time()
    result = optimizer.run(config.model_dump())
    duration = time.time() - start

    capture_event(
        "genetic_optimization",
        properties={
            "duration_ms": round(duration * 1000, 2),
            "population_size": config.population_size,
            "generations": config.generations,
            "mutation_rate": config.mutation_rate,
            "improvement": result.comparison.get("improvement_percent", 0),
        },
    )

    return OptimizeOutput(
        best_params=result.best_params,
        fitness_history=result.fitness_history,
        comparison=result.comparison,
    )
