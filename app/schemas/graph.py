from typing import Dict

from pydantic import BaseModel


class GraphSummaryResponse(BaseModel):
    node_count: int
    edge_count: int
    node_types: Dict[str, int]
    edge_types: Dict[str, int]
    has_isolated_nodes: bool