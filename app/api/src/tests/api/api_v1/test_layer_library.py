from typing import Dict

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.schemas.layer_library import request_examples
from src.tests.utils.layer_library import create_random_layer_library

pytestmark = pytest.mark.asyncio


async def test_read_layers_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    await create_random_layer_library(db=db)
    await create_random_layer_library(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/library", headers=superuser_token_headers
    )
    assert 200 <= r.status_code < 300
    layers = r.json()
    assert len(layers) > 1


async def test_get_layer_library_by_name(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_layer = await create_random_layer_library(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/library/{random_layer.name}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    retrieved_layer = r.json()
    assert retrieved_layer.get("name") == random_layer.name


async def test_create_layer_library(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_layer = request_examples.single_layer_library
    r = await client.post(
        f"{settings.API_V1_STR}/config/layers/library",
        headers=superuser_token_headers,
        json=random_layer,
    )
    assert 200 <= r.status_code < 300
    retrieved_layer = r.json()
    assert retrieved_layer.get("name") == random_layer.get("name")
    assert retrieved_layer.get("id")


async def test_update_layer_library(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_layer = await create_random_layer_library(db=db)
    layer_name = random_layer.name
    random_layer.name += "_updated"
    r = await client.put(
        f"{settings.API_V1_STR}/config/layers/library/{layer_name}",
        headers=superuser_token_headers,
        json=jsonable_encoder(random_layer),
    )
    assert 200 <= r.status_code < 300
    retrieved_layer = r.json()
    assert retrieved_layer.get("name") == random_layer.name
    assert retrieved_layer.get("id")


async def test_delete_layer_library(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_layer = await create_random_layer_library(db=db)
    r = await client.delete(
        f"{settings.API_V1_STR}/config/layers/library/{random_layer.name}",
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300

    # Try to get
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/library/{random_layer.name}",
        headers=superuser_token_headers,
    )

    assert r.status_code == 404

    # Try to delete again

    r = await client.delete(
        f"{settings.API_V1_STR}/config/layers/library/{random_layer.name}",
        headers=superuser_token_headers,
    )

    assert r.status_code == 404
