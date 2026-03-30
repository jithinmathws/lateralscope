from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Set

import networkx as nx

from app.core.exceptions import GraphBuildError
from app.graph.types import EdgeData, NodeData


@dataclass(frozen=True)
class GraphSummary:
    node_count: int
    edge_count: int
    node_types: Dict[str, int]
    edge_types: Dict[str, int]
    has_isolated_nodes: bool


class EnterpriseGraphBuilder:
    """
    Builds a high-fidelity MultiDiGraph representing the enterprise attack surface.

    Attributes:
        allow_self_loops: If False, prevents nodes from having edges to themselves.
    """

    _RESERVED_NODE_FIELDS = {"type", "label"}
    _RESERVED_EDGE_FIELDS = {"type", "weight"}

    def __init__(self, allow_self_loops: bool = False) -> None:
        self.allow_self_loops = allow_self_loops

    def build_graph(
        self,
        nodes: List[NodeData],
        edges: List[EdgeData],
    ) -> nx.MultiDiGraph:
        """
        Builds a MultiDiGraph to support multiple attack vectors between the same assets.
        """
        self._validate_unique_node_ids(nodes)

        graph = nx.MultiDiGraph()

        for node in nodes:
            self._validate_node_attributes(node)

            graph.add_node(
                node.id,
                type=node.type.value,
                label=node.label,
                **node.attributes,
            )

        node_ids: Set[str] = set(graph.nodes)

        for edge in edges:
            self._validate_edge_endpoints(edge, node_ids)
            self._validate_self_loop(edge)
            self._validate_edge_attributes(edge)

            graph.add_edge(
                edge.source,
                edge.target,
                type=edge.type.value,
                weight=edge.weight,
                **edge.attributes,
            )

        return graph

    def summarize(self, graph: nx.MultiDiGraph) -> GraphSummary:
        """
        Generates a structural and security-focused summary of the graph.
        """
        node_type_counts = Counter(
            data.get("type", "unknown") for _, data in graph.nodes(data=True)
        )
        edge_type_counts = Counter(
            data.get("type", "unknown")
            for _, _, _, data in graph.edges(keys=True, data=True)
        )

        isolated_nodes = list(nx.isolates(graph))

        return GraphSummary(
            node_count=graph.number_of_nodes(),
            edge_count=graph.number_of_edges(),
            node_types=dict(node_type_counts),
            edge_types=dict(edge_type_counts),
            has_isolated_nodes=len(isolated_nodes) > 0,
        )

    def _validate_unique_node_ids(self, nodes: List[NodeData]) -> None:
        seen: Set[str] = set()
        duplicates: Set[str] = set()

        for node in nodes:
            if node.id in seen:
                duplicates.add(node.id)
            seen.add(node.id)

        if duplicates:
            duplicate_list = ", ".join(sorted(duplicates))
            raise GraphBuildError(f"Duplicate node IDs found: {duplicate_list}")

    def _validate_edge_endpoints(self, edge: EdgeData, node_ids: Set[str]) -> None:
        missing = [n for n in (edge.source, edge.target) if n not in node_ids]
        if missing:
            missing_list = ", ".join(missing)
            raise GraphBuildError(
                f"Edge [{edge.source} -> {edge.target}] of type '{edge.type.value}' "
                f"references non-existent node(s): {missing_list}"
            )

    def _validate_self_loop(self, edge: EdgeData) -> None:
        if not self.allow_self_loops and edge.source == edge.target:
            raise GraphBuildError(
                f"Self-loop detected on node '{edge.source}'. "
                "Attackers cannot move laterally to the same node."
            )

    def _validate_node_attributes(self, node: NodeData) -> None:
        collisions = self._RESERVED_NODE_FIELDS.intersection(node.attributes.keys())
        if collisions:
            raise GraphBuildError(
                f"Node '{node.id}' uses reserved attribute name(s): {sorted(collisions)}"
            )

    def _validate_edge_attributes(self, edge: EdgeData) -> None:
        collisions = self._RESERVED_EDGE_FIELDS.intersection(edge.attributes.keys())
        if collisions:
            raise GraphBuildError(
                f"Edge '{edge.type.value}' from '{edge.source}' to '{edge.target}' "
                f"uses reserved attribute name(s): {sorted(collisions)}"
            )