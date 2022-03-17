from fastapi import FastAPI
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings

engine = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
legacy_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, future=False)

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
