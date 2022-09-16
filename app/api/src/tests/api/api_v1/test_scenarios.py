# TODO: Test scenario endpoints
# TODO: Don't allow to create scenario features outside of study area
from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.tests.utils.utils import create_sample_scenario

pytestmark = pytest.mark.asyncio


async def test_delete_scenarios(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    scenarios = [await create_sample_scenario(client, superuser_token_headers) for i in range(2)]
    scenario_ids = [scenario["id"] for scenario in scenarios]
    r = await client.delete(
        f"{settings.API_V1_STR}/scenarios/",
        headers=superuser_token_headers,
        params={"id": scenario_ids},
    )

    assert 200 <= r.status_code < 300

    # Try to get
    r = await client.get(
        f"{settings.API_V1_STR}/scenarios",
        headers=superuser_token_headers,
    )
    r_scenarios = r.json()
    r_scenario_ids = [scenario["id"] for scenario in r_scenarios]
    for id in scenario_ids:
        assert not id in r_scenario_ids
