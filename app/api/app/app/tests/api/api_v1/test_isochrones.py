import numpy as np
import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.asyncio
from app.api.api_v1.api import layer_tiles_prefix


# ======VECTOR TILE TESTING=====
async def test_isochrone_(client: AsyncClient) -> None:
    """test /isochrones endpoint."""
    response = await client.get(f"{settings.API_V1_STR}{layer_tiles_prefix}/isochrones")
    assert response.status_code == 200
    body = response.json()

    assert body["area"] > 0.1



async def test_tilematrixInfo(client: AsyncClient):
    """test /tileMatrixSet endpoint."""
    response = await client.get(
        f"{settings.API_V1_STR}{layer_tiles_prefix}/tileMatrixSets/WebMercatorQuad"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "TileMatrixSetType"
    assert body["identifier"] == "WebMercatorQuad"
