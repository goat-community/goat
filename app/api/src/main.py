import os

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware

from src import crud
from src.core.config import settings
from src.db.session import async_session, r5_mongo_db_client
from src.endpoints.v1.api import api_router

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=os.getenv("NAMESPACE", "dev"),
    traces_sample_rate=0.2,
)


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    swagger_ui_parameters={"persistAuthorization": True},
)


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


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    print("App is shutting down...")
    r5_mongo_db_client.close()


try:
    app.add_middleware(SentryAsgiMiddleware)
except Exception:
    # pass silently if the Sentry integration failed
    pass


@app.get("/api/healthz", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {"ping": "pong!"}


# Calling this endpoint to see if the setup works. If yes, an error message will show in Sentry dashboard
@app.get("/api/sentry", include_in_schema=False)
async def sentry():
    raise Exception("Test sentry integration")


app.include_router(api_router, prefix=settings.API_V1_STR)
