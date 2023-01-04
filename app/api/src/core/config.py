import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


# For old versions of SQLAlchemy (< 1.4)
class SyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgresql", "postgresql+psycopg2", "postgresql+pg8000"}


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    API_SECRET_KEY: str = secrets.token_urlsafe(32)
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

    SMTP_TLS: Optional[bool] = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = "smtp.office365.com"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"].upper()
        return v

    EMAIL_TOKEN_EXPIRE_HOURS: int = 2
    EMAIL_TEMPLATES_DIR: str = "/app/src/templates/email/build"
    LAYER_TEMPLATES_DIR: str = "/app/src/templates/layer"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("EMAILS_FROM_EMAIL")
        )

    FIRST_ORGANIZATION: str
    FIRST_SUPERUSER_NAME: str
    FIRST_SUPERUSER_SURNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: Optional[str] = "administrator@plan4better.de"
    FIRST_SUPERUSER_STORAGE: Optional[int] = 500000  # In kilobytes
    FIRST_SUPERUSER_ACTIVE_STUDY_AREA_ID: int = 91620000
    FIRST_SUPERUSER_ACTIVE_DATA_UPLOAD_IDS: List[int] = []
    FIRST_SUPERUSER_LIMIT_SCENARIOS: int = 50
    FIRST_SUPERUSER_LANGUAGE_PREFERENCE: str = "en"

    POSTGRES_DB_STAGING: Optional[str] = "goat"
    POSTGRES_SERVER_STAGING: Optional[str] = "localhost"
    POSTGRES_USER_STAGING: Optional[str] = "postgres"
    POSTGRES_PASSWORD_STAGING: Optional[str] = "secret"
    POSTGRES_OUTER_PORT_STAGING: Optional[int] = 5432

    POSTGRES_FUNCTIONS_SCHEMA: Optional[str] = "basic"

    DEMO_USER_STUDY_AREA_ID: Optional[int] = 91620000  # Munich
    DEMO_USER_SCENARIO_LIMIT: Optional[int] = 5
    DEMO_USER_STORAGE: Optional[int] = 0  # In kilobytes
    DEMO_USER_DEACTIVATION_DAYS: Optional[int] = 30
    USERS_OPEN_REGISTRATION: bool = False
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

    R5_API_URL: Optional[str] = None

    # path_traveltime_matrices
    TRAVELTIME_MATRICES_PATH: str = "/app/src/cache/traveltime_matrices"
    OPPORTUNITY_MATRICES_PATH: str = "/app/src/cache/opportunity_matrices"

    @validator("R5_API_URL", pre=True)
    def r5_api_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return f'http://{values.get("R5_HOST")}/api'

    R5_AUTHORIZATION: str = None

    @validator("R5_AUTHORIZATION", pre=True)
    def r5_authorization(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return f"Basic {v}="

    class Config:
        case_sensitive = True


settings = Settings()
