from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings
from typing_extensions import Self


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


# For old versions of SQLAlchemy (< 1.4)
class SyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgresql", "postgresql+psycopg2", "postgresql+pg8000"}


class Settings(BaseSettings):
    # Monitoring
    SENTRY_DSN: str | None = None
    ENVIRONMENT: str | None = "dev"

    CUSTOMER_SCHEMA: str = "customer"
    USER_DATA_SCHEMA: str = "user_data"

    API_V2_STR: str = "/api/v2"
    PROJECT_NAME: str = "GOAT Routing API"
    CACHE_DIR: str = "/tmp/cache"

    NETWORK_REGION_TABLE: str = "basic.geofence_active_mobility"

    CATCHMENT_AREA_CAR_BUFFER_DEFAULT_SPEED: int = 80  # km/h
    CATCHMENT_AREA_HOLE_THRESHOLD_SQM: int = 200000  # 20 hectares, ~450m x 450m

    BASE_STREET_NETWORK: str | None = "903ecdca-b717-48db-bbce-0219e41439cf"
    DEFAULT_STREET_NETWORK_NODE_LAYER_PROJECT_ID: int = (
        37319  # Hardcoded until node layers are added to GOAT projects by default
    )

    DATA_INSERT_BATCH_SIZE: int = 800

    CELERY_BROKER_URL: str | None = "pyamqp://guest@rabbitmq//"
    REDIS_HOST: str | None = "redis"
    REDIS_PORT: int | None = 6379
    REDIS_DB: int | None = 0

    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: int | None = 5432
    POSTGRES_DATABASE_URI: str = ""
    ASYNC_SQLALCHEMY_DATABASE_URI: AsyncPostgresDsn | None = None
    SQLALCHEMY_DATABASE_URI: SyncPostgresDsn | None = None

    @model_validator(mode="after")
    def _postgres_database_uri(self) -> Self:
        if not self.POSTGRES_DATABASE_URI:
            self.POSTGRES_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        if not self.ASYNC_SQLALCHEMY_DATABASE_URI:
            self.ASYNC_SQLALCHEMY_DATABASE_URI = AsyncPostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB or ''}",
            )

        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = SyncPostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB or ''}",
            )
        return self

    class Config:
        case_sensitive = True


settings = Settings()
