import asyncio
from typing import Dict, Generator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session
from src.main import app
from src.tests.utils.utils import get_superuser_token_headers
from src.tests.utils.user import get_user_token_headers


@pytest_asyncio.fixture(scope="session")
def event_loop():
    yield asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def db() -> Generator:
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="module")
async def client() -> Generator:
    async with AsyncClient(app=app, base_url="http://localhost:5000") as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    return await get_superuser_token_headers(client)

@pytest_asyncio.fixture(scope="module")
async def normal_user_token_headers(client: AsyncClient, db: AsyncSession) -> Dict[str, str]:
    return await get_user_token_headers(client=client, db=db)
