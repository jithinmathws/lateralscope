from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class SimulationRequestSchema(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "user_alice",
                    "target": "db_prod_01"
                },
                {
                    "source": "user_alice",
                    "target": "db_prod_01",
                    "budget": 3.0
                }
            ]
        }
    }

    source: str = Field(
        ...,
        min_length=1,
        description="Starting node ID for the simulated attack path.",
        examples=["user_alice"],
    )
    target: str = Field(
        ...,
        min_length=1,
        description="Target node ID the attacker is attempting to reach.",
        examples=["db_prod_01"],
    )
    budget: float | None = Field(
        default=None,
        gt=0,
        description="Optional maximum weighted attack budget.",
        examples=[3.0],
    )
    max_hops: int | None = Field(
        default=None,
        ge=1,
        description="Optional maximum number of hops allowed in the blast radius calculation.",
        examples=[2],
    )

    @model_validator(mode="after")
    def validate_constraints(self) -> "SimulationRequestSchema":
        if self.budget is not None and self.max_hops is not None:
            raise ValueError("Specify either 'budget' or 'max_hops', not both.")
        return self


class AttackStepSchema(BaseModel):
    from_node: str = Field(..., description="Source node of the attack step.")
    to_node: str = Field(..., description="Destination node of the attack step.")
    edge_type: str = Field(..., description="Attack vector or graph edge type used.")
    cost: float = Field(..., description="Weighted traversal cost for this step.")
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional edge-level metadata associated with the attack step.",
    )


class BlastRadiusRequestSchema(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "user_alice"
                },
                {
                    "source": "user_alice",
                    "max_hops": 2
                }
            ]
        }
    }

    source: str = Field(
        ...,
        min_length=1,
        description="Starting node ID for blast radius analysis.",
        examples=["user_alice"],
    )
    budget: float | None = Field(
        default=None,
        gt=0,
        description="Optional maximum weighted attack budget.",
        examples=[2.0],
    )
    max_hops: int | None = Field(
        default=None,
        ge=1,
        description="Optional maximum hop depth for reachability analysis.",
        examples=[2],
    )

    @model_validator(mode="after")
    def validate_constraints(self) -> "BlastRadiusRequestSchema":
        if self.budget is not None and self.max_hops is not None:
            raise ValueError("Specify either 'budget' or 'max_hops', not both.")
        return self


class BlastRadiusSchema(BaseModel):
    source: str = Field(..., description="Source node used for the blast radius analysis.")
    reachable_nodes: list[str] = Field(
        default_factory=list,
        description="Sorted list of nodes reachable from the source under the chosen constraints.",
    )
    reachable_node_count: int = Field(
        ...,
        description="Total number of reachable nodes, including the source.",
    )
    node_type_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Breakdown of reachable nodes by node type.",
    )
    path_costs: dict[str, float] = Field(
        default_factory=dict,
        description="Lowest known weighted cost from the source to each reachable node.",
    )
    critical_nodes_reached: list[str] = Field(
        default_factory=list,
        description="Reachable crown-jewel or critical nodes.",
    )
    exposure_score: float = Field(
        ...,
        description="Heuristic exposure score derived from reachable assets.",
    )


class SimulationResponseSchema(BaseModel):
    source: str = Field(..., description="Source node for the simulation.")
    target: str = Field(..., description="Target node for the simulation.")
    path_found: bool = Field(..., description="Whether a valid attack path to the target was found.")
    attack_path: list[str] = Field(
        default_factory=list,
        description="Ordered list of node IDs representing the attack path.",
    )
    attack_path_cost: float = Field(
        ...,
        description="Total weighted cost of the selected attack path.",
    )
    attack_steps: list[AttackStepSchema] = Field(
        default_factory=list,
        description="Step-by-step breakdown of the selected attack path.",
    )
    blast_radius: BlastRadiusSchema = Field(
        ...,
        description="Blast radius analysis from the selected source.",
    )
    lowest_cost_step: AttackStepSchema | None = Field(
        default=None,
        description="Single lowest-cost step found in the chosen attack path.",
    )
    risk_score: float = Field(
        default=0.0,
        description="Heuristic risk score derived from exposure and path cost.",
    )
    error: str | None = Field(
        default=None,
        description="Optional error message when no path is found or analysis is constrained.",
    )