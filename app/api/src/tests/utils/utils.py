import random
import string
from typing import Dict

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.core.config import settings
from src.db import models


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.de"


async def get_superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


async def create_sample_scenario(client, superuser_token_headers) -> models.Scenario:
    r = await client.post(
        f"{settings.API_V1_STR}/scenarios",
        headers=superuser_token_headers,
        json=schemas.scenario.request_examples["create"],
    )
    scenario = r.json()
    return scenario
