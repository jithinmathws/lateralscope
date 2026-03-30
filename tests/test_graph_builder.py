import pytest

from app.core.exceptions import GraphBuildError
from app.graph.builders.enterprise_graph_builder import EnterpriseGraphBuilder
from app.graph.loaders.synthetic_loader import load_sample_enterprise_data
from app.graph.types import EdgeData, EdgeType, NodeData, NodeType


def test_build_graph_success() -> None:
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()

    graph = builder.build_graph(nodes, edges)

    assert graph.number_of_nodes() == 8
    assert graph.number_of_edges() == 10
    assert graph.has_node("user_alice")
    assert graph.has_node("db_prod_01")
    assert graph.has_edge("ws_001", "app_srv_01")


def test_build_graph_preserves_parallel_edges() -> None:
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()

    graph = builder.build_graph(nodes, edges)

    edge_bundle = graph.get_edge_data("ws_001", "app_srv_01")

    assert edge_bundle is not None
    assert len(edge_bundle) == 2

    edge_types = {edge_data["type"] for edge_data in edge_bundle.values()}
    assert edge_types == {"NETWORK_REACHABLE", "CAN_RDP_TO"}


def test_build_graph_preserves_edge_attributes() -> None:
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()

    graph = builder.build_graph(nodes, edges)

    edge_bundle = graph.get_edge_data("app_srv_01", "db_prod_01")
    assert edge_bundle is not None

    exploit_edges = [
        edge_data
        for edge_data in edge_bundle.values()
        if edge_data["type"] == "EXPLOITS"
    ]

    assert len(exploit_edges) == 1

    exploit_edge = exploit_edges[0]
    assert exploit_edge["weight"] == 3.0
    assert exploit_edge["cve"] == "CVE-2026-0001"
    assert exploit_edge["exploit_success_prob"] == 0.7
    assert exploit_edge["detection_prob"] == 0.9


def test_build_graph_preserves_node_attributes() -> None:
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()

    graph = builder.build_graph(nodes, edges)

    alice = graph.nodes["user_alice"]
    assert alice["type"] == "identity"
    assert alice["label"] == "Alice"
    assert alice["privilege_level"] == "user"
    assert alice["domain"] == "corp.local"


def test_build_graph_rejects_duplicate_node_ids() -> None:
    nodes = [
        NodeData(id="n1", type=NodeType.IDENTITY, label="Node 1"),
        NodeData(id="n1", type=NodeType.HOST, label="Duplicate Node 1"),
    ]
    edges: list[EdgeData] = []

    builder = EnterpriseGraphBuilder()

    with pytest.raises(GraphBuildError, match="Duplicate node IDs found"):
        builder.build_graph(nodes, edges)


def test_build_graph_rejects_missing_edge_endpoint() -> None:
    nodes = [
        NodeData(id="n1", type=NodeType.IDENTITY, label="Node 1"),
    ]
    edges = [
        EdgeData(
            source="n1",
            target="missing_node",
            type=EdgeType.NETWORK_REACHABLE,
            weight=1.0,
        ),
    ]

    builder = EnterpriseGraphBuilder()

    with pytest.raises(GraphBuildError, match="references non-existent node"):
        builder.build_graph(nodes, edges)


def test_build_graph_rejects_self_loop_by_default() -> None:
    nodes = [
        NodeData(id="n1", type=NodeType.HOST, label="Host 1"),
    ]
    edges = [
        EdgeData(
            source="n1",
            target="n1",
            type=EdgeType.HAS_SESSION,
            weight=1.0,
        ),
    ]

    builder = EnterpriseGraphBuilder()

    with pytest.raises(GraphBuildError, match="Self-loop detected"):
        builder.build_graph(nodes, edges)


def test_build_graph_allows_self_loop_when_enabled() -> None:
    nodes = [
        NodeData(id="n1", type=NodeType.HOST, label="Host 1"),
    ]
    edges = [
        EdgeData(
            source="n1",
            target="n1",
            type=EdgeType.HAS_SESSION,
            weight=1.0,
        ),
    ]

    builder = EnterpriseGraphBuilder(allow_self_loops=True)
    graph = builder.build_graph(nodes, edges)

    assert graph.number_of_nodes() == 1
    assert graph.number_of_edges() == 1
    assert graph.has_edge("n1", "n1")


def test_graph_summary_counts_types_and_isolated_nodes() -> None:
    nodes = [
        NodeData(id="user_1", type=NodeType.IDENTITY, label="User 1"),
        NodeData(id="host_1", type=NodeType.HOST, label="Host 1"),
        NodeData(id="db_1", type=NodeType.CROWN_JEWEL, label="Database 1"),
    ]
    edges = [
        EdgeData(
            source="user_1",
            target="host_1",
            type=EdgeType.HAS_SESSION,
            weight=1.0,
        ),
    ]

    builder = EnterpriseGraphBuilder()
    graph = builder.build_graph(nodes, edges)
    summary = builder.summarize(graph)

    assert summary.node_count == 3
    assert summary.edge_count == 1
    assert summary.node_types["identity"] == 1
    assert summary.node_types["host"] == 1
    assert summary.node_types["crown_jewel"] == 1
    assert summary.edge_types["HAS_SESSION"] == 1
    assert summary.has_isolated_nodes is True