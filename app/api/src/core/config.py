import secrets
from typing import Any, Dict, List, Optional, Union

import boto3
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


# For old versions of SQLAlchemy (< 1.4)
class SyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgresql", "postgresql+psycopg2", "postgresql+pg8000"}


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    CACHE_PATH: str = "/app/src/cache"
    API_SECRET_KEY: str = secrets.token_urlsafe(32)
    AWS_ACCESS_KEY_ID: Optional[str] = ""
    AWS_SECRET_ACCESS_KEY: Optional[str] = ""
    AWS_REGION: Optional[str] = "eu-central-1"
    AWS_BUCKET_NAME: Optional[str] = "plan4better-data"
    S3_CLIENT: Optional[Any] = None

    @validator("S3_CLIENT", pre=True)
    def assemble_s3_client(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return boto3.client(
            "s3",
            aws_access_key_id=values.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=values.get("AWS_SECRET_ACCESS_KEY"),
            region_name=values.get("AWS_REGION"),
        )

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:1024",
        "https://dashboard.plan4better.de",
        "https://dashboard-dev.plan4better.de",
        "https://citizens.plan4better.de",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @validator("POSTGRES_DB", pre=True)
    def set_db_name_according_to_project_name_if_empty(cls, v, values):
        if not v and values.get("COMPOSE_PROJECT_NAME"):
            return values["COMPOSE_PROJECT_NAME"]
        return v

    POSTGRES_DATABASE_URI: str = None

    @validator("POSTGRES_DATABASE_URI", pre=True)
    def postgres_database_uri_(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return f'postgresql://{values.get("POSTGRES_USER")}:{values.get("POSTGRES_PASSWORD")}@{values.get("POSTGRES_SERVER")}:5432/{values.get("POSTGRES_DB")}'

    ASYNC_SQLALCHEMY_DATABASE_URI: Optional[AsyncPostgresDsn] = None

    @validator("ASYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SQLALCHEMY_DATABASE_URI: Optional[SyncPostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return SyncPostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    SRC_DIR: str = "/app/src"
    CACHE_DIR: str = "/app/src/cache"
    EMAIL_TEMPLATES_DIR: str = "/app/src/templates/email/build"
    LAYER_TEMPLATES_DIR: str = "/app/src/templates/layer"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("EMAILS_FROM_EMAIL")
        )

    POSTGRES_FUNCTIONS_SCHEMA: Optional[str] = "basic"

    # Tile / Table config
    TILE_RESOLUTION: int = 4096
    TILE_BUFFER: int = 256
    MAX_FEATURES_PER_TILE: int = 10000
    DEFAULT_MINZOOM: int = 0
    DEFAULT_MAXZOOM: int = 22
    # R5 config
    R5_HOST: str = None
    R5_MONGO_DB_URL: Optional[str] = None

    @validator("R5_MONGO_DB_URL", pre=True)
    def r5_mongodb_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        # mongodb://172.17.0.1:27017/analysis
        return f'mongodb://{values.get("R5_HOST")}:27017/analysis'

    R5_API_PORT: Optional[int] = 80
    R5_API_URL: Optional[str] = None

    @validator("R5_API_URL", pre=True)
    def r5_api_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return f'http://{values.get("R5_HOST")}:{values.get("R5_API_PORT")}/api'

    R5_AUTHORIZATION: str = None

    @validator("R5_AUTHORIZATION", pre=True)
    def r5_authorization(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v:
            return f"Basic {v}="
        return None

    # path_traveltime_matrices
    TRAVELTIME_MATRICES_PATH: str = "/app/src/cache/traveltime_matrices"
    OPPORTUNITY_MATRICES_PATH: str = "/app/src/cache/opportunity_matrices"
    AGGREGATING_MATRICES_PATH: str = "/app/src/cache/opportunity/grid"
    ANALYSIS_UNIT_PATH: str = "/app/src/cache/analysis_unit"
    OPPORTUNITY_PATH: str = "/app/src/cache/opportunity"

    HEATMAP_MULTIPROCESSING_BULK_SIZE = 50

    # Celery config
    CELERY_BROKER_URL: Optional[str] = ""
    CELERY_CONFIG: Optional[dict] = {}

    @validator("CELERY_CONFIG", pre=True)
    def celery_broker_config(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        celery_broker_url = values.get("CELERY_BROKER_URL")
        aws_region = values.get("AWS_REGION")
        if celery_broker_url == "sqs://":
            return {
                "broker_transport_options": {"region": aws_region or "eu-central-1"},
            }
        else:
            return {}

    CELERY_TASK_TIME_LIMIT: Optional[int] = 60  # seconds

    OPENROUTESERVICE_API_KEY: Optional[str] = None
    GEOAPIFY_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GITHUB_ACCESS_TOKEN: Optional[str] = None

    COMPOSE_PROJECT_NAME: Optional[str] = None
    SAMPLE_AUTHORIZATION = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0OG80Z1JXelh3YXBTY3NTdHdTMXZvREFJRlNOa0NtSVFpaDhzcEJTc2kwIn0.eyJleHAiOjE2OTEwMDQ1NTYsImlhdCI6MTY5MTAwNDQ5NiwiYXV0aF90aW1lIjoxNjkxMDAyNjIzLCJqdGkiOiI1MjBiN2RhNC0xYmM0LTRiM2QtODY2ZC00NDU0ODY2YThiYjIiLCJpc3MiOiJodHRwczovL2Rldi5hdXRoLnBsYW40YmV0dGVyLmRlL3JlYWxtcy9tYXN0ZXIiLCJzdWIiOiI3NDRlNGZkMS02ODVjLTQ5NWMtOGIwMi1lZmViY2U4NzUzNTkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJzZWN1cml0eS1hZG1pbi1jb25zb2xlIiwibm9uY2UiOiJjNGIzMDQ3Yi0xODVmLTQyOWEtOGZlNS1lNDliNTVhMzE3MzIiLCJzZXNzaW9uX3N0YXRlIjoiMzk5ZTc2NWMtYjM1MC00NDEwLTg4YTMtYjU5NDIyMmJkZDlhIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2Rldi5hdXRoLnBsYW40YmV0dGVyLmRlIl0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJzaWQiOiIzOTllNzY1Yy1iMzUwLTQ0MTAtODhhMy1iNTk0MjIyYmRkOWEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InA0YiJ9.mjywr9Dv19egsXwM1fK6g3sZ0trk87X0tEfK7oOizuBuCdkr6PZN1Eg58FCdjIgEBXqjltOWV43UIkXde4iPVa-KU5Q34Qjv6w0STa3Aq9vFbaUfSm_690qCdr8XSKMJUWQXWYwD2cjck5UCqf7-QqsF2Ab56i40_CJLZkJOi25WKIC855qPDi8BkJgh5eWoxobdyCbwJMEeoM-3QnxY5ikib5a2_AASEN3_5MYmT6-fvpW2t-MS6u4vtcG-WfqriK8YNoGPS2a1pFjLqQLHkM__j0O_t4wXP56x9yjkUdHCXqVcSlDvZYNWrv5CLqecqjOoliNMs6RTu9gV0Gr-cA"

    class Config:
        case_sensitive = True


settings = Settings()
