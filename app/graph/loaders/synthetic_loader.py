from __future__ import annotations

from app.graph.types import EdgeData, EdgeType, NodeData, NodeType


def load_sample_enterprise_data() -> tuple[list[NodeData], list[EdgeData]]:
    """
    Return a deterministic synthetic enterprise dataset for local development
    and unit testing.

    Attack story:
    - Alice has a session on a workstation
    - the workstation can reach an application server
    - the application server can reach and exploit the production database
    - the production database can reach the backup repository

    This creates a small but meaningful attack graph for early development.
    """
    nodes = [
        NodeData(
            id="user_alice",
            type=NodeType.IDENTITY,
            label="Alice",
            attributes={
                "privilege_level": "user",
                "domain": "corp.local",
            },
        ),
        NodeData(
            id="grp_it_admins",
            type=NodeType.GROUP,
            label="IT Admins",
            attributes={
                "tier": "privileged",
                "domain": "corp.local",
            },
        ),
        NodeData(
            id="ws_001",
            type=NodeType.HOST,
            label="Workstation 001",
            attributes={
                "os": "windows",
                "criticality": "low",
                "tier": "user",
            },
        ),
        NodeData(
            id="app_srv_01",
            type=NodeType.HOST,
            label="Application Server 01",
            attributes={
                "os": "windows",
                "criticality": "medium",
                "tier": "server",
            },
        ),
        NodeData(
            id="db_prod_01",
            type=NodeType.CROWN_JEWEL,
            label="Production Database",
            attributes={
                "criticality": "critical",
                "data_type": "customer_records",
                "tier": "crown_jewel",
            },
        ),
        NodeData(
            id="backup_01",
            type=NodeType.DATA_ASSET,
            label="Backup Repository",
            attributes={
                "sensitivity": "high",
                "criticality": "high",
            },
        ),
        NodeData(
            id="zone_user",
            type=NodeType.NETWORK,
            label="User Network Zone",
            attributes={
                "trust_level": "internal",
            },
        ),
        NodeData(
            id="zone_server",
            type=NodeType.NETWORK,
            label="Server Network Zone",
            attributes={
                "trust_level": "restricted",
            },
        ),
    ]

    edges = [
        EdgeData(
            source="user_alice",
            target="ws_001",
            type=EdgeType.HAS_SESSION,
            weight=1.0,
            attributes={
                "credential_type": "interactive",
            },
        ),
        EdgeData(
            source="user_alice",
            target="grp_it_admins",
            type=EdgeType.MEMBER_OF,
            weight=1.0,
            attributes={
                "membership": "direct",
            },
        ),
        EdgeData(
            source="grp_it_admins",
            target="app_srv_01",
            type=EdgeType.ADMIN_ON,
            weight=2.0,
            attributes={
                "access_path": "domain_admin_tools",
            },
        ),
        EdgeData(
            source="ws_001",
            target="zone_user",
            type=EdgeType.NETWORK_REACHABLE,
            weight=1.0,
            attributes={
                "protocol": "internal_routing",
            },
        ),
        EdgeData(
            source="zone_user",
            target="zone_server",
            type=EdgeType.TRUSTS,
            weight=1.5,
            attributes={
                "trust_type": "allowed_traffic_path",
            },
        ),
        EdgeData(
            source="ws_001",
            target="app_srv_01",
            type=EdgeType.NETWORK_REACHABLE,
            weight=1.0,
            attributes={
                "port": 3389,
                "protocol": "tcp",
            },
        ),
        EdgeData(
            source="ws_001",
            target="app_srv_01",
            type=EdgeType.CAN_RDP_TO,
            weight=2.0,
            attributes={
                "port": 3389,
                "protocol": "rdp",
            },
        ),
        EdgeData(
            source="app_srv_01",
            target="db_prod_01",
            type=EdgeType.NETWORK_REACHABLE,
            weight=1.0,
            attributes={
                "port": 1433,
                "protocol": "tcp",
            },
        ),
        EdgeData(
            source="app_srv_01",
            target="db_prod_01",
            type=EdgeType.EXPLOITS,
            weight=3.0,
            attributes={
                "cve": "CVE-2026-0001",
                "exploit_success_prob": 0.7,
                "detection_prob": 0.9,
            },
        ),
        EdgeData(
            source="db_prod_01",
            target="backup_01",
            type=EdgeType.NETWORK_REACHABLE,
            weight=1.0,
            attributes={
                "protocol": "backup_sync",
            },
        ),
    ]

    return nodes, edges