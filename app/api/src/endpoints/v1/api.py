from fastapi import APIRouter

from src.endpoints.v1 import (
    customizations,
    isochrones,
    layers,
    login,
    organizations,
    roles,
    scenarios,
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["Login"])

api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(customizations.router, prefix="/customizations", tags=["Customizations"])
api_router.include_router(utils.router, prefix="/utils", tags=["Utils"])


# Isochrone endpoints
api_router.include_router(isochrones.router, prefix="/isochrones", tags=["Isochrones"])
# Scenario endpoints
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])

# LAYER: Vector tile endpoints.
layer_tiles_prefix = "/layers/tiles"
layer_tiles = layers.VectorTilerFactory(
    router_prefix=layer_tiles_prefix,
    with_tables_metadata=True,
    with_functions_metadata=True,
    with_viewer=True,
)
api_router.include_router(layer_tiles.router, prefix=layer_tiles_prefix, tags=["Layers: Tiles"])
