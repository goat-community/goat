import contextlib
from typing import AsyncIterator

from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from core.core.config import settings


def engine_connect_args(url: str) -> dict:
    """`connect_args` for core's engines (the app's and the migrations').

    The session name operators see in pg_stat_activity: asyncpg takes server
    settings separately, psycopg as a libpq keyword. Behind a pooler in
    transaction mode a statement prepared on the server may be gone, or taken,
    on the next query's server connection, so psycopg prepares nothing there.
    SQLAlchemy's asyncpg dialect prepares every statement in a round trip of
    its own and can't be kept from it, so it is refused behind such a pooler.
    """
    driver = make_url(url).get_driver_name()
    if driver == "asyncpg":
        if settings.POSTGRES_TRANSACTION_POOLER:
            raise ValueError(
                "POSTGRES_TRANSACTION_POOLER needs the psycopg driver "
                "(postgresql+psycopg://) in ASYNC_SQLALCHEMY_DATABASE_URI"
            )
        return {"server_settings": {"application_name": "goat-core"}}
    args: dict = {"application_name": "goat-core"}
    if settings.POSTGRES_TRANSACTION_POOLER:
        args["prepare_threshold"] = None
    return args


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    def init(self, host: str | None) -> None:
        if not host:
            raise ValueError("Database host must be provided")

        self._engine = create_async_engine(
            host,
            connect_args=engine_connect_args(host),
            isolation_level="AUTOCOMMIT",
            pool_pre_ping=True,  # Check connection health before using
            pool_recycle=300,  # Recycle connections every 5 minutes
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Connect to the auth database and return a connection object.
        """
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise
            finally:
                await connection.close()

    async def close(self) -> None:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._session_maker = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_all(self, connection: AsyncConnection) -> None:
        await connection.run_sync(SQLModel.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection) -> None:
        # Use CASCADE to drop types and other dependent objects
        await connection.execute(text("DROP TYPE IF EXISTS assettype CASCADE"))
        await connection.run_sync(SQLModel.metadata.drop_all)


session_manager = DatabaseSessionManager()
