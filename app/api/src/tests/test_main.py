"""Test main.app."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_health(client: AsyncClient) -> None:
    """Test /healthz endpoint."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
