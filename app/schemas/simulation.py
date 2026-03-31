from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class SimulationRequestSchema(BaseModel):
    source: str = Field(..., min_length=1, description="Starting node ID")
    target: str = Field(..., min_length=1, description="Target node ID")
    budget: float | None = Field(default=None, gt=0)
    max_hops: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_constraints(self) -> "SimulationRequestSchema":
        if self.budget is not None and self.max_hops is not None:
            raise ValueError("Specify either 'budget' or 'max_hops', not both.")
        return self


class AttackStepSchema(BaseModel):
    from_node: str
    to_node: str
    edge_type: str
    cost: float
    attributes: dict[str, Any] = Field(default_factory=dict)


class BlastRadiusSchema(BaseModel):
    source: str
    reachable_nodes: list[str]
    reachable_node_count: int
    node_type_summary: dict[str, int]
    path_costs: dict[str, float]
    critical_nodes_reached: list[str]
    exposure_score: float


class SimulationResponseSchema(BaseModel):
    source: str
    target: str
    path_found: bool
    attack_path: list[str] = Field(default_factory=list)
    attack_path_cost: float
    attack_steps: list[AttackStepSchema] = Field(default_factory=list)
    blast_radius: BlastRadiusSchema
    lowest_cost_step: AttackStepSchema | None = None
    risk_score: float = 0.0
    error: str | None = None