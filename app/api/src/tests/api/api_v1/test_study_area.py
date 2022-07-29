import json
from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.core.config import settings
from src.schemas.study_area import GROUP_ORDER, StudyAreaSettings, groups_example_data
from src.tests.utils.study_area import duplicate_first_study_area
from src.tests.utils.utils import random_lower_string

pytestmark = pytest.mark.asyncio


async def test_read_study_area_setting(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    """
    Assume having study_area at the beginning.
    """
    first_study_area = await crud.study_area.get_first(db=db)
    for group in GROUP_ORDER:
        r = await client.get(
            f"{settings.API_V1_STR}/config/study-area/settings/{first_study_area.id}/{group}",
            headers=superuser_token_headers,
        )
        assert 200 <= r.status_code < 300


async def test_update_study_area_setting(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    """
    Assume having study_area at the beginning.
    """
    study_area = await duplicate_first_study_area(db=db)
    layer_groups = {}
    for group in GROUP_ORDER:
        r = await client.get(
            f"{settings.API_V1_STR}/config/study-area/settings/{study_area.id}/{group}",
            headers=superuser_token_headers,
        )
        assert 200 <= r.status_code < 300
        layer_groups[group] = r.json()

    for group in GROUP_ORDER:
        r = await client.put(
            f"{settings.API_V1_STR}/config/study-area/settings/{study_area.id}/{group}",
            headers=superuser_token_headers,
            json=layer_groups[group],
        )
        assert 200 <= r.status_code < 300

    for group in GROUP_ORDER:
        layer_groups[group].append(random_lower_string())
        r = await client.put(
            f"config/study-area/settings/{study_area.id}/{group}",
            headers=superuser_token_headers,
            json=layer_groups[group],
        )
        assert 400 <= r.status_code < 500


def test_parse_study_area_settings():

    groups_data = json.loads(groups_example_data)
    settings = StudyAreaSettings(**groups_data)
    assert len(settings.layer_groups) > 0
