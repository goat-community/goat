from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    isochrones,
    items,
    login,
    scenarios,
    users,
    utils,
    vectortiles,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(utils.router, prefix="/utils", tags=["Utils"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])

# Isochrone endpoints
api_router.include_router(isochrones.router, prefix="/isochrones", tags=["Isochrones"])
# Scenario endpoints
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
# Vector tile endpoints.
mvt_tiler = vectortiles.VectorTilerFactory(
    with_tables_metadata=True,
    with_functions_metadata=True,
    with_viewer=True,
)
api_router.include_router(mvt_tiler.router)

tms = vectortiles.TMSFactory()
api_router.include_router(tms.router, tags=["TileMatrixSets"])
