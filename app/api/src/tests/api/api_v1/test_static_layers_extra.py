import mimetypes
from typing import Dict

import pytest
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
    data = r.json()
    assert data["id"] == static_layer.id


async def test_read_static_layer_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    await create_static_layer(db=db)
    await create_static_layer(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/vector/static/",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    data = r.json()
    assert len(data) > 1


async def test_create_valid_static_layer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    valid_files = [
        "sample_no_directories.zip",
        "sample_single_directory.zip",
        "contain_geojson.zip",
        "valid_data.geojson",
    ]
    for file_name in valid_files:
        print(file_name)
        mimetype = mimetypes.guess_type(file_name)
        files = {
            "upload_file": (
                file_name,
                open(f"/app/src/tests/data/static_layer_upload_files/{file_name}", "rb"),
                mimetype[0],
            )
        }
        r = await client.post(
            f"{settings.API_V1_STR}/config/layers/vector/static",
            headers=superuser_token_headers,
            files=files,
        )
        retrieved_layer = r.json()
        print(retrieved_layer)
        assert 200 <= r.status_code < 300
        assert retrieved_layer.get("id")


async def test_create_wrong_static_layer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    invalid_files = [
        "sample_multiple_directories.zip",
        "invalid_no_csr.zip",
    ]
    for file_name in invalid_files:
        files = {
            "upload_file": (
                file_name,
                open(f"/app/src/tests/data/static_layer_upload_files/{file_name}", "rb"),
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
    valid_files = [
        "sample_no_directories.zip",
        "sample_single_directory.zip",
        "contain_geojson.zip",
        "valid_data.geojson",
    ]
    for file_name in valid_files:
        mimetype = mimetypes.guess_type(file_name)
        files = {
            "upload_file": (
                file_name,
                open(f"/app/src/tests/data/static_layer_upload_files/{file_name}", "rb"),
                mimetype[0],
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


async def test_delete_static_layers(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    static_layers = [await create_static_layer(db=db) for i in range(2)]
    static_layer_ids = [layer.id for layer in static_layers]
    r = await client.request(
        "DELETE",
        f"{settings.API_V1_STR}/config/layers/vector/static",
        headers=superuser_token_headers,
        json=static_layer_ids,
    )
    assert 200 <= r.status_code < 300
    for static_layer in static_layers:
        r = await client.get(
            f"{settings.API_V1_STR}/config/layers/vector/static/{static_layer.id}",
            headers=superuser_token_headers,
        )

        assert r.status_code == 404
