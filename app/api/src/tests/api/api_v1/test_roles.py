from typing import Dict

import pytest
from httpx import AsyncClient

from src.core.config import settings

pytestmark = pytest.mark.asyncio


async def test_get_roles_list(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = await client.get(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers)
    roles = r.json()
    assert roles
    assert len(roles) == 2
