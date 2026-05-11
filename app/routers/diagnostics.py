from fastapi import APIRouter, Request
import time

from app.models.schemas import (
    HealthResponse,
    ComponentHealth,
    ServiceStatus,
)
from app.services.redis_client import redis_client

router = APIRouter()


@router.get("")
async def health_check(request: Request):
    uptime = round(time.time() - request.app.state.start_time, 2)

    redis_status = ComponentHealth(
        status=ServiceStatus.healthy if redis_client.is_available else ServiceStatus.degraded,
        detail="Connected" if redis_client.is_available else "Unavailable"
    )

    overall = (
        ServiceStatus.healthy
        if redis_client.is_available
        else ServiceStatus.degraded
    )

    return HealthResponse(
        status=overall,
        version="1.0.0",
        uptime_seconds=uptime,
        components={
            "redis": redis_status
        }
    )


@router.get("/live")
async def liveness():
    return {"status": "alive"}


@router.get("/ready")
async def readiness():
    return {"status": "ready"}
