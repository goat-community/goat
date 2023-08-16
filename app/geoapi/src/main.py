"""
---------------------------------------------------------------------------------
This code is based on or incorporates material from the project:
https://github.com/developmentseed/tipg

The original code/repository is licensed under MIT License.
---------------------------------------------------------------------------------
"""


from contextlib import asynccontextmanager
from tipg import __version__ as tipg_version
from tipg.collections import Collection
from tipg import dependencies
from src.exts import _from, _select_no_geo, get_column, filter_query, _where

# Monkey patch filter query here because it needs to be patched before used by import down
dependencies.filter_query = filter_query

from tipg.database import close_db_connection, connect_to_db
from tipg.factory import Endpoints
from tipg.middleware import CacheControlMiddleware
from tipg.settings import (
    APISettings,
    CustomSQLSettings,
    DatabaseSettings,
    PostgresSettings,
)
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_cramjam.middleware import CompressionMiddleware
from src.catalog import LayerCatalog


settings = APISettings()
postgres_settings = PostgresSettings()
db_settings = DatabaseSettings()
custom_sql_settings = CustomSQLSettings()

# Monkey patch the function that need modification
Collection._from = _from
Collection._where = _where
Collection._select_no_geo = _select_no_geo
Collection.get_column = get_column


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
    # Create Initial Layer Catalog
    layer_catalog = LayerCatalog()
    await layer_catalog.connect()
    app.state.collection_catalog = await layer_catalog.init()
    await layer_catalog.disconnect()

    # Listen to the layer_changes channel
    layer_catalog_listen = LayerCatalog(app.state.collection_catalog)
    await layer_catalog_listen.connect()
    await layer_catalog_listen.listen()

    yield

    # Unlisten to layer_changes channel and close the Connection Pool
    await layer_catalog_listen.unlisten()
    await layer_catalog_listen.disconnect()

    await close_db_connection(app)


# Create FastAPI app
app = FastAPI(
    title=settings.name,
    version=tipg_version,
    openapi_url="/api",
    docs_url="/api.html",
    lifespan=lifespan,
)
# Create Endpoints
ogc_api = Endpoints(
    title=settings.name,
    with_tiles_viewer=settings.add_tiles_viewer,
)
app.include_router(ogc_api.router)

# Set all CORS enabled origins
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
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
    return {"ping": "pong!"}
