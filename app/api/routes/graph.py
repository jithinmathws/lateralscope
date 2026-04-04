from fastapi import APIRouter, Depends

from app.api.deps import get_service
from app.schemas.graph import GraphSummaryResponse
from app.services.graph_service import GraphService

router = APIRouter(tags=["graph"])


@router.get(
    "/graph/summary",
    response_model=GraphSummaryResponse,
    summary="Get graph summary",
    description="Returns structural metadata about the loaded enterprise graph, including node counts, edge counts, and type distributions.",
)
def get_graph_summary(
    service: GraphService = Depends(get_service),
) -> GraphSummaryResponse:
    summary = service.summary

    return GraphSummaryResponse(
        node_count=summary.node_count,
        edge_count=summary.edge_count,
        node_types=summary.node_types,
        edge_types=summary.edge_types,
        has_isolated_nodes=summary.has_isolated_nodes,
    )