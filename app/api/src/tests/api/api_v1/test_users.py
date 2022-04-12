from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.core.config import settings
from src.schemas.user import request_examples
from src.tests.utils.organization import create_random_organization
from src.tests.utils.user import create_random_user, get_user_token_headers
from src.tests.utils.utils import random_email, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_retrieve_users(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    user_in = await create_random_user(db=db)
    user_in2 = await create_random_user(db=db)
    r = await client.get(f"{settings.API_V1_STR}/users", headers=superuser_token_headers)
    all_users = r.json()
    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item


async def test_create_user_by_normal_user(client: AsyncClient, db: AsyncSession) -> None:
    normal_user_headers = await get_user_token_headers(client=client, db=db)
    data = request_examples["create"]
    data["email"] = random_email()
    data["password"] = random_lower_string()
    organization = await create_random_organization(db=db)
    data["organization_id"] = organization.id
    r = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_headers,
        json=data,
    )
    assert r.status_code == 400


async def test_get_users_superuser_me(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = await client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["email"] == settings.FIRST_SUPERUSER_EMAIL


async def test_get_users_normal_user_me(client: AsyncClient, db: AsyncSession) -> None:
    normal_user_headers = await get_user_token_headers(client=client, db=db)
    r = await client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True


async def test_get_user_superuser(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    user_in = await create_random_user(db=db)
    user_id = user_in.id
    r = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.user.get_by_key(db, key="email", value=user_in.email)
    assert len(existing_user) == 1
    assert existing_user[0].email == api_user["email"]


async def test_delete_user_superuser(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    user_in = await create_random_user(db=db)
    user_id = user_in.id
    r = await client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    existing_user = await crud.user.get_by_key(db, key="email", value=user_in.email)
    assert len(existing_user) == 0


async def test_update_user_superuser(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    user_in = await create_random_user(db=db)
    user_id = user_in.id
    data = request_examples["update"]
    data["email"] = user_in.email
    data["organization_id"] = user_in.organization_id
    r = await client.put(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    existing_user = await crud.user.get_by_key(db, key="email", value=data["email"])
    assert len(existing_user) == 1
    assert existing_user[0].email == data["email"]


async def test_create_user_existing_username(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = await create_random_user(db=db, email=email, password=password)

    data = request_examples["create"]
    data["email"] = email
    data["password"] = password
    organization = await create_random_organization(db=db)
    data["organization_id"] = organization.id
    r = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "id" not in created_user


async def test_read_user_study_area_list(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me/study-areas-list",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    study_areas = r.json()
    assert len(study_areas) > 0


async def test_read_user_active_study_area(
    client: AsyncClient, superuser_token_headers: dict, db: AsyncSession
) -> None:
    superuser = await crud.user.get_by_key(db, key="email", value=settings.FIRST_SUPERUSER_EMAIL)
    assert len(superuser) == 1
    r = await client.get(
        f"{settings.API_V1_STR}/users/me/study-area",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    study_area = r.json()
    assert len(study_area["features"]) == 1
    assert study_area["features"][0]["id"] == superuser[0].active_study_area_id


async def test_update_user_preference(client: AsyncClient, db: AsyncSession) -> None:
    normal_user_headers = await get_user_token_headers(client=client, db=db)
    data = request_examples["update_user_preference"]["language_study_area_preference"]["value"]
    data["active_study_area_id"] = request_examples["create"]["active_study_area_id"]
    r = await client.put(
        f"{settings.API_V1_STR}/users/me/preference",
        headers=normal_user_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    r = r.json()
    assert r["language_preference"] == data["language_preference"]
    assert r["active_study_area_id"] == data["active_study_area_id"]


async def test_update_normal_user_preference_not_allowed_fields(
    client: AsyncClient, db: AsyncSession
) -> None:
    normal_user_headers = await get_user_token_headers(client=client, db=db)
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "limit_scenarios": 100,
        "storage": 500,
    }
    r = await client.put(
        f"{settings.API_V1_STR}/users/me/preference",
        headers=normal_user_headers,
        json=data,
    )
    assert r.status_code >= 400
