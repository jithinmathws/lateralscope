from functools import lru_cache

from app.analysis.blast_radius import BlastRadiusEngine
from app.graph.builders.enterprise_graph_builder import EnterpriseGraphBuilder
from app.graph.types import EdgeData, EdgeType, NodeData, NodeType
from app.services.simulation_service import SimulationService


class GraphService:
    """
    Builds a small in-memory enterprise graph for API bootstrapping.
    Replace this later with file-backed loading.
    """

    def __init__(self) -> None:
        builder = EnterpriseGraphBuilder()

        nodes = self._load_nodes()
        edges = self._load_edges()

        self.graph = builder.build_graph(nodes=nodes, edges=edges)
        self.summary = builder.summarize(self.graph)
        self.simulation_service = SimulationService(self.graph)
        self.blast_radius_engine = BlastRadiusEngine(self.graph)

    def _load_nodes(self) -> list[NodeData]:
        return [
            NodeData(
                id="user_alice",
                type=NodeType.IDENTITY,
                label="Alice",
                attributes={"department": "Finance"},
            ),
            NodeData(
                id="group_it_admins",
                type=NodeType.GROUP,
                label="IT Admins",
                attributes={},
            ),
            NodeData(
                id="ws_001",
                type=NodeType.HOST,
                label="Workstation 001",
                attributes={"os": "Windows"},
            ),
            NodeData(
                id="app_srv_01",
                type=NodeType.HOST,
                label="App Server 01",
                attributes={"os": "Linux"},
            ),
            NodeData(
                id="db_prod_01",
                type=NodeType.CROWN_JEWEL,
                label="Production Database",
                attributes={"criticality": "high"},
            ),
        ]

    def _load_edges(self) -> list[EdgeData]:
        return [
            EdgeData(
                source="user_alice",
                target="group_it_admins",
                type=EdgeType.MEMBER_OF,
                weight=1.0,
                attributes={},
            ),
            EdgeData(
                source="group_it_admins",
                target="ws_001",
                type=EdgeType.ADMIN_ON,
                weight=1.0,
                attributes={},
            ),
            EdgeData(
                source="user_alice",
                target="ws_001",
                type=EdgeType.HAS_SESSION,
                weight=1.0,
                attributes={},
            ),
            EdgeData(
                source="ws_001",
                target="app_srv_01",
                type=EdgeType.CAN_RDP_TO,
                weight=1.0,
                attributes={},
            ),
            EdgeData(
                source="app_srv_01",
                target="db_prod_01",
                type=EdgeType.CAN_SSH_TO,
                weight=1.0,
                attributes={},
            ),
        ]


@lru_cache
def get_graph_service() -> GraphService:
    return GraphService()