"""Fixtures that make the PL/pgSQL authorization functions testable.

conftest.py builds test_schema with create_all and runs with AUTH=False, so the
functions under db/sql/functions/authz are never installed and never exercised.
This installs them (add-only — CREATE OR REPLACE — so the shared `basic`
schema on the dev database is never dropped) and seeds roles/resources.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from core.core.config import settings
from core.db.models._link_model import UserTeamLink
from core.db.models.folder import Folder
from core.db.models.layer import Layer
from core.db.models.organization import Organization
from core.db.models.project import Project
from core.db.models.role import Role
from core.db.models.space import Space, SpaceDefaultRole, SpaceKind
from core.db.models.team import Team
from core.db.models.user import User
from core.db.seed_roles import seed_roles
from core.db.sql.create_functions import AsyncFunctionManager
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import make_organization

S = settings.SCHEMA


async def _personal_space(db_session: AsyncSession, user: User) -> UUID:
    row = (
        await db_session.execute(
            select(Space.id).where(
                Space.kind == SpaceKind.personal, Space.user_id == user.id
            )
        )
    ).scalar_one_or_none()
    if row is not None:
        return cast(UUID, row)
    space = Space(
        kind=SpaceKind.personal, user_id=user.id, default_role=SpaceDefaultRole.editor
    )
    db_session.add(space)
    await db_session.flush()
    assert space.id is not None
    return space.id


@pytest_asyncio.fixture
async def authz_sql(db_session: AsyncSession) -> None:
    manager = AsyncFunctionManager(
        session=db_session,
        path="functions/authz",
        schema="basic",
        schema_mapping={"basic": "basic", "customer": S},
    )
    await manager.add_functions()
    await seed_roles(db_session)  # commits


@pytest_asyncio.fixture
async def roles(db_session: AsyncSession, authz_sql: None) -> dict[str, UUID]:
    rows = (await db_session.execute(select(Role.name, Role.id))).all()
    return {name: rid for name, rid in rows}


@pytest_asyncio.fixture
async def make_user(db_session: AsyncSession) -> Callable[..., Awaitable[User]]:
    async def _make(organization_id: UUID | None = None) -> User:
        uid = uuid4()
        user = User(
            id=uid,
            email=f"authz-{uid.hex[:8]}@goat.test",
            firstname="Authz",
            lastname="Test",
            avatar="",
            organization_id=organization_id,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    return _make


@pytest_asyncio.fixture
async def make_org(db_session: AsyncSession) -> Callable[[], Awaitable[Organization]]:
    async def _make() -> Organization:
        org = make_organization(id=uuid4())
        db_session.add(org)
        await db_session.flush()
        db_session.add(
            Space(
                kind=SpaceKind.organization,
                organization_id=org.id,
                default_role=SpaceDefaultRole.viewer,
            )
        )
        await db_session.flush()
        return org

    return _make


@pytest_asyncio.fixture
async def make_space(db_session: AsyncSession) -> Callable[..., Awaitable[Space]]:
    async def _make(
        kind: SpaceKind,
        *,
        user: User | None = None,
        team: Team | None = None,
        org: Organization | None = None,
        default_role: SpaceDefaultRole | None = None,
    ) -> Space:
        owner = {
            "user_id": user.id if user else None,
            "team_id": team.id if team else None,
            "organization_id": org.id if org else None,
        }
        existing = (
            await db_session.execute(
                select(Space).filter_by(
                    kind=kind.value, **{k: v for k, v in owner.items() if v is not None}
                )
            )
        ).scalar_one_or_none()
        if existing:
            return existing
        role = default_role or (
            SpaceDefaultRole.viewer
            if kind == SpaceKind.organization
            else SpaceDefaultRole.editor
        )
        space = Space(kind=kind, default_role=role, **owner)
        db_session.add(space)
        await db_session.flush()
        return space

    return _make


@pytest_asyncio.fixture
async def make_team(
    db_session: AsyncSession, roles: dict[str, UUID]
) -> Callable[..., Awaitable[Team]]:
    async def _make(*members: User, org: Organization | None = None) -> Team:
        organization_id = (
            org.id if org else (members[0].organization_id if members else None)
        )
        team = Team(
            id=uuid4(),
            name=f"team-{uuid4().hex[:6]}",
            avatar="",
            organization_id=organization_id,
        )
        db_session.add(team)
        await db_session.flush()
        for m in members:
            db_session.add(
                UserTeamLink(
                    user_id=m.id, team_id=team.id, role_id=roles["team-member"]
                )
            )
        await db_session.flush()
        return team

    return _make


@pytest_asyncio.fixture
async def make_folder(db_session: AsyncSession) -> Callable[..., Awaitable[Folder]]:
    async def _make(owner: User, name: str | None = None) -> Folder:
        folder = Folder(
            id=uuid4(),
            user_id=owner.id,
            space_id=await _personal_space(db_session, owner),
            name=name or f"f-{uuid4().hex[:6]}",
        )
        db_session.add(folder)
        await db_session.flush()
        return folder

    return _make


@pytest_asyncio.fixture
async def make_layer(db_session: AsyncSession) -> Callable[..., Awaitable[Layer]]:
    async def _make(owner: User, folder: Folder) -> Layer:
        layer = Layer(
            id=uuid4(),
            user_id=owner.id,
            folder_id=folder.id,
            space_id=await _personal_space(db_session, owner),
            name=f"layer-{uuid4().hex[:6]}",
            type="feature",
            feature_layer_type="standard",
            feature_layer_geometry_type="polygon",
        )
        db_session.add(layer)
        await db_session.flush()
        return layer

    return _make


@pytest_asyncio.fixture
async def make_project(db_session: AsyncSession) -> Callable[..., Awaitable[Project]]:
    async def _make(owner: User, folder: Folder) -> Project:
        project = Project(
            id=uuid4(),
            user_id=owner.id,
            folder_id=folder.id,
            space_id=await _personal_space(db_session, owner),
            name=f"p-{uuid4().hex[:6]}",
        )
        db_session.add(project)
        await db_session.flush()
        return project

    return _make


async def find_resource(db: AsyncSession, url_pattern: str, method: str) -> UUID:
    row = (
        await db.execute(
            text(
                f"SELECT id FROM {S}.resource WHERE url_pattern = :p AND :m = ANY(method)"
            ),
            {"p": url_pattern, "m": method},
        )
    ).scalar_one()
    return cast(UUID, row)


async def _call(db: AsyncSession, sql: str, params: dict[str, object]) -> bool:
    """Run a check_* function; True if it returned, False if it raised.

    The engine runs with isolation_level="AUTOCOMMIT" (db/session.py), so
    there is no live transaction for ``begin_nested()`` to place a SAVEPOINT
    in — Postgres rejects it with "SAVEPOINT can only be used in transaction
    blocks". A plain rollback() is enough to clear the ORM Session's
    bookkeeping after a raised DBAPIError; it does not undo any statement
    (each already committed on its own under AUTOCOMMIT).
    """
    try:
        result = await db.execute(text(sql), params)
        return bool(result.scalar())
    except DBAPIError:
        await db.rollback()
        return False


async def call_check_project(
    db: AsyncSession,
    *,
    resource_id: UUID,
    user_id: UUID,
    organization_id: UUID | None,
    project_ids: list[UUID],
) -> bool:
    return await _call(
        db,
        f"SELECT {S}.check_project(:rid, :uid, :oid, CAST(:pids AS uuid[]))",
        {
            "rid": resource_id,
            "uid": user_id,
            "oid": organization_id,
            "pids": project_ids,
        },
    )


async def call_check_layer(
    db: AsyncSession,
    *,
    resource_id: UUID,
    user_id: UUID,
    organization_id: UUID | None,
    layer_ids: list[UUID],
) -> bool:
    return await _call(
        db,
        f"SELECT {S}.check_layer(:rid, :uid, :oid, CAST(:lids AS uuid[]))",
        {"rid": resource_id, "uid": user_id, "oid": organization_id, "lids": layer_ids},
    )


async def call_check_team(
    db: AsyncSession, *, user_id: UUID, team_ids: list[UUID], resource_id: UUID
) -> bool:
    return await _call(
        db,
        f"SELECT {S}.check_team(:uid, CAST(:tids AS uuid[]), :rid)",
        {"uid": user_id, "tids": team_ids, "rid": resource_id},
    )


# --- Real authorization (AUTH on) -------------------------------------------
#
# The rest of the suite runs with AUTH=False, where auth_z returns True and no
# token is verified, so the route layer is never exercised over HTTP. A module
# that requests `auth_on` runs its requests the way production does: tokens
# are RS256-signed by a key generated for the test session, verified by the
# same KeycloakAuth instance the app uses, and every auth_z route goes through
# authorization() for real. Keycloak itself is never contacted: the public key
# is set on the instance before any request needs it.

_RSA_KEYS: tuple[str, str] | None = None


def _rsa_keys() -> tuple[str, str]:
    global _RSA_KEYS
    if _RSA_KEYS is None:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        public_pem = (
            key.public_key()
            .public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )
        _RSA_KEYS = (private_pem, public_pem)
    return _RSA_KEYS


def signed_token(
    user_id: UUID,
    *,
    roles: list[str] | None = None,
    private_pem: str | None = None,
    **claims: object,
) -> str:
    """An RS256 token the app accepts while `auth_on` is active."""
    import time

    from core.deps.auth import ISSUER_URL
    from jose import jwt

    payload: dict[str, object] = {
        "sub": str(user_id),
        "email": f"{str(user_id)[:8]}@goat.test",
        "given_name": "Auth",
        "family_name": "Test",
        "iss": ISSUER_URL,
        "exp": int(time.time()) + 600,
        "realm_access": {"roles": roles or []},
        **claims,
    }
    return jwt.encode(payload, private_pem or _rsa_keys()[0], algorithm="RS256")


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_on(
    authz_sql: None, monkeypatch: "pytest.MonkeyPatch"
) -> Callable[..., dict[str, str]]:
    """Switch real authorization on for one test; returns a header factory."""
    from core.deps import auth as auth_module

    monkeypatch.setattr(settings, "AUTH", True)
    monkeypatch.setattr(auth_module._keycloak_auth, "_verify_signature", True)
    monkeypatch.setattr(auth_module._keycloak_auth, "_public_key", _rsa_keys()[1])

    def headers(user_id: UUID, *, roles: list[str] | None = None) -> dict[str, str]:
        return bearer(signed_token(user_id, roles=roles))

    return headers
