import pytest

from app.analysis.attack_path_engine import (
    calculate_path_cost,
    find_attack_path_with_cost,
    find_shortest_attack_path,
    get_blast_radius_with_budget,
    get_path_step_details,
)
from app.core.exceptions import (
    AttackPathNotFoundError,
    DomainValidationError,
    EdgeNotFoundError,
    NodeNotFoundError,
)
from app.graph.builders.enterprise_graph_builder import EnterpriseGraphBuilder
from app.graph.loaders.synthetic_loader import load_sample_enterprise_data


@pytest.fixture
def sample_graph():
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()
    return builder.build_graph(nodes, edges)


def test_find_shortest_attack_path_success(sample_graph) -> None:
    path = find_shortest_attack_path(sample_graph, "user_alice", "db_prod_01")

    assert path == ["user_alice", "ws_001", "app_srv_01", "db_prod_01"]


def test_find_shortest_attack_path_rejects_missing_source(sample_graph) -> None:
    with pytest.raises(NodeNotFoundError, match="Source node 'missing_source' not found"):
        find_shortest_attack_path(sample_graph, "missing_source", "db_prod_01")


def test_find_shortest_attack_path_rejects_missing_target(sample_graph) -> None:
    with pytest.raises(NodeNotFoundError, match="Target node 'missing_target' not found"):
        find_shortest_attack_path(sample_graph, "user_alice", "missing_target")


def test_find_shortest_attack_path_raises_when_no_path_exists(sample_graph) -> None:
    with pytest.raises(AttackPathNotFoundError, match="No attack path"):
        find_shortest_attack_path(sample_graph, "backup_01", "user_alice")


def test_calculate_path_cost_success(sample_graph) -> None:
    path = ["user_alice", "grp_it_admins", "app_srv_01", "db_prod_01"]

    cost = calculate_path_cost(sample_graph, path)

    assert cost == 4.0


def test_calculate_path_cost_returns_zero_for_short_path(sample_graph) -> None:
    assert calculate_path_cost(sample_graph, ["user_alice"]) == 0.0
    assert calculate_path_cost(sample_graph, []) == 0.0


def test_calculate_path_cost_raises_for_invalid_edge_sequence(sample_graph) -> None:
    bad_path = ["user_alice", "db_prod_01"]

    with pytest.raises(EdgeNotFoundError, match="No edge exists between"):
        calculate_path_cost(sample_graph, bad_path)


def test_find_attack_path_with_cost_success(sample_graph) -> None:
    path, cost = find_attack_path_with_cost(sample_graph, "user_alice", "db_prod_01")

    assert path == ["user_alice", "ws_001", "app_srv_01", "db_prod_01"]
    assert cost == 3.0


def test_get_path_step_details_success(sample_graph) -> None:
    path = ["user_alice", "ws_001", "app_srv_01", "db_prod_01"]

    steps = get_path_step_details(sample_graph, path)

    assert len(steps) == 3

    assert steps[0]["from"] == "user_alice"
    assert steps[0]["to"] == "ws_001"
    assert steps[0]["vector"] == "HAS_SESSION"
    assert steps[0]["cost"] == 1.0

    assert steps[1]["from"] == "ws_001"
    assert steps[1]["to"] == "app_srv_01"
    assert steps[1]["vector"] == "NETWORK_REACHABLE"
    assert steps[1]["cost"] == 1.0

    assert steps[2]["from"] == "app_srv_01"
    assert steps[2]["to"] == "db_prod_01"
    assert steps[2]["vector"] == "NETWORK_REACHABLE"
    assert steps[2]["cost"] == 1.0


def test_get_path_step_details_preserves_extra_edge_attributes(sample_graph) -> None:
    path = ["app_srv_01", "db_prod_01"]

    steps = get_path_step_details(sample_graph, path)

    assert len(steps) == 1

    step = steps[0]
    assert step["vector"] == "NETWORK_REACHABLE"
    assert step["attributes"]["port"] == 1433
    assert step["attributes"]["protocol"] == "tcp"


def test_get_path_step_details_returns_empty_for_short_path(sample_graph) -> None:
    assert get_path_step_details(sample_graph, []) == []
    assert get_path_step_details(sample_graph, ["user_alice"]) == []


def test_get_path_step_details_raises_for_invalid_edge_sequence(sample_graph) -> None:
    bad_path = ["user_alice", "db_prod_01"]

    with pytest.raises(EdgeNotFoundError, match="No edge exists between"):
        get_path_step_details(sample_graph, bad_path)


def test_get_blast_radius_with_budget_success(sample_graph) -> None:
    reachable = get_blast_radius_with_budget(sample_graph, "user_alice", budget=4.0)

    assert "user_alice" in reachable
    assert "ws_001" in reachable
    assert "app_srv_01" in reachable
    assert "db_prod_01" in reachable
    assert "backup_01" in reachable


def test_get_blast_radius_with_budget_rejects_missing_source(sample_graph) -> None:
    with pytest.raises(NodeNotFoundError, match="Source node 'missing_source' not found"):
        get_blast_radius_with_budget(sample_graph, "missing_source", budget=3.0)


def test_get_blast_radius_with_budget_rejects_negative_budget(sample_graph) -> None:
    with pytest.raises(DomainValidationError, match="Budget must be non-negative"):
        get_blast_radius_with_budget(sample_graph, "user_alice", budget=-1.0)