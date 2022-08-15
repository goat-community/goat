from typing import Dict

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.schemas.opportunity_config import request_examples
from src.tests.utils.opportunity_config import create_random_opportunity_config

pytestmark = pytest.mark.asyncio


async def test_read_opportunity_configs_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    await create_random_opportunity_config(db=db)
    await create_random_opportunity_config(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/opportunity-study-area", headers=superuser_token_headers
    )
    assert 200 <= r.status_code < 300
    opportunity_configs = r.json()
    assert len(opportunity_configs) > 1


async def test_get_opportunity_config_by_id(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    opportunity_config = await create_random_opportunity_config(db=db)
    r = await client.get(
        f"{settings.API_V1_STR}/config/opportunity-study-area/{opportunity_config.id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    retrieved_opportunity_config = r.json()
    assert retrieved_opportunity_config.get("id") == opportunity_config.id


async def test_create_opportunity_configs(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    opportunity_config = request_examples.oportunity_study_area_config
    r = await client.post(
        f"{settings.API_V1_STR}/config/opportunity-study-area",
        headers=superuser_token_headers,
        json=opportunity_config,
    )
    assert 200 <= r.status_code < 300
    retrieved_opportunity_config = r.json()
    assert retrieved_opportunity_config.get("name") == opportunity_config.get("name")
    assert retrieved_opportunity_config.get("id")


async def test_update_opportunity_configs(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    opportunity_config = await create_random_opportunity_config(db=db)
    opportunity_config_id = opportunity_config.id
    opportunity_config.category += "_updated"
    r = await client.put(
        f"{settings.API_V1_STR}/config/opportunity-study-area/{opportunity_config_id}",
        headers=superuser_token_headers,
        json=jsonable_encoder(opportunity_config),
    )
    assert 200 <= r.status_code < 300
    retrieved_opportunity_config = r.json()
    assert retrieved_opportunity_config.get("category") == opportunity_config.category
    assert retrieved_opportunity_config.get("id")


async def test_delete_opportunity_config(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    opportunity_config = await create_random_opportunity_config(db=db)
    r = await client.delete(
        f"{settings.API_V1_STR}/config/opportunity-study-area/{opportunity_config.id}",
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300

    # Try to get
    r = await client.get(
        f"{settings.API_V1_STR}/config/opportunity-study-area/{opportunity_config.id}",
        headers=superuser_token_headers,
    )

    assert r.status_code == 404

    # Try to delete again

    r = await client.delete(
        f"{settings.API_V1_STR}/config/opportunity-study-area/{opportunity_config.id}",
        headers=superuser_token_headers,
    )

    assert r.status_code == 404
