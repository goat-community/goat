import logging
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sqlalchemy.exc import IntegrityError
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.db.session import r5_mongo_db_client, session_manager
from src.endpoints.v2.api import router as api_router_v2
from fastapi_pagination import add_pagination

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    session_manager.init(settings.ASYNC_SQLALCHEMY_DATABASE_URI)
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    yield
    print("Shutting down...")
    await session_manager.close()
    r5_mongo_db_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    redoc_url="/api/redoc",
    openapi_url=f"{settings.API_V2_STR}/openapi.json",
    lifespan=lifespan,
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        swagger_favicon_url="/static/api_favicon.png",
        openapi_url=f"{settings.API_V2_STR}/openapi.json",
        title=settings.PROJECT_NAME,
        swagger_ui_parameters={"persistAuthorization": True},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=os.getenv("NAMESPACE", "dev"),
    traces_sample_rate=0.2,
)

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


app.include_router(api_router_v2, prefix=settings.API_V2_STR)


@app.exception_handler(IntegrityError)
async def item_already_exists_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "message": "object with a unique field already exists.",
            "detail": str(exc.__dict__.get("orig")),
        },
    )
# add_pagination(app)
