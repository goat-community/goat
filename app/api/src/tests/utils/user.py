from typing import Dict, List, Optional

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.core.config import settings
from src.db import models
from src.schemas.user import UserCreate, UserUpdate, request_examples
from src.tests.utils.organization import create_random_organization
from src.tests.utils.utils import random_email, random_lower_string


async def user_authentication_headers(
    *, client: AsyncClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


async def create_random_user(
    db: AsyncSession,
    email: Optional[str] = random_email(),
    password: Optional[str] = random_lower_string(),
    roles: Optional[List[str]] = ["user"],
) -> models.User:
    user_in = UserCreate(**request_examples["create"])
    user_in.email = email
    user_in.password = password
    user_in.roles = roles
    organization = await create_random_organization(db=db)
    user_in.organization_id = organization.id
    user = await crud.user.create(db=db, obj_in=user_in)
    return user


async def get_user_token_headers(
    client: AsyncClient,
    db: AsyncSession,
    email: Optional[str] = None,
    password: Optional[str] = None,
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email oand password or create a new user
    """

    if email is not None and password is not None:
        headers = await user_authentication_headers(client=client, email=email, password=password)
        return headers

    email = random_email()
    password = random_lower_string()
    user = await create_random_user(db=db, email=email, password=password)
    return await user_authentication_headers(client=client, email=email, password=password)
