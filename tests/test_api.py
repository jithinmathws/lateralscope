from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "LateralScope API"


def test_graph_summary_endpoint():
    response = client.get("/api/graph/summary")

    assert response.status_code == 200
    data = response.json()

    assert "node_count" in data
    assert "edge_count" in data
    assert "node_types" in data
    assert "edge_types" in data
    assert "has_isolated_nodes" in data

    assert data["node_count"] == 5
    assert data["edge_count"] == 5
    assert data["has_isolated_nodes"] is False


def test_simulate_endpoint_success():
    payload = {
        "source": "user_alice",
        "target": "db_prod_01",
    }

    response = client.post("/api/simulate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["source"] == "user_alice"
    assert data["target"] == "db_prod_01"
    assert data["path_found"] is True
    assert data["attack_path"] == [
        "user_alice",
        "ws_001",
        "app_srv_01",
        "db_prod_01",
    ]
    assert data["attack_path_cost"] == 3.0
    assert len(data["attack_steps"]) == 3
    assert data["blast_radius"]["reachable_node_count"] == 5
    assert data["risk_score"] == 4.67
    assert data["error"] is None


def test_simulate_endpoint_invalid_node():
    payload = {
        "source": "not_a_real_node",
        "target": "db_prod_01",
    }

    response = client.post("/api/simulate", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "does not exist" in data["detail"]


def test_simulate_endpoint_conflicting_constraints():
    payload = {
        "source": "user_alice",
        "target": "db_prod_01",
        "budget": 3,
        "max_hops": 2,
    }

    response = client.post("/api/simulate", json=payload)

    assert response.status_code == 422

def test_blast_radius_endpoint_full():
    payload = {
        "source": "user_alice",
    }

    response = client.post("/api/blast-radius", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["source"] == "user_alice"
    assert data["reachable_node_count"] == 5
    assert "db_prod_01" in data["critical_nodes_reached"]
    assert data["exposure_score"] == 14.0


def test_blast_radius_endpoint_budgeted():
    payload = {
        "source": "user_alice",
        "budget": 2,
    }

    response = client.post("/api/blast-radius", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["source"] == "user_alice"
    assert data["reachable_node_count"] == 4
    assert "db_prod_01" not in data["reachable_nodes"]


def test_blast_radius_endpoint_invalid_node():
    payload = {
        "source": "not_a_real_node",
    }

    response = client.post("/api/blast-radius", json=payload)

    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]


def test_blast_radius_endpoint_conflicting_constraints():
    payload = {
        "source": "user_alice",
        "budget": 2,
        "max_hops": 2,
    }

    response = client.post("/api/blast-radius", json=payload)

    assert response.status_code == 422