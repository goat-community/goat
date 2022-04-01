import asyncio
from typing import Dict, Generator, Optional

import pytest
from httpx import AsyncClient

from src.db.session import async_session
from src.main import app
from src.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session")
def event_loop():
    yield asyncio.get_event_loop()


@pytest.fixture(scope="session")
async def db() -> Generator:
    async with async_session() as session:
        yield session


@pytest.fixture(scope="module")
async def client() -> Generator:
    async with AsyncClient(app=app, base_url="http://localhost:5000") as c:
        yield c


@pytest.fixture(scope="module")
async def superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    return await get_superuser_token_headers(client)
