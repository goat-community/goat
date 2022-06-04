from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.tests.utils.layer_library import create_random_layer_library

pytestmark = pytest.mark.asyncio


async def test_read_main(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    create_random_layer_library(db=db)
    create_random_layer_library(db=db)
    r = await client.get(f"{settings.API_V1_STR}/layers/library", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    layers = r.json()
    assert len(layers) > 1


async def test_read_layers_list_new(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    await create_random_layer_library(db=db)
    await create_random_layer_library(db=db)
    r = await client.get(f"{settings.API_V1_STR}/layers/library", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    layers = r.json()
    assert len(layers) > 1
