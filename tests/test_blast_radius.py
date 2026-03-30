import pytest

from app.analysis.blast_radius import BlastRadiusEngine
from app.core.exceptions import DomainValidationError, NodeNotFoundError
from app.graph.builders.enterprise_graph_builder import EnterpriseGraphBuilder
from app.graph.loaders.synthetic_loader import load_sample_enterprise_data


@pytest.fixture
def sample_graph():
    nodes, edges = load_sample_enterprise_data()
    builder = EnterpriseGraphBuilder()
    return builder.build_graph(nodes, edges)


@pytest.fixture
def blast_engine(sample_graph):
    return BlastRadiusEngine(sample_graph)


def test_compute_full_radius_success(blast_engine) -> None:
    result = blast_engine.compute_full_radius("user_alice")

    assert result.source == "user_alice"
    assert result.reachable_node_count == 8
    assert result.reachable_nodes == {
        "user_alice",
        "grp_it_admins",
        "ws_001",
        "app_srv_01",
        "zone_user",
        "zone_server",
        "db_prod_01",
        "backup_01",
    }


def test_compute_full_radius_detects_crown_jewel(blast_engine) -> None:
    result = blast_engine.compute_full_radius("user_alice")

    assert result.critical_nodes_reached == {"db_prod_01"}
    assert result.node_type_summary["crown_jewel"] == 1


def test_compute_full_radius_path_costs_are_correct(blast_engine) -> None:
    result = blast_engine.compute_full_radius("user_alice")

    assert result.path_costs["user_alice"] == 0
    assert result.path_costs["ws_001"] == 1.0
    assert result.path_costs["grp_it_admins"] == 1.0
    assert result.path_costs["app_srv_01"] == 2.0
    assert result.path_costs["db_prod_01"] == 3.0
    assert result.path_costs["backup_01"] == 4.0


def test_compute_budgeted_radius_success(blast_engine) -> None:
    result = blast_engine.compute_budgeted_radius("user_alice", budget=2.0)

    assert result.reachable_nodes == {
        "user_alice",
        "grp_it_admins",
        "ws_001",
        "app_srv_01",
        "zone_user",
    }
    assert result.reachable_node_count == 5
    assert result.critical_nodes_reached == set()


def test_compute_budgeted_radius_includes_crown_jewel_when_budget_allows(blast_engine) -> None:
    result = blast_engine.compute_budgeted_radius("user_alice", budget=3.0)

    assert "db_prod_01" in result.reachable_nodes
    assert result.critical_nodes_reached == {"db_prod_01"}


def test_compute_depth_limited_radius_success(blast_engine) -> None:
    result = blast_engine.compute_depth_limited_radius("user_alice", max_hops=2)

    assert result.reachable_nodes == {
        "user_alice",
        "grp_it_admins",
        "ws_001",
        "app_srv_01",
        "zone_user",
    }
    assert result.reachable_node_count == 5
    assert "db_prod_01" not in result.reachable_nodes


def test_compute_depth_limited_radius_reaches_crown_jewel_at_higher_depth(blast_engine) -> None:
    result = blast_engine.compute_depth_limited_radius("user_alice", max_hops=3)

    assert "db_prod_01" in result.reachable_nodes
    assert result.critical_nodes_reached == {"db_prod_01"}


def test_compute_inbound_exposure_success(blast_engine) -> None:
    result = blast_engine.compute_inbound_exposure("db_prod_01")

    assert result.source == "db_prod_01"
    assert result.reachable_nodes == {
        "db_prod_01",
        "app_srv_01",
        "ws_001",
        "grp_it_admins",
        "user_alice",
    }


def test_compute_inbound_exposure_identifies_upstream_attack_sources(blast_engine) -> None:
    result = blast_engine.compute_inbound_exposure("db_prod_01")

    assert "user_alice" in result.reachable_nodes
    assert "app_srv_01" in result.reachable_nodes
    assert "backup_01" not in result.reachable_nodes


def test_exposure_score_is_positive(blast_engine) -> None:
    result = blast_engine.compute_full_radius("user_alice")

    assert result.exposure_score > 0


def test_compute_full_radius_rejects_missing_node(blast_engine) -> None:
    with pytest.raises(NodeNotFoundError, match="does not exist in the current graph"):
        blast_engine.compute_full_radius("missing_node")


def test_compute_budgeted_radius_rejects_negative_budget(blast_engine) -> None:
    with pytest.raises(DomainValidationError, match="Budget must be non-negative"):
        blast_engine.compute_budgeted_radius("user_alice", budget=-1.0)


def test_compute_depth_limited_radius_rejects_negative_hops(blast_engine) -> None:
    with pytest.raises(DomainValidationError, match="max_hops must be non-negative"):
        blast_engine.compute_depth_limited_radius("user_alice", max_hops=-1)