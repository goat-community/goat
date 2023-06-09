from fastapi import APIRouter

from src.endpoints.v1 import (
    customizations,
    data_preparation,
    geostores,
    indicators,
    layer_library,
    layers,
    login,
    opportunities,
    opportunity_config,
    organizations,
    poi_aoi,
    r5,
    roles,
    scenarios,
    static_layers,
    static_layers_extra,
    study_area,
    system,
    upload,
    users,
    utils,
    projects,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(system.router, prefix="", tags=["Health Check"])

api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(customizations.router, prefix="/customizations", tags=["Customizations"])
api_router.include_router(utils.router, prefix="/utils", tags=["Utils"])
api_router.include_router(upload.router, prefix="/custom-data", tags=["Custom Data"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["Indicators"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(poi_aoi.router, prefix="/pois-aois", tags=["POIs and AOIs"])
api_router.include_router(
    static_layers.router, prefix="/read/table", tags=["Read Selected Tables"]
)
api_router.include_router(
    static_layers_extra.router, prefix="/config/layers/vector", tags=["Manage extra layers"]
)
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# LAYER: Vector tile endpoints.
layer_tiles_prefix = "/layers/tiles"
layer_tiles = layers.VectorTilerFactory(
    router_prefix=layer_tiles_prefix,
    with_tables_metadata=True,
    with_functions_metadata=False,
    with_viewer=False,
)

api_router.include_router(layer_tiles.router, prefix=layer_tiles_prefix, tags=["Layers"])
api_router.include_router(r5.router, prefix="/r5", tags=["PT-R5"])
api_router.include_router(
    layer_library.styles_router, prefix="/config/layers/library/styles", tags=["Layer Library"]
)
api_router.include_router(
    layer_library.router, prefix="/config/layers/library", tags=["Layer Library"]
)
api_router.include_router(study_area.router, prefix="/config/study-area", tags=["Layer Library"])
api_router.include_router(geostores.router, prefix="/config/geostores", tags=["Geostores"])
api_router.include_router(
    opportunities.router, prefix="/config/opportunities", tags=["Opportunities"]
)
api_router.include_router(data_preparation.router, prefix="/config/data-preparation", tags=["Data Preparation"])
api_router.include_router(
    opportunity_config.router, prefix="/config/opportunity-study-area", tags=["Opportunities"]
)

