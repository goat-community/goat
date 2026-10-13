"""GET /template lists a shared template under the source it was shared through.

A template shared with the caller's organization belongs under Organization, one
shared with a team of theirs under Team, and one shared with them alone under
Shared with me, whether the grant sits on the template or on a folder above it.
Before, those filters only looked at the templates stored in the caller's own
spaces, so a colleague who shared a template with the organization was found
under Everyone alone.
"""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID, uuid4

import pytest
from core.core.config import settings
from core.db.models._link_model import ResourceGrant
from core.db.models.folder import Folder
from core.db.models.organization import Organization
from core.db.models.space import Space, SpaceKind
from core.db.models.team import Team
from core.db.models.template import Template, TemplatePayloadKind
from core.db.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.test_bundle_legacy_status import _bearer

API = settings.API_V2_STR

# The folders this test's templates live in.
_FOLDERS: set[str] = set()


async def _template(
    db: AsyncSession, owner: User, folder: Folder, name: str
) -> Template:
    template = Template(
        id=uuid4(),
        name=name,
        space_id=folder.space_id,
        folder_id=folder.id,
        user_id=owner.id,
        payload_kind=TemplatePayloadKind.workflow,
    )
    db.add(template)
    await db.flush()
    return template


def _grant(
    resource_type: str,
    resource_id: UUID | None,
    grantee_type: str,
    grantee_id: UUID | None,
    role_id: UUID,
    granted_by: UUID | None,
) -> ResourceGrant:
    return ResourceGrant(
        resource_type=resource_type,
        resource_id=resource_id,
        grantee_type=grantee_type,
        grantee_id=grantee_id,
        role_id=role_id,
        granted_by=granted_by,
    )


async def _listed(client: AsyncClient, caller: User, source: str) -> dict[str, Any]:
    """The templates this test made that `source` lists for `caller`, by name;
    published templates other tests leave behind are on Everyone too."""
    response = await client.get(
        f"{API}/template",
        params={"source": source, "size": 100},
        headers=_bearer(caller.id),
    )
    assert response.status_code == 200, response.text
    return {
        item["name"]: item
        for item in response.json()["items"]
        if item["folder_id"] in _FOLDERS
    }


@pytest.mark.asyncio
async def test_a_shared_template_is_listed_under_the_source_it_was_shared_through(
    client: AsyncClient,
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_team: Callable[..., Awaitable[Team]],
    make_space: Callable[..., Awaitable[Space]],
    make_folder: Callable[..., Awaitable[Folder]],
) -> None:
    org = await make_org()
    author = await make_user(org.id)
    colleague = await make_user(org.id)
    team = await make_team(colleague, author, org=org)
    team_space = await make_space(SpaceKind.team, team=team)
    org_space = (
        await db_session.execute(
            select(Space).where(
                Space.kind == SpaceKind.organization, Space.organization_id == org.id
            )
        )
    ).scalar_one()

    loose = await make_folder(author, "Loose")
    shared_folder = await make_folder(author, "Schulung")
    _FOLDERS.update({str(loose.id), str(shared_folder.id)})
    with_org = await _template(
        db_session, author, loose, "Shared with the organization"
    )
    in_folder = await _template(
        db_session, author, shared_folder, "In a folder shared with the organization"
    )
    with_team = await _template(db_session, author, loose, "Shared with the team")
    with_me = await _template(db_session, author, loose, "Shared with the colleague")
    with_both = await _template(
        db_session, author, loose, "Shared with the team and the organization"
    )
    await _template(db_session, author, loose, "Not shared")
    viewer, folder_viewer = roles["template-viewer"], roles["folder-viewer"]
    db_session.add_all(
        [
            _grant("template", with_org.id, "organization", org.id, viewer, author.id),
            _grant(
                "folder",
                shared_folder.id,
                "organization",
                org.id,
                folder_viewer,
                author.id,
            ),
            _grant("template", with_team.id, "team", team.id, viewer, author.id),
            _grant("template", with_me.id, "user", colleague.id, viewer, author.id),
            _grant("template", with_both.id, "team", team.id, viewer, author.id),
            _grant("template", with_both.id, "organization", org.id, viewer, author.id),
        ]
    )
    await db_session.commit()

    org_list = await _listed(client, colleague, "org")
    assert set(org_list) == {
        "Shared with the organization",
        "In a folder shared with the organization",
        "Shared with the team and the organization",
    }
    assert set(await _listed(client, colleague, "team")) == {
        "Shared with the team",
        "Shared with the team and the organization",
    }
    assert set(await _listed(client, colleague, "shared")) == {
        "Shared with the colleague"
    }
    assert set(await _listed(client, colleague, "mine")) == set()

    everyone = await _listed(client, colleague, "all")
    assert set(everyone) == {
        "Shared with the organization",
        "In a folder shared with the organization",
        "Shared with the team",
        "Shared with the colleague",
        "Shared with the team and the organization",
    }
    # The browser shelves a row by the caller's space it was shared into.
    assert everyone["Shared with the organization"]["shared_into_space_id"] == str(
        org_space.id
    )
    assert everyone["In a folder shared with the organization"][
        "shared_into_space_id"
    ] == str(org_space.id)
    assert everyone["Shared with the team"]["shared_into_space_id"] == str(
        team_space.id
    )
    assert everyone["Shared with the colleague"]["shared_into_space_id"] is None
    # Shared with both, it sits on the narrower shelf: the team's.
    assert everyone["Shared with the team and the organization"][
        "shared_into_space_id"
    ] == str(team_space.id)

    single = await client.get(
        f"{API}/template/{in_folder.id}", headers=_bearer(colleague.id)
    )
    assert single.status_code == 200, single.text
    assert single.json()["shared_into_space_id"] == str(org_space.id)

    # The author finds them under Mine, with no shelf of someone else's.
    mine = await _listed(client, author, "mine")
    assert len(mine) == 6
    assert all(item["shared_into_space_id"] is None for item in mine.values())
