from typing import Dict

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.core.config import settings
from src.crud.crud_customization import dynamic_customization
from src.schemas.customization import request_examples
from src.tests.utils.user import create_random_user

pytestmark = pytest.mark.asyncio


# get user customization
async def test_get_customizations(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/customizations/me", headers=superuser_token_headers
    )
    all_customizations = r.json()
    assert len(all_customizations) > 0
    assert len(all_customizations["poi_groups"]) > 0


async def test_insert_poi_customizations(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = request_examples["user_customization_insert"]["poi"]["value"]
    r = await client.post(
        f"{settings.API_V1_STR}/customizations/user/insert/poi",
        headers=superuser_token_headers,
        json=data,
    )
    all_customizations = r.json()
    assert 200 <= r.status_code < 300
    assert len(all_customizations) > 0
    assert len(all_customizations["poi_groups"]) > 0


async def test_reset_poi_style_customizations(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    superuser = await crud.user.get_by_key(db, key="email", value=settings.FIRST_SUPERUSER_EMAIL)
    obj_dict = jsonable_encoder(request_examples["user_customization_insert"]["poi"]["value"])
    await dynamic_customization.handle_user_setting_modification(
        db=db,
        current_user=superuser[0],
        setting_type="poi",
        changeset=obj_dict,
        modification_type="insert",
    )
    await dynamic_customization.build_main_setting_json(db=db, current_user=superuser[0])
    category = request_examples["user_customization_delete"]["poi"]["value"]
    r = await client.delete(
        f"{settings.API_V1_STR}/customizations/user/reset-style/poi/{category}",
        headers=superuser_token_headers,
    )
    all_customizations = r.json()
    assert 200 <= r.status_code < 300
    assert isinstance(all_customizations["poi_groups"], list)


async def test_superuser_get_normal_user_setting(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    user_in = await create_random_user(db=db)
    obj_dict = jsonable_encoder(request_examples["user_customization_insert"]["poi"]["value"])
    await dynamic_customization.handle_user_setting_modification(
        db=db,
        current_user=user_in,
        setting_type="poi",
        changeset=obj_dict,
        modification_type="insert",
    )
    await dynamic_customization.build_main_setting_json(db=db, current_user=user_in)
    r = await client.get(
        f"{settings.API_V1_STR}/customizations/{user_in.id}/{user_in.active_study_area_id}",
        headers=superuser_token_headers,
    )
    all_customizations = r.json()
    assert 200 <= r.status_code < 300
    assert isinstance(all_customizations["poi_groups"], list)


# TODO: test_superuser_update_normal_user_setting
# TODO: test_superuser_delete_normal_user_setting
# TODO: test_normal_user_get_normal_user_setting
