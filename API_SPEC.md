# 🔌 LateralScope API Specification

## Overview

This document defines the API contract for **LateralScope**, a graph-based cyber attack simulation platform.

The API enables clients to:
- load and inspect enterprise graphs
- define attack scenarios
- run attack path and blast radius simulations
- evaluate remediation strategies

---

## Base URL

```text
http://localhost:8000
```

## Authentication (Planned)

Authentication is not required in v1.

Future versions may include:

- API keys
- JWT-based authentication

## Content Type

All requests and responses use:

```
Content-Type: application/json
```

## 📊 Health

### GET /health

Check if the API is running.

**Response:**

```json
{
  "status": "ok"
}
```

## 🧠 Graph Endpoints

### POST /graphs/load-sample

Load a synthetic enterprise graph into memory.

**Response:**

```json
{
  "graph_id": "graph_001",
  "nodes": 120,
  "edges": 340
}
```

### GET /graphs/{graph_id}/summary

Get high-level graph statistics.

**Response:**

```json
{
  "graph_id": "graph_001",
  "node_count": 120,
  "edge_count": 340,
  "node_types": {
    "identity": 40,
    "host": 50,
    "data_asset": 20,
    "network": 10
  }
}
```

### GET /graphs/{graph_id}/nodes

Return all nodes.

**Response:**

```json
[
  {
    "id": "user_1",
    "type": "identity",
    "label": "User A"
  }
]
```

### GET /graphs/{graph_id}/edges

Return all edges.

**Response:**

```json
[
  {
    "source": "user_1",
    "target": "server_1",
    "type": "CAN_RDP_TO",
    "weight": 2.0
  }
]
```

## 🎯 Scenario Endpoints

### POST /scenarios

Create a new attack scenario.

**Request:**

```json
{
  "graph_id": "graph_001",
  "entry_nodes": ["workstation_1"],
  "target_nodes": ["database_1"],
  "max_steps": 5
}
```

**Response:**

```json
{
  "scenario_id": "scenario_001",
  "status": "created"
}
```

### GET /scenarios/{scenario_id}

Retrieve scenario details.

**Response:**

```json
{
  "scenario_id": "scenario_001",
  "graph_id": "graph_001",
  "entry_nodes": ["workstation_1"],
  "target_nodes": ["database_1"],
  "max_steps": 5
}
```

## ⚡ Simulation Endpoints

### POST /simulations/run

Run attack path and blast radius simulation.

**Request:**

```json
{
  "scenario_id": "scenario_001"
}
```

**Response:**

```json
{
  "run_id": "run_001",
  "status": "completed",
  "attack_paths": [
    {
      "path": ["workstation_1", "server_1", "database_1"],
      "cost": 5.0
    }
  ],
  "blast_radius": [
    "server_1",
    "database_1",
    "backup_1"
  ],
  "metrics": {
    "reachable_nodes": 12,
    "critical_assets_reached": 2
  }
}
```

### GET /simulations/{run_id}

Retrieve simulation results.

**Response:**

```json
{
  "run_id": "run_001",
  "status": "completed",
  "metrics": {
    "reachable_nodes": 12,
    "critical_assets_reached": 2,
    "min_path_cost": 5.0
  }
}
```

## 🛡️ Remediation Endpoints

### POST /remediations/evaluate

Evaluate remediation actions.

**Request:**

```json
{
  "scenario_id": "scenario_001",
  "actions": [
    {
      "type": "REMOVE_EDGE",
      "source": "user_1",
      "target": "server_1"
    }
  ]
}
```

**Response:**

```json
{
  "remediation_id": "rem_001",
  "impact": {
    "paths_reduced": 3,
    "blast_radius_reduction": 5,
    "risk_reduction": 0.42
  }
}
```

### GET /remediations/{remediation_id}

Retrieve remediation analysis.

**Response:**

```json
{
  "remediation_id": "rem_001",
  "status": "completed",
  "impact": {
    "paths_reduced": 3,
    "blast_radius_reduction": 5,
    "risk_reduction": 0.42
  }
}
```

## 📦 Data Models

### Node

```json
{
  "id": "string",
  "type": "identity | host | data_asset | network | crown_jewel",
  "label": "string"
}
```

### Edge

```json
{
  "source": "string",
  "target": "string",
  "type": "string",
  "weight": "number"
}
```

### Scenario

```json
{
  "graph_id": "string",
  "entry_nodes": ["string"],
  "target_nodes": ["string"],
  "max_steps": "integer"
}
```

### Simulation Result

```json
{
  "attack_paths": [],
  "blast_radius": [],
  "metrics": {}
}
```

## ❗ Error Handling

### Standard Error Response

```json
{
  "detail": "Error message"
}
```

### Common Errors

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid request payload |
| 404 | Resource not found |
| 500 | Internal server error |

## 🔮 Future Enhancements

- Authentication and authorization
- Pagination for large graphs
- Streaming simulation results
- Async job queue for long-running simulations
- Graph filtering and subgraph queries
- Versioned API (/v1/, /v2/)

## 📌 Notes

- All IDs are string-based for flexibility
- Graph is assumed to be loaded before simulation
- Simulation runs are deterministic in v1