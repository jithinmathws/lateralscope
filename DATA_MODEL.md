# 📊 LateralScope Data Model

## Overview

This document defines the **canonical data model** used in LateralScope.

LateralScope represents an enterprise environment as a **directed, weighted attack graph**, where:

- **nodes** represent entities (users, systems, assets)
- **edges** represent attacker-usable relationships or capabilities

The data model is designed to:
- support attack path analysis
- simulate compromise propagation
- enable remediation evaluation
- remain extensible for future enhancements (ATT&CK, cloud IAM, probabilistic modeling)

---

# 🧠 Graph Model

The system uses a **directed graph**:

- Nodes = entities  
- Edges = relationships enabling attacker movement  

Each edge may include attributes representing:
- difficulty
- detectability
- exploitability
- privilege requirements  

---

# 🧩 Node Model

## Base Node Schema

```json
{
  "id": "string",
  "type": "string",
  "label": "string",
  "attributes": {}
}
```

## Node Types

### 1. Identity

Represents users or accounts capable of authentication.

**Examples:**

- employee user
- service account
- admin account

```json
{
  "id": "user_1",
  "type": "identity",
  "label": "Alice",
  "attributes": {
    "privilege_level": "user | admin",
    "domain": "corp.local"
  }
}
```

### 2. Host

Represents compute infrastructure.

**Examples:**

- workstation
- application server
- database server
- domain controller

```json
{
  "id": "server_1",
  "type": "host",
  "label": "App Server",
  "attributes": {
    "os": "windows | linux",
    "criticality": "low | medium | high"
  }
}
```

### 3. Data Asset

Represents storage or sensitive data systems.

**Examples:**

- SQL database
- object storage
- backup system

```json
{
  "id": "db_1",
  "type": "data_asset",
  "label": "Customer Database",
  "attributes": {
    "sensitivity": "high",
    "data_type": "pii | financial"
  }
}
```

### 4. Network Zone

Represents network segmentation boundaries.

**Examples:**

- subnet
- VLAN
- security zone

```json
{
  "id": "zone_1",
  "type": "network",
  "label": "Internal Network",
  "attributes": {
    "trust_level": "internal | external"
  }
}
```

### 5. Crown Jewel

Represents high-value compromise targets.

**Examples:**

- domain controller
- production database
- backup server

```json
{
  "id": "dc_1",
  "type": "crown_jewel",
  "label": "Domain Controller",
  "attributes": {
    "criticality": "critical"
  }
}
```

## 🔗 Edge Model

### Base Edge Schema

```json
{
  "source": "string",
  "target": "string",
  "type": "string",
  "weight": 1.0,
  "attributes": {}
}
```

### Edge Categories

#### 1. Identity & Privilege Edges

**MEMBER_OF**

Represents group or role membership.

```json
{
  "source": "user_1",
  "target": "group_admins",
  "type": "MEMBER_OF",
  "weight": 1.0
}
```

**ADMIN_ON**

Represents administrative control over a host.

```json
{
  "source": "user_1",
  "target": "server_1",
  "type": "ADMIN_ON",
  "weight": 2.0
}
```

**TRUSTS**

Represents trust relationships.

```json
{
  "source": "domain_a",
  "target": "domain_b",
  "type": "TRUSTS",
  "weight": 2.5
}
```

#### 2. Session & Credential Edges

**HAS_SESSION**

Represents active credential presence.

```json
{
  "source": "user_1",
  "target": "server_1",
  "type": "HAS_SESSION",
  "weight": 1.5
}
```

**CAN_IMPERSONATE**

Represents ability to impersonate another identity.

```json
{
  "source": "user_1",
  "target": "user_2",
  "type": "CAN_IMPERSONATE",
  "weight": 2.0
}
```

#### 3. Lateral Movement Edges

**CAN_RDP_TO**

```json
{
  "source": "host_1",
  "target": "host_2",
  "type": "CAN_RDP_TO",
  "weight": 2.0
}
```

**CAN_SSH_TO**

```json
{
  "source": "host_1",
  "target": "host_2",
  "type": "CAN_SSH_TO",
  "weight": 2.0
}
```

#### 4. Network Reachability Edges

**NETWORK_REACHABLE**

```json
{
  "source": "host_1",
  "target": "host_2",
  "type": "NETWORK_REACHABLE",
  "weight": 1.0
}
```

#### 5. Exploitability Edges

**EXPLOITS**

```json
{
  "source": "host_1",
  "target": "host_2",
  "type": "EXPLOITS",
  "weight": 3.0,
  "attributes": {
    "cve": "CVE-2023-1234"
  }
}
```

**VULNERABLE_TO**

```json
{
  "source": "host_1",
  "target": "vuln_1",
  "type": "VULNERABLE_TO",
  "weight": 2.5
}
```

## ⚖️ Edge Attributes

Each edge may include:

| Attribute | Description |
|-----------|-------------|
| weight | Cost of performing the attack step |
| difficulty | Technical difficulty |
| detectability | Likelihood of detection |
| exploitability | Ease of exploitation |
| required_privilege | Required access level |

## 🧮 Weighting Strategy

Edge weights represent attacker effort.

- **Higher weight** → harder or riskier step
- **Lower weight** → easier step

**Example:**

| Edge Type | Typical Weight |
|-----------|----------------|
| NETWORK_REACHABLE | 1.0 |
| HAS_SESSION | 1.5 |
| ADMIN_ON | 2.0 |
| EXPLOITS | 3.0 |

## 🔄 Graph Constraints

The model enforces:

- Directed edges (no implicit symmetry)
- Unique node IDs
- Valid edge references (source and target must exist)
- No self-loops (unless explicitly allowed)

## 📦 Example Graph

```json
{
  "nodes": [
    {"id": "user_1", "type": "identity"},
    {"id": "host_1", "type": "host"},
    {"id": "db_1", "type": "data_asset"}
  ],
  "edges": [
    {"source": "user_1", "target": "host_1", "type": "ADMIN_ON", "weight": 2.0},
    {"source": "host_1", "target": "db_1", "type": "NETWORK_REACHABLE", "weight": 1.0}
  ]
}
```

## 🔮 Future Extensions

Planned enhancements:

- MITRE ATT&CK technique mapping
- CVE / KEV enrichment
- probabilistic edge weights
- time-based attack propagation
- cloud IAM entities (AWS, Azure)

## 💡 Design Principles

- Keep the model simple but extensible
- Represent real attacker capabilities
- Avoid overfitting to specific environments
- Support both simulation and analysis

## ⭐ Summary

The LateralScope data model provides:

- a flexible graph representation of enterprise environments
- a foundation for attack path simulation
- a structure for risk and remediation analysis

It is designed to balance:

- realism
- simplicity
- extensibility