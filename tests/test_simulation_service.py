import pytest

from app.core.exceptions import ConstraintConflictError, NodeNotFoundError
from app.graph.builders.enterprise_graph_builder import EnterpriseGraphBuilder
from app.graph.loaders.synthetic_loader import load_sample_enterprise_data
from app.services.simulation_service import SimulationRequest, SimulationService


@pytest.fixture
def sample_graph():
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()
    return builder.build_graph(nodes, edges)


@pytest.fixture
def simulation_service(sample_graph):
    return SimulationService(sample_graph)


def test_run_simulation_success(simulation_service) -> None:
    request = SimulationRequest(
        source="user_alice",
        target="db_prod_01",
    )

    result = simulation_service.run_simulation(request)

    assert result.source == "user_alice"
    assert result.target == "db_prod_01"
    assert result.path_found is True
    assert result.attack_path == ["user_alice", "ws_001", "app_srv_01", "db_prod_01"]
    assert result.attack_path_cost == 3.0
    assert len(result.attack_steps) == 3
    assert result.lowest_cost_step is not None
    assert result.lowest_cost_step["cost"] == 1.0
    assert result.risk_score > 0
    assert result.error is None


def test_run_simulation_includes_blast_radius(simulation_service) -> None:
    request = SimulationRequest(
        source="user_alice",
        target="db_prod_01",
    )

    result = simulation_service.run_simulation(request)

    assert result.blast_radius.source == "user_alice"
    assert "db_prod_01" in result.blast_radius.reachable_nodes
    assert "backup_01" in result.blast_radius.reachable_nodes
    assert result.blast_radius.critical_nodes_reached == {"db_prod_01"}


def test_run_simulation_handles_unreachable_target(sample_graph) -> None:
    graph = sample_graph.copy()
    graph.add_node("isolated_target", type="crown_jewel", label="Isolated")

    service = SimulationService(graph)
    request = SimulationRequest(
        source="user_alice",
        target="isolated_target",
    )

    result = service.run_simulation(request)

    assert result.source == "user_alice"
    assert result.target == "isolated_target"
    assert result.path_found is False
    assert result.attack_path == []
    assert result.attack_path_cost == 0.0
    assert result.attack_steps == []
    assert result.lowest_cost_step is None
    assert result.risk_score == 0.0
    assert result.error is not None
    assert "No attack path" in result.error

    assert result.blast_radius.source == "user_alice"
    assert "ws_001" in result.blast_radius.reachable_nodes
    assert "app_srv_01" in result.blast_radius.reachable_nodes


def test_run_simulation_uses_budgeted_blast_radius(simulation_service) -> None:
    request = SimulationRequest(
        source="user_alice",
        target="db_prod_01",
        budget=2.0,
    )

    result = simulation_service.run_simulation(request)

    assert result.path_found is True
    assert result.blast_radius.reachable_nodes == {
        "user_alice",
        "grp_it_admins",
        "ws_001",
        "app_srv_01",
        "zone_user",
    }
    assert result.blast_radius.critical_nodes_reached == set()


def test_run_simulation_uses_depth_limited_blast_radius(simulation_service) -> None:
    request = SimulationRequest(
        source="user_alice",
        target="db_prod_01",
        max_hops=2,
    )

    result = simulation_service.run_simulation(request)

    assert result.path_found is True
    assert result.blast_radius.reachable_nodes == {
        "user_alice",
        "grp_it_admins",
        "ws_001",
        "app_srv_01",
        "zone_user",
    }
    assert "db_prod_01" not in result.blast_radius.reachable_nodes


def test_run_simulation_enforces_exclusive_constraints(simulation_service) -> None:
    request = SimulationRequest(
        source="user_alice",
        target="db_prod_01",
        budget=10.0,
        max_hops=5,
    )

    with pytest.raises(ConstraintConflictError, match="Specify either 'budget' or 'max_hops'"):
        simulation_service.run_simulation(request)


def test_run_simulation_rejects_missing_source(simulation_service) -> None:
    request = SimulationRequest(
        source="missing_source",
        target="db_prod_01",
    )

    with pytest.raises(NodeNotFoundError, match="Simulation error: Node 'missing_source' does not exist."):
        simulation_service.run_simulation(request)


def test_run_simulation_rejects_missing_target(simulation_service) -> None:
    request = SimulationRequest(
        source="user_alice",
        target="missing_target",
    )

    with pytest.raises(NodeNotFoundError, match="Simulation error: Node 'missing_target' does not exist."):
        simulation_service.run_simulation(request)