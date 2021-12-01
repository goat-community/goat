from buildpg import asyncpg
from fastapi import FastAPI
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.testing.exclusions import future

from app.core.config import settings

engine = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
legacy_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, future=False, echo=True)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# FOR NON-ORM DB CONNECTIONS
async def _buildpg_connect_to_db(app: FastAPI) -> None:
    """Connect."""
    app.state.pool = await asyncpg.create_pool_b(
        settings.SQLALCHEMY_DATABASE_URI,
        min_size=1,
        max_size=10,
        max_queries=50000,
        max_inactive_connection_lifetime=300.0,
    )


async def _buildpg_close_db_connection(app: FastAPI) -> None:
    """Close connection."""
    await app.state.pool.close()
