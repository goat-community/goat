"""
---------------------------------------------------------------------------------
This code is based on or incorporates material from the project:
https://github.com/developmentseed/tipg

The original code/repository is licensed under MIT License.
---------------------------------------------------------------------------------
"""
import os
from contextlib import asynccontextmanager

import sentry_sdk
from tipg import __version__ as tipg_version
from tipg import dependencies
from tipg.collections import Collection

from .exts import (
    Operator as OperatorPatch,
)
from .exts import (
    _from,
    _select_no_geo,
    _where,
    filter_query,
    get_column,
    get_mvt_point,
    get_tile,
    single_select_h3,
)

# Monkey patch filter query here because it needs to be patched before used by import down
dependencies.filter_query = filter_query

from fastapi import FastAPI  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402
from starlette_cramjam.middleware import CompressionMiddleware  # noqa: E402
from tipg.database import close_db_connection, connect_to_db  # noqa: E402
from tipg.factory import Endpoints  # noqa: E402
from tipg.filter.filters import Operator  # noqa: E402
from tipg.middleware import CacheControlMiddleware  # noqa: E402
from tipg.settings import (  # noqa: E402
    APISettings,
    CustomSQLSettings,
    DatabaseSettings,
    MVTSettings,
    PostgresSettings,
)

from .catalog import LayerCatalog  # noqa: E402

mvt_settings = MVTSettings()
mvt_settings.max_features_per_tile = 20000
settings = APISettings()
postgres_settings = PostgresSettings()
db_settings = DatabaseSettings()
custom_sql_settings = CustomSQLSettings()


if os.getenv("SENTRY_DSN") and os.getenv("ENVIRONMENT"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("ENVIRONMENT"),
        traces_sample_rate=1.0 if os.getenv("ENVIRONMENT") == "prod" else 0.1,
    )

# Monkey patch the function that need modification
Operator.OPERATORS = OperatorPatch.OPERATORS
Collection._from = _from
Collection.get_mvt_point = get_mvt_point
Collection.single_select_h3 = single_select_h3
Collection._where = _where
Collection._select_no_geo = _select_no_geo
Collection.get_column = get_column
Collection.get_tile = get_tile


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan."""
    # Create Connection Pool
    await connect_to_db(
        app,
        settings=postgres_settings,
        schemas=db_settings.schemas,
        user_sql_files=custom_sql_settings.sql_files,
    )
    # Init Layer Catalog
    layer_catalog = LayerCatalog(app=app)
    await layer_catalog.start()
    yield
    await layer_catalog.stop()
    await close_db_connection(app)


# Create FastAPI app
app = FastAPI(
    title=settings.name,
    version=tipg_version,
    openapi_url="/api",
    docs_url="/api.html",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

# Create Endpoints
ogc_api = Endpoints(
    title=settings.name,
    with_tiles_viewer=settings.add_tiles_viewer,
)
# Remove the list all collections endpoint
ogc_api.router.routes = ogc_api.router.routes[1:]
app.include_router(ogc_api.router)
app.add_middleware(CacheControlMiddleware, cachecontrol=settings.cachecontrol)
app.add_middleware(CompressionMiddleware)

@app.get(
    "/healthz",
    description="Health Check.",
    summary="Health Check.",
    operation_id="healthCheck",
    tags=["Health Check"],
)
def ping():
    """Health check."""
    return {"ping": "pongpong!"}
