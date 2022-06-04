from fastapi import APIRouter

from src.endpoints.v1 import (
    customizations,
    heatmap,
    isochrones,
    layer_library,
    layers,
    login,
    organizations,
    poi_aoi,
    roles,
    scenarios,
    static_layers,
    upload,
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
api_router.include_router(upload.router, prefix="/custom-data", tags=["Custom Data"])
api_router.include_router(isochrones.router, prefix="/isochrones", tags=["Isochrones"])
api_router.include_router(heatmap.router, prefix="/heatmap", tags=["Heatmap"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(poi_aoi.router, prefix="/pois-aois", tags=["POIs and AOIs"])
api_router.include_router(
    static_layers.router, prefix="/layers/vector", tags=["Static vector layers"]
)

# LAYER: Vector tile endpoints.
layer_tiles_prefix = "/layers/tiles"
layer_tiles = layers.VectorTilerFactory(
    router_prefix=layer_tiles_prefix,
    with_tables_metadata=True,
    with_functions_metadata=False,
    with_viewer=False,
)

api_router.include_router(layer_tiles.router, prefix=layer_tiles_prefix, tags=["Layers"])
api_router.include_router(layer_library.router, prefix="/layers/library", tags=["Layer Library"])
