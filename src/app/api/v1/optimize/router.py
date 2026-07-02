import time

import structlog
from fastapi import APIRouter, Depends

from app.api.v1.optimize.schemas import GeneticConfig, OptimizeOutput
from app.core.dependencies import get_optimizer
from app.monitoring.posthog import capture_event
from app.services.genetic_optimizer import GeneticOptimizerService

logger = structlog.get_logger()

router = APIRouter()


@router.post("/", response_model=OptimizeOutput)
async def optimize(
    config: GeneticConfig,
    optimizer: GeneticOptimizerService = Depends(get_optimizer),
):
    logger.info(
        "optimize_request_received",
        population_size=config.population_size,
        generations=config.generations,
        mutation_rate=config.mutation_rate,
        crossover_rate=config.crossover_rate,
    )
    start = time.time()

    try:
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

        fitness_history = result.fitness_history
        logger.info(
            "optimize_response_sent",
            best_fitness=result.comparison.get("optimized_auc"),
            best_params=result.best_params,
            fitness_summary={
                "best": round(max(fitness_history), 4) if fitness_history else None,
                "worst": round(min(fitness_history), 4) if fitness_history else None,
                "final": round(fitness_history[-1], 4) if fitness_history else None,
                "generations": len(fitness_history),
            },
            duration_seconds=round(duration, 3),
        )

        return OptimizeOutput(
            best_params=result.best_params,
            fitness_history=result.fitness_history,
            comparison=result.comparison,
        )
    except Exception as e:
        duration = time.time() - start
        capture_event(
            "genetic_optimization",
            properties={
                "duration_ms": round(duration * 1000, 2),
                "status": "error",
                "error": str(e),
            },
        )
        raise
