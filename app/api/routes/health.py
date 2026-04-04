from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns a simple health status for the LateralScope API service.",
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="LateralScope API")