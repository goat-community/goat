"""Whoever may use a template may read the datasets it ships (rule 6c).

The case this comes from: an author keeps a training's datasets in one folder
and the templates built on them in another, and shares only the templates'
folder with the organization. The colleagues could see and use the templates,
but not read their datasets: a shipped dataset was missing from (or empty in)
the projects they made, and a copy was refused as `source_not_readable`. Only a
grant on each template shared its datasets (T6).
"""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
from core.core.config import settings
from core.db.models.folder import Folder
from core.db.models.layer import Layer
from core.db.models.organization import Organization
from core.db.models.user import User
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.test_content_feed import _unverified_bearer
from tests.authz.test_template_api import _create_project
from tests.authz.test_template_copy import (
    _add_layers,
    _choice,
    _project_template,
    processes,  # noqa: F401  (fixture)
)

S = settings.SCHEMA
API = settings.API_V2_STR


async def _role(db: AsyncSession, layer: Layer, user: User) -> str | None:
    return (
        await db.execute(
            text(f"SELECT {S}.effective_role('layer', :l, :u)"),
            {"l": layer.id, "u": user.id},
        )
    ).scalar()


@pytest.mark.asyncio
async def test_a_template_shared_through_a_folder_lets_its_users_read_its_datasets(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Folder]],
    make_layer: Callable[..., Awaitable[Layer]],
    processes: Any,  # noqa: F811
) -> None:
    org = await make_org()
    await db_session.execute(
        text(f'UPDATE {S}."user" SET organization_id = :o WHERE id = :u'),
        {"o": org.id, "u": fixture_create_user},
    )
    author = await db_session.get(User, fixture_create_user)
    assert author is not None
    colleague = await make_user(org.id)
    colleague_home = await make_folder(colleague)

    data = await make_folder(author, "Bonn")
    shipped = await make_layer(author, data)
    copied = await make_layer(author, data)
    copied_empty = await make_layer(author, data)
    # A dataset only shared with the author to view: theirs to use, not to
    # pass on.
    lender = await make_user(org.id)
    lent = await make_layer(lender, await make_folder(lender))
    await db_session.execute(
        text(
            f"INSERT INTO {S}.resource_grant "
            "(resource_type, resource_id, grantee_type, grantee_id, role_id, granted_by) "
            "VALUES ('layer', :l, 'user', :u, :r, :b)"
        ),
        {"l": lent.id, "u": author.id, "r": roles["layer-viewer"], "b": lender.id},
    )
    # A dataset shared with the whole organization to view, like the viewer
    # grants a template grant writes (T6): readable by the author, still not
    # theirs to pass on.
    org_wide = await make_layer(lender, await make_folder(lender))
    await db_session.execute(
        text(
            f"INSERT INTO {S}.resource_grant "
            "(resource_type, resource_id, grantee_type, grantee_id, role_id, granted_by) "
            "VALUES ('layer', :l, 'organization', :o, :r, :b)"
        ),
        {"l": org_wide.id, "o": org.id, "r": roles["layer-viewer"], "b": lender.id},
    )
    training = await make_folder(author, "Schulung")
    await db_session.commit()
    for layer, may_share in ((lent, False), (org_wide, False), (shipped, True)):
        rank = (
            await db_session.execute(
                text(f"SELECT {S}.effective_rank('layer', :l, :u, FALSE)"),
                {"l": layer.id, "u": author.id},
            )
        ).scalar()
        assert (rank >= 2) is may_share, (layer.id, rank)

    home = str(data.id)
    project_id = await _create_project(client, home)
    await _add_layers(
        client, project_id, shipped.id, copied.id, copied_empty.id, lent.id
    )
    saved = await _project_template(
        client,
        str(training.id),
        project_id,
        [
            _choice(shipped, "ship"),
            _choice(copied, "copy"),
            _choice(copied_empty, "copy", copy_content=False),
            _choice(lent, "ship"),
        ],
    )
    assert saved.status_code == 201, saved.text
    tid = saved.json()["id"]

    for layer in (shipped, copied, copied_empty, lent):
        assert await _role(db_session, layer, colleague) is None

    shared = await client.post(
        f"{API}/folder/{training.id}/share",
        json={
            "grantee_type": "organization",
            "grantee_id": str(org.id),
            "role": "folder-viewer",
        },
    )
    assert shared.status_code == 200, shared.text

    # Through the folder alone the colleague may now read what the template
    # links or copies with its rows; not the columns-only copy, and not what
    # the author may only view.
    assert await _role(db_session, shipped, colleague) == "viewer"
    assert await _role(db_session, copied, colleague) == "viewer"
    assert await _role(db_session, copied_empty, colleague) is None
    assert await _role(db_session, lent, colleague) is None
    # Read only: the template hands out no write.
    assert (
        await db_session.execute(
            text(f"SELECT {S}.layer_write_allowed(:l, :u)"),
            {"l": shipped.id, "u": colleague.id},
        )
    ).scalar() is False

    use = await client.post(
        f"{API}/template/{tid}/use",
        json={"target_folder_id": str(colleague_home.id)},
        headers={"Authorization": f"Bearer {_unverified_bearer(colleague.id)}"},
    )
    assert use.status_code == 200, use.text
    jobs = {job["source_layer_id"]: job for job in use.json()["copy_jobs"]}
    assert jobs[str(copied.id)]["error"] is None
    assert jobs[str(copied.id)]["job_id"] is not None

    # Read live: the dataset leaving the template ends it ...
    await db_session.execute(
        text(
            f"UPDATE {S}.template SET inputs = (SELECT jsonb_agg(i) "
            "FROM jsonb_array_elements(inputs) i WHERE i->>'layer_id' <> :l) WHERE id = :t"
        ),
        {"l": str(shipped.id), "t": tid},
    )
    await db_session.commit()
    assert await _role(db_session, shipped, colleague) is None
    # ... and so does the template no longer reaching the colleague.
    await db_session.execute(
        text(
            f"DELETE FROM {S}.resource_grant "
            "WHERE resource_type = 'folder' AND resource_id = :f"
        ),
        {"f": training.id},
    )
    await db_session.commit()
    assert await _role(db_session, copied, colleague) is None
