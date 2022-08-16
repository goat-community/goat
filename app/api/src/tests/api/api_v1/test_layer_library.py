from typing import Dict

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.schemas.layer_library import request_examples
from src.tests.utils.layer_library import (
    create_random_layer_library,
    create_random_style_library,
)
from src.tests.utils.utils import random_lower_string

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


async def test_delete_layer_libraries(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_layers = [await create_random_layer_library(db=db) for i in range(2)]
    random_layer_names = [layer.name for layer in random_layers]
    r = await client.request(
        "DELETE",
        f"{settings.API_V1_STR}/config/layers/library",
        headers=superuser_token_headers,
        json=random_layer_names,
    )

    assert 200 <= r.status_code < 300

    for random_layer in random_layers:
        # Try to get
        r = await client.get(
            f"{settings.API_V1_STR}/config/layers/library/{random_layer.name}",
            headers=superuser_token_headers,
        )

        assert r.status_code == 404

        # Try to delete again


async def test_read_styles_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    await create_random_style_library(db=db)
    await create_random_style_library(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/library/styles", headers=superuser_token_headers
    )
    assert 200 <= r.status_code < 300
    styles = r.json()
    assert len(styles) > 1


async def test_get_style_library_by_name(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_style = await create_random_style_library(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/layers/library/styles/{random_style.name}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    retrieved_style = r.json()
    assert retrieved_style.get("name") == random_style.name


async def test_create_style_library(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_style = request_examples.single_style_library
    r = await client.post(
        f"{settings.API_V1_STR}/config/layers/library/styles",
        headers=superuser_token_headers,
        json=random_style,
    )
    assert 200 <= r.status_code < 300
    retrieved_style = r.json()
    assert retrieved_style.get("name") == random_style.get("name")
    assert retrieved_style.get("id")


async def test_create_wrong_style_library_untranslated_rule(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_style = request_examples.single_style_library

    # Change one of rules to get 400 error
    random_style["style"]["rules"][0]["name"] = random_lower_string()

    r = await client.post(
        f"{settings.API_V1_STR}/config/layers/library/styles",
        headers=superuser_token_headers,
        json=random_style,
    )
    assert 400 <= r.status_code < 500


async def test_create_wrong_style_library_additional_language(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:

    # Test against additional translation language
    random_style = request_examples.single_style_library

    # Get the name of first rule
    first_rule_name = random_style["style"]["rules"][0]["name"]
    random_style["translation"][first_rule_name][random_lower_string()] = random_lower_string()

    r = await client.post(
        f"{settings.API_V1_STR}/config/layers/library/styles",
        headers=superuser_token_headers,
        json=random_style,
    )
    assert 400 <= r.status_code < 500


async def test_update_style_library(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_style = await create_random_style_library(db=db)
    style_name = random_style.name
    random_style.name += "_updated"
    r = await client.put(
        f"{settings.API_V1_STR}/config/layers/library/styles/{style_name}",
        headers=superuser_token_headers,
        json=jsonable_encoder(random_style),
    )
    assert 200 <= r.status_code < 300
    retrieved_style = r.json()
    assert retrieved_style.get("name") == random_style.name
    assert retrieved_style.get("id")


async def test_delete_style_libraries(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    random_styles = [await create_random_style_library(db=db) for i in range(2)]
    random_style_names = [style.name for style in random_styles]
    r = await client.request(
        "DELETE",
        f"{settings.API_V1_STR}/config/layers/library/styles",
        headers=superuser_token_headers,
        json=random_style_names,
    )

    assert 200 <= r.status_code < 300
    for random_style in random_styles:
        # Try to get
        r = await client.get(
            f"{settings.API_V1_STR}/config/layers/library/styles/{random_style.name}",
            headers=superuser_token_headers,
        )

        assert r.status_code == 404
