from uuid import UUID, uuid4

import pytest
from core.core.config import settings
from core.db.models import Role, User
from core.support.store import SqlSupportStore
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import make_organization

pytestmark = pytest.mark.unit

S = settings.SCHEMA


async def _role(db: AsyncSession, name: str) -> tuple[UUID, bool]:
    """Return (role id, created): created roles are removed by the test."""
    rid = (
        await db.execute(select(Role.id).where(Role.name == name))
    ).scalar_one_or_none()
    if rid is not None:
        return rid, False
    role = Role(name=name, resource_type="organization")
    db.add(role)
    await db.flush()
    return role.id, True  # type: ignore[return-value]


async def test_load_user_with_org_role_and_language(
    db_session: AsyncSession, fixture_create_user: UUID
) -> None:
    org_id = uuid4()
    colleague_id = uuid4()
    db_session.add(make_organization(id=org_id, odoo_company_id=500))
    await db_session.flush()
    role_id, role_created = await _role(db_session, "organization-admin")
    colleague = User(
        id=colleague_id,
        email="Anna.Keller@Stadt.de",
        firstname="Anna",
        lastname="Keller",
        organization_id=org_id,
        odoo_contact_id=77,
    )
    try:
        await db_session.execute(
            text(f'UPDATE {S}."user" SET organization_id = :o WHERE id = :u'),
            {"o": org_id, "u": fixture_create_user},
        )
        await db_session.execute(
            text(f"INSERT INTO {S}.user_role (user_id, role_id) VALUES (:u, :r)"),
            {"u": fixture_create_user, "r": role_id},
        )
        db_session.add(colleague)
        await db_session.commit()

        store = SqlSupportStore(db_session)
        user = await store.load_user(fixture_create_user)
        assert user.org_id == org_id and user.is_org_admin and user.contact_id is None
        assert user.name == "Green GOAT" and user.lang in ("en", "de")
        assert await store.org_company_id(org_id) == 500
        members = {m.email: m for m in await store.org_members(org_id)}
        assert members["Anna.Keller@Stadt.de"].contact_id == 77
        assert fixture_create_user in {m.user_id for m in members.values()}

        await store.save_contact_id(fixture_create_user, 4242)
        assert (await store.load_user(fixture_create_user)).contact_id == 4242
        await store.clear_contact_id(fixture_create_user)
        assert (await store.load_user(fixture_create_user)).contact_id is None
    finally:
        await db_session.rollback()
        await db_session.execute(
            text(f'DELETE FROM {S}."user" WHERE id = :u'), {"u": colleague_id}
        )
        await db_session.execute(
            text(
                f'UPDATE {S}."user" SET organization_id = NULL, odoo_contact_id = NULL WHERE id = :u'
            ),
            {"u": fixture_create_user},
        )
        await db_session.execute(
            text(f"DELETE FROM {S}.user_role WHERE user_id = :u AND role_id = :r"),
            {"u": fixture_create_user, "r": role_id},
        )
        if role_created:
            await db_session.execute(
                text(f"DELETE FROM {S}.role WHERE id = :r"), {"r": role_id}
            )
        await db_session.execute(
            text(f"DELETE FROM {S}.organization WHERE id = :o"), {"o": org_id}
        )
        await db_session.commit()


async def test_read_markers_never_move_backwards(
    db_session: AsyncSession, fixture_create_user: UUID
) -> None:
    store = SqlSupportStore(db_session)
    await store.set_read_markers(fixture_create_user, {31: 70, 29: 50})
    await store.set_read_markers(fixture_create_user, {31: 60})
    assert await store.read_markers(fixture_create_user, [31, 29, 5]) == {
        31: 70,
        29: 50,
    }


async def test_the_seeded_contact_is_overwritten_not_maximised(
    db_session: AsyncSession, fixture_create_user: UUID
) -> None:
    store = SqlSupportStore(db_session)
    assert await store.seeded_contact(fixture_create_user) is None
    await store.set_seeded_contact(fixture_create_user, 5000)
    assert await store.seeded_contact(fixture_create_user) == 5000
    await store.set_seeded_contact(fixture_create_user, 100)  # relinked
    assert await store.seeded_contact(fixture_create_user) == 100
    # the marker row is no ticket: ticket lookups never see it
    await store.set_read_markers(fixture_create_user, {31: 70})
    assert await store.read_markers(fixture_create_user, [31]) == {31: 70}
