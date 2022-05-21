from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.core.config import settings
from src.schemas.organization import OrganizationCreate, OrganizationUpdate
from src.tests.utils.user import get_user_token_headers
from src.tests.utils.utils import random_lower_string

pytestmark = pytest.mark.asyncio


async def test_get_organizations(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = await client.get(f"{settings.API_V1_STR}/organizations", headers=superuser_token_headers)
    all_organizations = r.json()
    assert len(all_organizations) > 0
    for organization in all_organizations:
        assert "id" in organization
        assert "name" in organization


async def test_create_organization(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    organization_name = random_lower_string()
    organization_in = OrganizationCreate(name=organization_name)
    r = await client.post(
        f"{settings.API_V1_STR}/organizations",
        headers=superuser_token_headers,
        json=organization_in.dict(),
    )
    assert 200 <= r.status_code < 300
    created_organization = r.json()
    organization = await crud.organization.get(db=db, id=created_organization["id"])
    assert organization
    assert organization.name == created_organization["name"]


async def test_create_organization_existing_name(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    organization_name = random_lower_string()
    organization_in = OrganizationCreate(name=organization_name)
    await crud.organization.create(db, obj_in=organization_in)
    r = await client.post(
        f"{settings.API_V1_STR}/organizations",
        headers=superuser_token_headers,
        json=organization_in.dict(),
    )
    created_organization = r.json()
    assert r.status_code == 400
    assert "id" not in created_organization


async def test_create_organization_by_normal_user(client: AsyncClient, db: AsyncSession) -> None:
    normal_user_headers = await get_user_token_headers(client=client, db=db)
    organization_name = random_lower_string()
    organization_in = OrganizationCreate(name=organization_name)
    r = await client.post(
        f"{settings.API_V1_STR}/organizations",
        headers=normal_user_headers,
        json=organization_in.dict(),
    )
    assert r.status_code == 400


# test_update_organization
async def test_update_organization(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    organization_name = random_lower_string()
    organization_in = OrganizationCreate(name=organization_name)
    organization = await crud.organization.create(db, obj_in=organization_in)
    organization_update = OrganizationUpdate(name=organization_name)
    r = await client.put(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=superuser_token_headers,
        json=organization_update.dict(),
    )
    assert 200 <= r.status_code < 300
    updated_organization = r.json()
    assert updated_organization["name"] == organization_name
    assert updated_organization["id"] == organization.id


# test_delete_organization
async def test_delete_organization(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db: AsyncSession
) -> None:
    organization_name = random_lower_string()
    organization_in = OrganizationCreate(name=organization_name)
    organization = await crud.organization.create(db, obj_in=organization_in)
    r = await client.delete(
        f"{settings.API_V1_STR}/organizations/{organization.id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    deleted_organization = r.json()
    assert deleted_organization["id"] == organization.id
