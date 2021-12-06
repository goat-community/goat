import numpy as np
import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.asyncio
from app.api.api_v1.api import layer_tiles_prefix


# ======VECTOR TILE TESTING=====
async def test_tilematrix(client: AsyncClient) -> None:
    """test /tileMatrixSet endpoint."""
    response = await client.get(f"{settings.API_V1_STR}{layer_tiles_prefix}/tileMatrixSets")
    assert response.status_code == 200
    body = response.json()

    assert len(body["tileMatrixSets"]) == 13  # morecantile has 13 defaults
    tms = list(filter(lambda m: m["id"] == "WebMercatorQuad", body["tileMatrixSets"]))[0]
    assert (
        tms["links"][0]["href"]
        == f"http://test{settings.API_V1_STR}{layer_tiles_prefix}/tileMatrixSets/WebMercatorQuad"
    )


async def test_tilematrixInfo(client: AsyncClient):
    """test /tileMatrixSet endpoint."""
    response = await client.get(
        f"{settings.API_V1_STR}{layer_tiles_prefix}/tileMatrixSets/WebMercatorQuad"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "TileMatrixSetType"
    assert body["identifier"] == "WebMercatorQuad"
