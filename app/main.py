from fastapi import FastAPI

from app.api.routes.graph import router as graph_router
from app.api.routes.health import router as health_router
from app.api.routes.simulation import router as simulation_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="LateralScope API",
        version="0.1.0",
        description="Graph-based cyber attack path and blast radius simulation API.",
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(graph_router, prefix="/api")
    app.include_router(simulation_router, prefix="/api")

    return app


app = create_app()