"""POST /bundle/{id}/share may only name a grantee inside the caller's organization."""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
from core.core.config import settings
from core.db.models.folder import Folder
from core.db.models.organization import Organization
from core.db.models.team import Team
from core.db.models.user import User
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.test_bundle_legacy_status import _bearer, _insert_bundle

S = settings.SCHEMA


async def _grants(db: AsyncSession, bundle_id: UUID) -> list[Any]:
    return list(
        (
            await db.execute(
                text(
                    f"SELECT grantee_type, grantee_id::text FROM {S}.resource_grant "
                    f"WHERE resource_type = 'bundle' AND resource_id = :r ORDER BY 1,2"
                ),
                {"r": bundle_id},
            )
        ).all()
    )


@pytest.mark.asyncio
async def test_bundle_share_refuses_a_grantee_outside_the_callers_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    authz_sql: None,
    roles: dict[str, UUID],
    make_user: Callable[..., Awaitable[User]],
    make_org: Callable[[], Awaitable[Organization]],
    make_team: Callable[..., Awaitable[Team]],
    make_folder: Callable[..., Awaitable[Folder]],
) -> None:
    """Same class as the folder and template paths: the owner's right to share
    the bundle says nothing about who the grantee is."""
    mine = await make_org()
    theirs = await make_org()
    owner = await make_user(mine.id)
    colleague = await make_user(mine.id)
    my_team = await make_team(colleague, org=mine)
    outsider = await make_user(theirs.id)
    foreign_team = await make_team(outsider, org=theirs)
    folder = await make_folder(owner, "Bundles")
    bundle_id = await _insert_bundle(
        db_session, owner=owner, folder=folder, status="ready", revision=1
    )
    await db_session.commit()

    for grantee_type, grantee_id in (
        ("team", foreign_team.id),
        ("organization", theirs.id),
    ):
        refused = await client.post(
            f"{settings.API_V2_STR}/bundle/{bundle_id}/share",
            json={
                "grantee_type": grantee_type,
                "grantee_id": str(grantee_id),
                "role": "bundle-viewer",
            },
            headers=_bearer(owner.id),
        )
        assert refused.status_code == 403, refused.text
        assert await _grants(db_session, bundle_id) == []

    # A team inside the owner's own organization still goes through.
    ok = await client.post(
        f"{settings.API_V2_STR}/bundle/{bundle_id}/share",
        json={
            "grantee_type": "team",
            "grantee_id": str(my_team.id),
            "role": "bundle-viewer",
        },
        headers=_bearer(owner.id),
    )
    assert ok.status_code == 200, ok.text
    assert await _grants(db_session, bundle_id) == [("team", str(my_team.id))]
