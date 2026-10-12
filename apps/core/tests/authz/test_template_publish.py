"""Task 6: publish/unpublish (T4, superuser only) and template grants
(T3/T6)."""

from typing import Any, Awaitable, Callable
from uuid import UUID, uuid4

import pytest
from core.core.config import settings
from core.db.models.folder import Folder
from core.db.models.layer import Layer
from core.db.models.organization import Organization
from core.db.models.space import Space, SpaceKind
from core.db.models.team import Team
from core.db.models.user import User
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.test_content_feed import _unverified_bearer

S = settings.SCHEMA
VIEW = {
    "latitude": 48.1,
    "longitude": 11.5,
    "zoom": 10,
    "min_zoom": 0,
    "max_zoom": 20,
    "bearing": 0,
    "pitch": 0,
}


async def _create_project(
    client: AsyncClient, folder_id: str, name: str = "src"
) -> str:
    r = await client.post(
        f"{settings.API_V2_STR}/project",
        json={
            "name": f"{name}-{uuid4().hex[:6]}",
            "folder_id": folder_id,
            "initial_view_state": VIEW,
        },
    )
    assert r.status_code in (200, 201), r.text
    return str(r.json()["id"])


def _layout_config() -> dict[str, Any]:
    return {
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margins": {"top": 10, "right": 10, "bottom": 10, "left": 10},
        },
        "layout": {"type": "grid", "columns": 12, "rows": 12, "gap": 5},
        "elements": [],
        "theme": None,
        "atlas": None,
    }


async def _create_layout(
    client: AsyncClient, project_id: str, config: dict[str, Any]
) -> str:
    r = await client.post(
        f"{settings.API_V2_STR}/project/{project_id}/report-layout",
        json={"name": "layout", "config": config},
    )
    assert r.status_code == 201, r.text
    return str(r.json()["id"])


async def _project_template_with_layer(
    client: AsyncClient,
    db_session: AsyncSession,
    *,
    home: str,
    layer_id: UUID,
    name: str = "Dashboard template",
) -> str:
    """A project-payload template shipping one layer as its only input,
    via `_project_inputs`' auto-detection (T5) -- no workflow config needed."""
    project_id = await _create_project(client, home, name=name)
    add_resp = await client.post(
        f"{settings.API_V2_STR}/project/{project_id}/layer",
        params=[("layer_ids", str(layer_id))],
    )
    assert add_resp.status_code == 200, add_resp.text

    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": name,
            "folder_id": home,
            "source": {"kind": "project", "project_id": project_id},
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    return str(create_resp.json()["id"])


@pytest.mark.asyncio
async def test_publish_succeeds_when_every_ship_input_is_catalog_origin(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_layer: Callable[..., Awaitable[Any]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    home = str(fixture_get_home_folder["id"])
    owner = await db_session.get(User, fixture_create_user)
    assert owner is not None
    home_folder = await db_session.get(Folder, UUID(home))
    assert home_folder is not None
    layer = await make_layer(owner, home_folder)
    await db_session.execute(
        text(
            f"UPDATE {S}.layer SET catalog_external_uid = 'x', catalog_version = '1' "
            "WHERE id = :id"
        ),
        {"id": layer.id},
    )
    await db_session.commit()

    tid = await _project_template_with_layer(
        client, db_session, home=home, layer_id=layer.id
    )

    publish_resp = await client.post(f"{settings.API_V2_STR}/template/{tid}/publish")
    assert publish_resp.status_code == 200, publish_resp.text
    assert publish_resp.json()["catalog_status"] == "published"

    stranger = await make_user()
    await db_session.commit()
    stranger_headers = {"Authorization": f"Bearer {_unverified_bearer(stranger.id)}"}

    read_resp = await client.get(
        f"{settings.API_V2_STR}/template/{tid}", headers=stranger_headers
    )
    assert read_resp.status_code == 200, read_resp.text
    assert read_resp.json()["my_role"] == "viewer"

    listing = await client.get(
        f"{settings.API_V2_STR}/template",
        params={"source": "goat"},
        headers=stranger_headers,
    )
    assert listing.status_code == 200, listing.text
    assert tid in {i["id"] for i in listing.json()["items"]}


async def _team_space_layer(
    db_session: AsyncSession,
    *,
    owner: User,
    make_user: Callable[..., Awaitable[User]],
    make_team: Callable[..., Awaitable[Team]],
    make_space: Callable[..., Awaitable[Space]],
) -> Layer:
    """A layer the caller may read and edit but does not own: it lives in a
    team space where the caller is a plain member (editor by the space
    default), and making a dataset public is the owner's call."""
    colleague = await make_user()
    team = await make_team(owner, colleague)
    space = await make_space(SpaceKind.team, team=team)
    folder = Folder(
        id=uuid4(), user_id=owner.id, space_id=space.id, name=f"team-{uuid4().hex[:6]}"
    )
    db_session.add(folder)
    await db_session.flush()
    layer = Layer(
        id=uuid4(),
        user_id=owner.id,
        folder_id=folder.id,
        space_id=space.id,
        name=f"team-layer-{uuid4().hex[:6]}",
        type="feature",
        feature_layer_type="standard",
        feature_layer_geometry_type="polygon",
    )
    db_session.add(layer)
    await db_session.flush()
    return layer


async def _layer_public_read(db_session: AsyncSession, layer_id: UUID) -> bool:
    return bool(
        (
            await db_session.execute(
                text(f"SELECT public_read FROM {S}.layer WHERE id = :id"),
                {"id": layer_id},
            )
        ).scalar_one()
    )


@pytest.mark.asyncio
async def test_publish_409s_naming_a_shipped_layer_the_caller_does_not_own(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_user: Callable[..., Awaitable[User]],
    make_team: Callable[..., Awaitable[Team]],
    make_space: Callable[..., Awaitable[Space]],
) -> None:
    """A shipped dataset that is neither a catalog dataset nor public, and
    that the publisher does not own, is refused — and publishing must not
    have touched its flag: someone else's data never becomes public as a
    side effect of curating the shelf."""
    home = str(fixture_get_home_folder["id"])
    owner = await db_session.get(User, fixture_create_user)
    assert owner is not None
    layer = await _team_space_layer(
        db_session,
        owner=owner,
        make_user=make_user,
        make_team=make_team,
        make_space=make_space,
    )
    await db_session.commit()

    tid = await _project_template_with_layer(
        client, db_session, home=home, layer_id=layer.id, name="Team data"
    )

    publish_resp = await client.post(f"{settings.API_V2_STR}/template/{tid}/publish")
    assert publish_resp.status_code == 409, publish_resp.text
    detail = publish_resp.json()["detail"]
    assert detail["code"] == "template_dataset_not_public"
    assert detail["layers"] == [{"id": str(layer.id), "name": layer.name}]
    assert await _layer_public_read(db_session, layer.id) is False

    read_resp = await client.get(f"{settings.API_V2_STR}/template/{tid}")
    assert read_resp.status_code == 200, read_resp.text
    (shipped,) = read_resp.json()["inputs"]
    assert shipped["from_catalog"] is False
    assert shipped["public_read"] is False


@pytest.mark.asyncio
async def test_publish_makes_the_publishers_own_datasets_public(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_layer: Callable[..., Awaitable[Any]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """A shipped dataset the publisher owns becomes a public dataset:
    publishing sets `public_read`, so every signed-in user reads it as
    viewer (anonymous still gets nothing), the owner keeps owning it, it is
    reported as public on the template's inputs, and the template counts as
    shipping data. It never enters the STAC catalog: `catalog_external_uid`
    stays NULL."""
    home = str(fixture_get_home_folder["id"])
    owner = await db_session.get(User, fixture_create_user)
    assert owner is not None
    home_folder = await db_session.get(Folder, UUID(home))
    assert home_folder is not None
    layer = await make_layer(owner, home_folder)
    await db_session.commit()

    tid = await _project_template_with_layer(
        client, db_session, home=home, layer_id=layer.id, name="Sample data"
    )
    before = await client.get(f"{settings.API_V2_STR}/template/{tid}")
    (shipped,) = before.json()["inputs"]
    assert shipped["public_read"] is False
    assert before.json()["ships_data"] is False

    publish_resp = await client.post(f"{settings.API_V2_STR}/template/{tid}/publish")
    assert publish_resp.status_code == 200, publish_resp.text
    body = publish_resp.json()
    assert body["catalog_status"] == "published"
    assert body["ships_data"] is True
    (shipped,) = body["inputs"]
    assert shipped["from_catalog"] is False
    assert shipped["public_read"] is True

    assert await _layer_public_read(db_session, layer.id) is True
    uid = (
        await db_session.execute(
            text(f"SELECT catalog_external_uid FROM {S}.layer WHERE id = :id"),
            {"id": layer.id},
        )
    ).scalar_one()
    assert uid is None

    stranger = await make_user()
    await db_session.commit()

    async def role_of(who: UUID | None) -> str | None:
        return (
            await db_session.execute(
                text(f"SELECT {S}.effective_role('layer', :l, :u)"),
                {"l": layer.id, "u": who},
            )
        ).scalar_one_or_none()

    assert await role_of(stranger.id) == "viewer"
    assert await role_of(None) is None
    assert await role_of(owner.id) == "owner"


@pytest.mark.asyncio
async def test_publish_401s_for_a_non_superuser_token(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    layout_id = await _create_layout(client, project_id, _layout_config())
    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": "No datasets",
            "folder_id": home,
            "source": {
                "kind": "layout",
                "project_id": project_id,
                "layout_id": layout_id,
            },
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    stranger = await make_user()
    await db_session.commit()

    # `_unverified_bearer` carries only `sub` -- no `realm_access` -- so
    # `is_superuser` finds no roles at all and rejects with 401, regardless
    # of who the caller is or whether they own the template.
    resp = await client.post(
        f"{settings.API_V2_STR}/template/{tid}/publish",
        headers={"Authorization": f"Bearer {_unverified_bearer(stranger.id)}"},
    )
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_publish_401s_even_with_throw_error_false_query_param(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """B1: the old `is_superuser` dependency's `throw_error` bool has no
    `Depends`/`Body` marker, so FastAPI exposed it as an overridable query
    parameter — `?throw_error=false` let a non-superuser call through. The
    route now gates on `require_superuser`, which takes no parameters a
    caller can override."""
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    layout_id = await _create_layout(client, project_id, _layout_config())
    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": "Gate bypass attempt",
            "folder_id": home,
            "source": {
                "kind": "layout",
                "project_id": project_id,
                "layout_id": layout_id,
            },
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    stranger = await make_user()
    await db_session.commit()

    resp = await client.post(
        f"{settings.API_V2_STR}/template/{tid}/publish",
        params={"throw_error": "false"},
        headers={"Authorization": f"Bearer {_unverified_bearer(stranger.id)}"},
    )
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_unpublish_by_a_superuser_with_only_shelf_viewer_access_succeeds(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """E1: `unpublish` used to `assert` the caller's post-flip role, but a
    superuser whose only relationship to a published template was the
    shelf's blanket viewer role loses even that the instant `catalog_status`
    flips back to `none` — that used to be an unhandled 500 after the write
    already committed. It must succeed and return some role, not crash."""
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    layout_id = await _create_layout(client, project_id, _layout_config())
    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": "Shelf-only access",
            "folder_id": home,
            "source": {
                "kind": "layout",
                "project_id": project_id,
                "layout_id": layout_id,
            },
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    publish_resp = await client.post(f"{settings.API_V2_STR}/template/{tid}/publish")
    assert publish_resp.status_code == 200, publish_resp.text

    # A stranger superuser: `realm_access.roles` carries "superuser" but the
    # caller has no other relationship to this template — their only access
    # is the shelf's blanket viewer role.
    stranger = await make_user()
    await db_session.commit()
    stranger_token = _unverified_bearer(stranger.id, roles=["superuser"])

    resp = await client.post(
        f"{settings.API_V2_STR}/template/{tid}/unpublish",
        headers={"Authorization": f"Bearer {stranger_token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["catalog_status"] == "none"
    assert resp.json()["my_role"] in ("viewer", "owner", "editor")


@pytest.mark.asyncio
async def test_stranger_gets_403_listing_grants_on_a_published_template(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """E2: once a template is published every authenticated user is a
    shelf viewer — `GET /template/{id}/grant` must not treat that as enough
    to list every grantee (individual users included); it now requires
    write (editor+), matching bundle grants."""
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    layout_id = await _create_layout(client, project_id, _layout_config())
    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": "Published, grants private",
            "folder_id": home,
            "source": {
                "kind": "layout",
                "project_id": project_id,
                "layout_id": layout_id,
            },
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    publish_resp = await client.post(f"{settings.API_V2_STR}/template/{tid}/publish")
    assert publish_resp.status_code == 200, publish_resp.text

    stranger = await make_user()
    await db_session.commit()

    resp = await client.get(
        f"{settings.API_V2_STR}/template/{tid}/grant",
        headers={"Authorization": f"Bearer {_unverified_bearer(stranger.id)}"},
    )
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_unpublish_returns_to_none(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
) -> None:
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    layout_id = await _create_layout(client, project_id, _layout_config())
    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": "Layout, no datasets",
            "folder_id": home,
            "source": {
                "kind": "layout",
                "project_id": project_id,
                "layout_id": layout_id,
            },
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    publish_resp = await client.post(f"{settings.API_V2_STR}/template/{tid}/publish")
    assert publish_resp.status_code == 200, publish_resp.text
    assert publish_resp.json()["catalog_status"] == "published"

    unpublish_resp = await client.post(
        f"{settings.API_V2_STR}/template/{tid}/unpublish"
    )
    assert unpublish_resp.status_code == 200, unpublish_resp.text
    assert unpublish_resp.json()["catalog_status"] == "none"


async def _team_folder(db: AsyncSession, space_id: UUID, owner: UUID) -> UUID:
    """A team-space folder -- `make_folder` only targets personal spaces."""
    return (
        await db.execute(
            text(
                f"""
                INSERT INTO {S}.folder (id, name, user_id, space_id, updated_at)
                VALUES (gen_random_uuid(), :n, :u, :s, now())
                RETURNING id
                """
            ),
            {"n": f"f-{uuid4().hex[:6]}", "u": owner, "s": space_id},
        )
    ).scalar_one()


@pytest.mark.asyncio
async def test_grant_a_team_viewer_role_then_delete_it(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_org: Callable[[], Awaitable[Organization]],
    make_team: Callable[..., Awaitable[Team]],
    make_space: Callable[..., Awaitable[Space]],
) -> None:
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    layout_id = await _create_layout(client, project_id, _layout_config())
    create_resp = await client.post(
        f"{settings.API_V2_STR}/template",
        json={
            "name": "Team-shared template",
            "folder_id": home,
            "source": {
                "kind": "layout",
                "project_id": project_id,
                "layout_id": layout_id,
            },
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    # Template grants stay inside the owner's organization (D14), so the
    # owner and the team share one.
    org = await make_org()
    await db_session.execute(
        text(f'UPDATE {S}."user" SET organization_id = :o WHERE id = :u'),
        {"o": org.id, "u": fixture_create_user},
    )
    member = User(
        id=uuid4(),
        email=f"member-{uuid4().hex[:8]}@goat.test",
        firstname="Team",
        lastname="Member",
        avatar="",
        organization_id=org.id,
    )
    db_session.add(member)
    await db_session.flush()
    team = await make_team(member, org=org)
    await make_space(SpaceKind.team, team=team)
    await db_session.commit()
    member_headers = {"Authorization": f"Bearer {_unverified_bearer(member.id)}"}

    # Unshared: the member cannot read it yet.
    denied = await client.get(
        f"{settings.API_V2_STR}/template/{tid}", headers=member_headers
    )
    assert denied.status_code == 403, denied.text

    grant_resp = await client.post(
        f"{settings.API_V2_STR}/template/{tid}/grant",
        json={
            "grantee_type": "team",
            "grantee_id": str(team.id),
            "role": "template-viewer",
        },
    )
    assert grant_resp.status_code == 201, grant_resp.text
    grant = grant_resp.json()
    assert grant["grantee_type"] == "team"
    assert grant["role"] == "template-viewer"
    grant_id = grant["id"]

    listing = await client.get(f"{settings.API_V2_STR}/template/{tid}/grant")
    assert listing.status_code == 200, listing.text
    assert grant_id in {g["id"] for g in listing.json()["grants"]}

    read_resp = await client.get(
        f"{settings.API_V2_STR}/template/{tid}", headers=member_headers
    )
    assert read_resp.status_code == 200, read_resp.text
    assert read_resp.json()["my_role"] == "viewer"

    delete_resp = await client.delete(
        f"{settings.API_V2_STR}/template/{tid}/grant/{grant_id}"
    )
    assert delete_resp.status_code == 204, delete_resp.text

    denied_again = await client.get(
        f"{settings.API_V2_STR}/template/{tid}", headers=member_headers
    )
    assert denied_again.status_code == 403, denied_again.text
