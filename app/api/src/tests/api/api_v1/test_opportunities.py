from typing import Dict

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.core.config import settings
from src.schemas.geostore import request_examples

pytestmark = pytest.mark.asyncio


async def test_read_oportunities_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/config/opportunities", headers=superuser_token_headers
    )
    assert 200 <= r.status_code < 300
    oportunities = r.json()
    assert len(oportunities) > 1


async def test_read_oportunity_groups_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/config/opportunities/groups", headers=superuser_token_headers
    )
    assert 200 <= r.status_code < 300
    groups = r.json()
    assert len(groups) > 1
