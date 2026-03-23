from __future__ import annotations

import networkx as nx


class AttackPathNotFound(Exception):
    """Raised when no attack path exists between source and target."""


def find_shortest_attack_path(
    graph: nx.MultiDiGraph,
    source: str,
    target: str,
) -> list[str]:
    """
    Find the lowest-cost attack path between source and target using edge weights.
    """
    if source not in graph:
        raise ValueError(f"Source node '{source}' not found in graph")

    if target not in graph:
        raise ValueError(f"Target node '{target}' not found in graph")

    try:
        return nx.shortest_path(
            graph,
            source=source,
            target=target,
            weight="weight",
        )
    except nx.NetworkXNoPath as exc:
        raise AttackPathNotFound(
            f"No attack path from '{source}' to '{target}'"
        ) from exc


def calculate_path_cost(
    graph: nx.MultiDiGraph,
    path: list[str],
) -> float:
    """
    Calculate total cost of a given path.

    For parallel edges between two nodes, the minimum-weight edge is used.
    """
    if len(path) < 2:
        return 0.0

    total_cost = 0.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        edge_bundle = graph.get_edge_data(u, v)
        if not edge_bundle:
            raise ValueError(f"No edge exists between '{u}' and '{v}'")

        min_weight = min(edge_data["weight"] for edge_data in edge_bundle.values())
        total_cost += min_weight

    return total_cost


def find_attack_path_with_cost(
    graph: nx.MultiDiGraph,
    source: str,
    target: str,
) -> tuple[list[str], float]:
    """
    Return both the shortest attack path and its total cost.
    """
    path = find_shortest_attack_path(graph, source, target)
    cost = calculate_path_cost(graph, path)
    return path, cost


def get_path_step_details(
    graph: nx.MultiDiGraph,
    path: list[str],
) -> list[dict]:
    """
    Return step-by-step details for a path.

    For each pair of nodes in the path, the minimum-weight edge is selected.
    """
    if len(path) < 2:
        return []

    steps: list[dict] = []

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        edge_bundle = graph.get_edge_data(u, v)
        if not edge_bundle:
            raise ValueError(f"No edge exists between '{u}' and '{v}'")

        best_edge_key = min(edge_bundle, key=lambda k: edge_bundle[k]["weight"])
        best_edge = edge_bundle[best_edge_key]

        extra_attributes = {
            key: value
            for key, value in best_edge.items()
            if key not in {"type", "weight"}
        }

        steps.append(
            {
                "from": u,
                "to": v,
                "vector": best_edge["type"],
                "cost": best_edge["weight"],
                "attributes": extra_attributes,
            }
        )

    return steps


def get_blast_radius_with_budget(
    graph: nx.MultiDiGraph,
    source: str,
    budget: float,
) -> set[str]:
    """
    Return all nodes reachable from source within a total attacker effort budget.
    """
    if source not in graph:
        raise ValueError(f"Source node '{source}' not found in graph")

    if budget < 0:
        raise ValueError("Budget must be non-negative")

    lengths = nx.single_source_dijkstra_path_length(
        graph,
        source,
        weight="weight",
    )

    return {node for node, dist in lengths.items() if dist <= budget}