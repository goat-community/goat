import contextlib
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncConnection,
    create_async_engine,
)


from src.core.config import settings

engine = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
legacy_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, future=False)
r5_mongo_db_client = AsyncIOMotorClient(str(settings.R5_MONGO_DB_URL))

sync_session = sessionmaker(
    bind=legacy_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_maker: sessionmaker | None = None

    def init(self, host: str):
        self._engine = create_async_engine(host, isolation_level="AUTOCOMMIT")
        self._session_maker = sessionmaker(
            bind=self._engine, autocommit=False, class_=AsyncSession
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

    async def close(self):
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

    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(SQLModel.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(SQLModel.metadata.drop_all)


session_manager = DatabaseSessionManager()
