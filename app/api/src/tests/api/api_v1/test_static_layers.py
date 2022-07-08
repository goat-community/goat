from typing import Dict

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.tests.utils.static_layer import create_static_layer

pytestmark = pytest.mark.asyncio


async def test_read_static_layer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    static_layer = await create_static_layer(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/vector/static/{static_layer.id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    data_frame = r.json().get("data_frame")
    assert len(data_frame) > 1


async def test_create_static_layer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    files = {
        "upload_file": (
            "sample.zip",
            open("/app/src/tests/data/sample.zip", "rb"),
            "application/zip",
        )
    }
    r = await client.post(
        f"{settings.API_V1_STR}/config/layers/vector/static",
        headers=superuser_token_headers,
        files=files,
    )
    assert 200 <= r.status_code < 300
    retrieved_layer = r.json()
    assert retrieved_layer.get("id")


async def test_create_wrong_static_layer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    files = {
        "upload_file": (
            "fail_file.zip",
            open("/app/src/tests/data/fail_file.zip", "rb"),
            "application/zip",
        )
    }
    r = await client.post(
        f"{settings.API_V1_STR}/config/layers/vector/static",
        headers=superuser_token_headers,
        files=files,
    )
    assert 400 <= r.status_code < 500


async def test_update_static_layer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    static_layer = await create_static_layer(db=db)
    files = {
        "upload_file": (
            "sample.zip",
            open("/app/src/tests/data/sample.zip", "rb"),
            "application/zip",
        )
    }
    r = await client.put(
        f"{settings.API_V1_STR}/config/layers/vector/static/{static_layer.id}",
        headers=superuser_token_headers,
        files=files,
    )
    assert 200 <= r.status_code < 300
    retrieved_layer = r.json()
    assert retrieved_layer.get("id") == static_layer.id
