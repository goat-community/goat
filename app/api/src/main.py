import logging
import os

import sentry_sdk
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from src import crud, run_time_method_calls
from src.core.config import settings
from src.db.session import async_session, r5_mongo_db_client
from src.endpoints import deps
from src.endpoints.v1.api import api_router

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=os.getenv("NAMESPACE", "dev"),
    traces_sample_rate=0.2,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    redoc_url="/api/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        swagger_favicon_url="/static/api_favicon.png",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=settings.PROJECT_NAME,
        swagger_ui_parameters={"persistAuthorization": True}
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"],
    )


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    print("App is starting...")
    async with async_session() as db:
        table_index = await crud.layer.table_index(db)
        app.state.table_catalog = table_index

    if not os.environ.get("DISABLE_NUMBA_STARTUP_CALL") == "True":
        await run_time_method_calls.call_isochrones_startup(app=app)


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


@app.get("/api/status", description="Status Check", tags=["Health Check"])
async def status_check(db: AsyncSession = Depends(deps.get_db)):
    """Status check."""
    try:
        results = await crud.system.get_by_key(db, key="type", value="status")
        results = results[0]
    except Exception as e:
        return JSONResponse(status_code=503, content={"message": "Service Unavailable"})

    if results.setting.get("status") == "maintenance":
        return JSONResponse(status_code=503, content={"message": "Service Unavailable"})
    else:
        return {"status": "ok"}


# Calling this endpoint to see if the setup works. If yes, an error message will show in Sentry dashboard
@app.get("/api/sentry", include_in_schema=False)
async def sentry():
    raise Exception("Test sentry integration")


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(IntegrityError)
async def item_already_exists_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "message": "object with a unique field already exists.",
            "detail": str(exc.__dict__.get("orig")),
        },
    )

