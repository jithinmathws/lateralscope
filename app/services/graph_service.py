from functools import lru_cache
from pathlib import Path

from app.analysis.blast_radius import BlastRadiusEngine
from app.graph.builders.enterprise_graph_builder import EnterpriseGraphBuilder
from app.graph.loaders.graph_data_loader import GraphDataLoader
from app.services.simulation_service import SimulationService


class GraphService:
    """
    Loads enterprise graph data from JSON files,
    builds the graph, and exposes analysis services.
    """

    def __init__(self) -> None:
        builder = EnterpriseGraphBuilder()
        loader = GraphDataLoader(self._data_dir())

        nodes = loader.load_nodes()
        edges = loader.load_edges()

        self.graph = builder.build_graph(nodes=nodes, edges=edges)
        self.summary = builder.summarize(self.graph)
        self.simulation_service = SimulationService(self.graph)
        self.blast_radius_engine = BlastRadiusEngine(self.graph)

    def _data_dir(self) -> Path:
        return Path(__file__).resolve().parents[2] / "data"


@lru_cache
def get_graph_service() -> GraphService:
    return GraphService()