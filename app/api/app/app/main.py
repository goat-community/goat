from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app import crud
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.session import (
    _buildpg_close_db_connection,
    _buildpg_connect_to_db,
    async_session,
)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_event():
    print("App is starting...")
    async with async_session() as db:
        table_index = await crud.layer.table_index(db)
        app.state.table_catalog = table_index
    await _buildpg_connect_to_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await _buildpg_close_db_connection(app)


@app.get("/healthz", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {"ping": "pong!"}


app.include_router(api_router, prefix=settings.API_V1_STR)
