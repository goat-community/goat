from fastapi import APIRouter

from . import health, routing

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["System"])
router.include_router(routing.router, prefix="/routing", tags=["Routing"])
