from typing import Dict

from pydantic import BaseModel, Field


class GraphSummaryResponse(BaseModel):
    node_count: int = Field(..., description="Total number of nodes in the enterprise graph.")
    edge_count: int = Field(..., description="Total number of edges in the enterprise graph.")
    node_types: Dict[str, int] = Field(
        ...,
        description="Distribution of nodes by node type.",
    )
    edge_types: Dict[str, int] = Field(
        ...,
        description="Distribution of edges by edge type.",
    )
    has_isolated_nodes: bool = Field(
        ...,
        description="Whether the graph contains isolated nodes with no relationships.",
    )