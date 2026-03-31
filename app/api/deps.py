from app.services.graph_service import GraphService, get_graph_service


def get_service() -> GraphService:
    return get_graph_service()