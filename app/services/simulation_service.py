from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx

from app.analysis.attack_path_engine import (
    AttackPathNotFound,
    find_attack_path_with_cost,
    get_path_step_details,
)
from app.analysis.blast_radius import BlastRadiusEngine, BlastRadiusResult


@dataclass(frozen=True)
class SimulationRequest:
    source: str
    target: str
    budget: float | None = None
    max_hops: int | None = None


@dataclass(frozen=True)
class SimulationResult:
    source: str
    target: str
    path_found: bool
    attack_path: list[str]
    attack_path_cost: float
    attack_steps: list[dict[str, Any]]
    blast_radius: BlastRadiusResult
    lowest_cost_step: dict[str, Any] | None = None
    risk_score: float = 0.0
    error: str | None = None


class SimulationService:
    """
    Central orchestration layer for cyber attack simulation.
    Combines path analysis, step enrichment, and blast radius evaluation.
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.blast_radius_engine = BlastRadiusEngine(graph)

    def run_simulation(self, request: SimulationRequest) -> SimulationResult:
        """
        Execute a multi-stage attack simulation.

        Blast radius remains meaningful even if the target exists
        but is unreachable from the chosen source.
        """
        self._validate_request(request)

        blast_result = self._compute_blast_radius(request)

        try:
            attack_path, cost = find_attack_path_with_cost(
                self.graph,
                request.source,
                request.target,
            )
            steps = get_path_step_details(self.graph, attack_path)

            lowest_cost_step = min(steps, key=lambda step: step["cost"]) if steps else None

            # Initial heuristic:
            # higher exposure and lower attack cost produce higher risk
            risk = blast_result.exposure_score / (cost if cost > 0 else 1.0)

            return SimulationResult(
                source=request.source,
                target=request.target,
                path_found=True,
                attack_path=attack_path,
                attack_path_cost=cost,
                attack_steps=steps,
                blast_radius=blast_result,
                lowest_cost_step=lowest_cost_step,
                risk_score=round(risk, 2),
                error=None,
            )

        except AttackPathNotFound as exc:
            return self._build_empty_path_result(
                request=request,
                blast_result=blast_result,
                error_msg=str(exc),
            )

    def _validate_request(self, request: SimulationRequest) -> None:
        if request.budget is not None and request.max_hops is not None:
            raise ValueError("Specify either 'budget' or 'max_hops', not both.")

        for node in (request.source, request.target):
            if node not in self.graph:
                raise ValueError(f"Simulation error: Node '{node}' does not exist.")

    def _compute_blast_radius(self, request: SimulationRequest) -> BlastRadiusResult:
        if request.budget is not None:
            return self.blast_radius_engine.compute_budgeted_radius(
                request.source,
                request.budget,
            )

        if request.max_hops is not None:
            return self.blast_radius_engine.compute_depth_limited_radius(
                request.source,
                request.max_hops,
            )

        return self.blast_radius_engine.compute_full_radius(request.source)

    def _build_empty_path_result(
        self,
        request: SimulationRequest,
        blast_result: BlastRadiusResult,
        error_msg: str,
    ) -> SimulationResult:
        return SimulationResult(
            source=request.source,
            target=request.target,
            path_found=False,
            attack_path=[],
            attack_path_cost=0.0,
            attack_steps=[],
            blast_radius=blast_result,
            lowest_cost_step=None,
            risk_score=0.0,
            error=error_msg,
        )