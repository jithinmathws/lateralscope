from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import networkx as nx


@dataclass(frozen=True)
class BlastRadiusResult:
    source: str
    reachable_nodes: set[str]
    reachable_node_count: int
    node_type_summary: dict[str, int]
    path_costs: dict[str, float]
    critical_nodes_reached: set[str]
    exposure_score: float = 0.0


class BlastRadiusEngine:
    """
    Analysis engine for asset exposure and attack propagation.
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    def compute_full_radius(self, source: str) -> BlastRadiusResult:
        """
        Compute the maximum weighted blast radius from a source node.
        """
        self._validate_node(source)

        path_costs = nx.single_source_dijkstra_path_length(
            self.graph,
            source,
            weight="weight",
        )

        return self._assemble_result(source, path_costs)

    def compute_budgeted_radius(self, source: str, budget: float) -> BlastRadiusResult:
        """
        Compute reachability constrained by total attacker effort budget.
        """
        self._validate_node(source)

        if budget < 0:
            raise ValueError("Budget must be non-negative")

        path_costs = nx.single_source_dijkstra_path_length(
            self.graph,
            source,
            cutoff=budget,
            weight="weight",
        )

        return self._assemble_result(source, path_costs)

    def compute_depth_limited_radius(self, source: str, max_hops: int) -> BlastRadiusResult:
        """
        Compute reachability constrained by hop count rather than weighted cost.
        """
        self._validate_node(source)

        if max_hops < 0:
            raise ValueError("max_hops must be non-negative")

        hops = nx.single_source_shortest_path_length(
            self.graph,
            source,
            cutoff=max_hops,
        )
        reachable_ids = set(hops.keys())

        all_weighted_costs = nx.single_source_dijkstra_path_length(
            self.graph,
            source,
            weight="weight",
        )

        filtered_costs = {
            node_id: all_weighted_costs[node_id]
            for node_id in reachable_ids
            if node_id in all_weighted_costs
        }

        return self._assemble_result(source, filtered_costs)

    def compute_inbound_exposure(self, target: str) -> BlastRadiusResult:
        """
        Reverse exposure analysis.

        Identifies all nodes that can reach the specified target.
        Useful for crown-jewel protection and exposure review.
        """
        self._validate_node(target)

        reversed_graph = self.graph.reverse(copy=False)

        path_costs = nx.single_source_dijkstra_path_length(
            reversed_graph,
            target,
            weight="weight",
        )

        return self._assemble_result(target, path_costs)

    def _validate_node(self, node_id: str) -> None:
        if node_id not in self.graph:
            raise ValueError(f"Node '{node_id}' does not exist in the current graph.")

    def _assemble_result(self, source: str, path_costs: dict[str, float]) -> BlastRadiusResult:
        reachable_nodes = set(path_costs.keys())

        node_types = [
            self.graph.nodes[node_id].get("type", "unknown")
            for node_id in reachable_nodes
        ]
        summary = dict(Counter(node_types))

        critical_reached = {
            node_id
            for node_id in reachable_nodes
            if self.graph.nodes[node_id].get("type") == "crown_jewel"
        }

        # Initial heuristic:
        # - crown_jewel nodes contribute 10
        # - all other nodes contribute 1
        # This can later be replaced by asset-specific criticality weights.
        score = sum(10.0 if node_type == "crown_jewel" else 1.0 for node_type in node_types)

        return BlastRadiusResult(
            source=source,
            reachable_nodes=reachable_nodes,
            reachable_node_count=len(reachable_nodes),
            node_type_summary=summary,
            path_costs=dict(path_costs),
            critical_nodes_reached=critical_reached,
            exposure_score=score,
        )