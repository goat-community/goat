# Standard library imports
import asyncio
from typing import AsyncGenerator, Generator

# Third party imports
import pytest
import pytest_asyncio
from httpx import AsyncClient

# Local application imports
from routing.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
