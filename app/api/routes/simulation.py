from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_service
from app.core.exceptions import (
    ConstraintConflictError,
    DomainValidationError,
    NodeNotFoundError,
)
from app.schemas.simulation import (
    AttackStepSchema,
    BlastRadiusSchema,
    SimulationRequestSchema,
    SimulationResponseSchema,
)
from app.services.graph_service import GraphService
from app.services.simulation_service import SimulationRequest

router = APIRouter(tags=["simulation"])


@router.post("/simulate", response_model=SimulationResponseSchema)
def simulate_attack(
    payload: SimulationRequestSchema,
    service: GraphService = Depends(get_service),
) -> SimulationResponseSchema:
    try:
        request = SimulationRequest(
            source=payload.source,
            target=payload.target,
            budget=payload.budget,
            max_hops=payload.max_hops,
        )

        result = service.simulation_service.run_simulation(request)

        blast_radius = BlastRadiusSchema(
            source=result.blast_radius.source,
            reachable_nodes=sorted(result.blast_radius.reachable_nodes),
            reachable_node_count=result.blast_radius.reachable_node_count,
            node_type_summary=result.blast_radius.node_type_summary,
            path_costs=result.blast_radius.path_costs,
            critical_nodes_reached=sorted(result.blast_radius.critical_nodes_reached),
            exposure_score=result.blast_radius.exposure_score,
        )

        attack_steps = [
            AttackStepSchema(
                from_node=step["from"],
                to_node=step["to"],
                edge_type=step["vector"],
                cost=step["cost"],
                attributes=step.get("attributes", {}),
            )
            for step in result.attack_steps
        ]

        lowest_cost_step = (
            AttackStepSchema(
                from_node=result.lowest_cost_step["from"],
                to_node=result.lowest_cost_step["to"],
                edge_type=result.lowest_cost_step["vector"],
                cost=result.lowest_cost_step["cost"],
                attributes=result.lowest_cost_step.get("attributes", {}),
            )
            if result.lowest_cost_step is not None
            else None
        )

        return SimulationResponseSchema(
            source=result.source,
            target=result.target,
            path_found=result.path_found,
            attack_path=result.attack_path,
            attack_path_cost=result.attack_path_cost,
            attack_steps=attack_steps,
            blast_radius=blast_radius,
            lowest_cost_step=lowest_cost_step,
            risk_score=result.risk_score,
            error=result.error,
        )

    except (NodeNotFoundError, ConstraintConflictError, DomainValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {exc}") from exc