from uuid import UUID

import pytest
from core.core.config import settings
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get(
        "/api/healthz",
    )

    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}


@pytest.mark.asyncio
async def test_a_first_settings_save_starts_from_the_defaults(
    client: AsyncClient, db_session: AsyncSession, fixture_create_user: UUID
) -> None:
    """A user with no settings row yet can save settings: the defaults fill
    what the request leaves out (it used to fail with 422 on spotlight_seen)."""
    await db_session.execute(
        text(f"DELETE FROM {settings.SCHEMA}.system_setting WHERE user_id = :u"),
        {"u": fixture_create_user},
    )
    await db_session.commit()

    saved = await client.put(
        f"{settings.API_V2_STR}/system/settings",
        json={"preferred_language": "en", "client_theme": "light", "unit": "metric"},
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["spotlight_seen"] == []

    read = await client.get(f"{settings.API_V2_STR}/system/settings")
    assert read.json()["preferred_language"] == "en"
    assert read.json()["client_theme"] == "light"
