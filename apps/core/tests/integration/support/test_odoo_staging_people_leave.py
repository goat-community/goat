"""People leave, contacts disappear: the real provider and service on staging.

Staff who leave (user archived or deleted), customer contacts that are archived,
deleted or merged, and colleagues whose stored contact was merged away. Needs
the bridge key (ODOO_SUPPORT_API_KEY) and an admin key (ODOO_ADMIN_KEY): the
admin plays Odoo's staff (creates a
throwaway internal user, archives, deletes, merges) and removes every record a
test created. The service runs on an in-memory store, so neither GOAT's
database nor its caches are involved.
"""

import json
import os
import uuid
from collections.abc import AsyncIterator
from typing import Any

import aiohttp
import pytest
from core.support.odoo_client import OdooRejected, SupportOdooClient
from core.support.odoo_provider import OdooSupportProvider
from core.support.service import SupportService
from core.support.throttle import RateLimiter, TTLCache
from core.support.types import EmailProof, NewTicket, TicketQuery
from tests.unit.support.fakes import ORG, MemoryStore

URL = os.environ.get("ODOO_URL", "")
DB = os.environ.get("ODOO_DB", "")
ACTION = "GOAT: post message as ticket participant"
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        "staging" not in URL
        or "staging" not in DB
        or not os.environ.get("ODOO_SUPPORT_API_KEY")
        or not os.environ.get("ODOO_ADMIN_KEY"),
        reason="needs staging Odoo, the bridge key and an admin key",
    ),
]


# Tickets first (they point at contacts), then employees and users, then contacts.
_CLEANUP_ORDER = ["helpdesk.ticket", "hr.employee", "res.users", "res.partner"]


class Admin:
    """Plain JSON-2 calls with the admin key; records what to delete afterwards."""

    def __init__(self) -> None:
        self.created: list[tuple[str, int]] = []

    async def call(self, model: str, method: str, **kw: Any) -> Any:
        assert "staging" in URL and "staging" in DB
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{URL.rstrip('/')}/json/2/{model}/{method}",
                data=json.dumps(kw),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"bearer {os.environ['ODOO_ADMIN_KEY']}",
                    "X-Odoo-Database": DB,
                },
            ) as response:
                body = await response.json(content_type=None)
                if response.status >= 400:
                    raise AssertionError(f"{model}.{method}: {body}")
                return body

    def track(self, model: str, record_id: int) -> int:
        self.created.append((model, record_id))
        return record_id

    async def cleanup(self) -> None:
        """Best effort over every record; fails at the end if any is left."""
        left = []
        for model, record_id in sorted(
            self.created, key=lambda c: _CLEANUP_ORDER.index(c[0])
        ):
            try:
                exists = await self.call(
                    model,
                    "search",
                    domain=[["id", "=", record_id]],
                    context={"active_test": False},
                )
                if exists:
                    await self.call(model, "unlink", ids=[record_id])
            except AssertionError:
                left.append((model, record_id))
        assert not left, f"left on staging: {left}"


@pytest.fixture
async def admin() -> AsyncIterator[Admin]:
    a = Admin()
    try:
        yield a
    finally:
        await a.cleanup()


@pytest.fixture
async def client() -> AsyncIterator[SupportOdooClient]:
    c = SupportOdooClient(URL, DB, os.environ["ODOO_SUPPORT_API_KEY"])
    yield c
    await c.close()


def _provider(client: SupportOdooClient) -> OdooSupportProvider:
    """A new provider each time: no cached staff answers or photos."""
    team = int(os.environ.get("ODOO_SUPPORT_TEAM_ID", "1"))
    return OdooSupportProvider(client, team_id=team, post_action_name=ACTION)


def _service(provider: OdooSupportProvider, store: MemoryStore) -> SupportService:
    async def keycloak(user_id: str) -> dict[str, Any]:
        """Keycloak verified everyone's stored email."""
        user = await store.load_user(uuid.UUID(user_id))
        return {"email": user.email, "emailVerified": True}

    return SupportService(
        provider,
        store,
        cache=TTLCache(),
        ticket_limiter=RateLimiter(50, 3600),
        reply_limiter=RateLimiter(50, 3600),
        email_proof=EmailProof(verified_email=None, trust_stored=True),
        keycloak_user=keycloak,
    )


def _email(tag: str) -> str:
    return f"goat-it-{tag}-{uuid.uuid4().hex[:8]}@example.invalid"


async def _contact(
    provider: OdooSupportProvider, admin: Admin, name: str, email: str
) -> int:
    cid = await provider.create_contact(
        name=name, email=email, lang="en", company_id=None
    )
    return admin.track("res.partner", cid)


async def _ticket(
    provider: OdooSupportProvider,
    admin: Admin,
    customer: int,
    subject: str,
    org_id: str | None = None,
) -> tuple[int, str]:
    t = await provider.create_ticket(
        NewTicket(
            subject=f"[TEST] edge {subject}",
            description_html="<p>edge case</p>",
            category="other",
            impact=None,
            customer_contact_id=customer,
            org_id=org_id,
            user_id="it-edge",
            request_id=uuid.uuid4().hex,
        )
    )
    admin.track("helpdesk.ticket", t.id)
    return t.id, t.ref


async def _merge(admin: Admin, source: int, into: int) -> None:
    """Odoo's own merge wizard (Contacts > Merge), as staff would run it."""
    (wizard,) = await admin.call(
        "base.partner.merge.automatic.wizard",
        "create",
        vals_list=[
            {
                "partner_ids": [[6, 0, [source, into]]],
                "dst_partner_id": into,
                "state": "selection",
            }
        ],
    )
    await admin.call(
        "base.partner.merge.automatic.wizard", "action_merge", ids=[wizard]
    )


async def _former_staff_checks(
    client: SupportOdooClient, ticket_id: int, ref: str, agent: int, email: str
) -> None:
    provider = _provider(client)
    detail = await provider.get_ticket(ref)
    assert detail is not None
    (reply,) = [m for m in detail.messages if m.author_contact_id == agent]
    assert reply.is_agent and reply.author_name == "GOAT IT Agent"
    assert detail.ticket.latest_message_is_agent
    assert {f.contact_id: f.is_internal for f in detail.followers}[agent] is True
    assert agent in detail.avatars  # the photo stays
    (listed,) = await provider.list_tickets(
        TicketQuery((detail.ticket.customer_contact_id or 0,), None, None, None)
    )
    assert listed.latest_message_is_agent
    # never linked to a GOAT user with that email, never a live customer contact
    assert await provider.find_contacts_by_email([email]) == {}
    assert await provider.contacts_exist([agent]) == set()
    # the server action refuses to post or rate as them
    with pytest.raises(OdooRejected, match="customer-side participant"):
        await provider.post_message(ticket_id, agent, "[TEST] as former staff", [])
    with pytest.raises(OdooRejected, match="customer-side participant"):
        await provider.rate(ticket_id, agent, "top", "")


# a 1x1 PNG
_PHOTO = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"


async def test_staff_who_leave_stay_staff(
    admin: Admin, client: SupportOdooClient
) -> None:
    provider = _provider(client)
    customer = await _contact(provider, admin, "GOAT IT Customer", _email("cust"))
    ticket_id, ref = await _ticket(provider, admin, customer, "staff leaves")
    # a throwaway agent: internal user + employee record, as Plan4Better's staff have
    agent_email = _email("agent")
    (group,) = await admin.call(
        "ir.model.data",
        "search_read",
        domain=[["module", "=", "base"], ["name", "=", "group_user"]],
        fields=["res_id"],
    )
    (uid,) = await admin.call(
        "res.users",
        "create",
        vals_list=[
            {
                "name": "GOAT IT Agent",
                "login": agent_email,
                "email": agent_email,
                "group_ids": [[6, 0, [group["res_id"]]]],
            }
        ],
        context={"no_reset_password": True},
    )
    (user,) = await admin.call("res.users", "read", ids=[uid], fields=["partner_id"])
    agent = user["partner_id"][0]
    admin.track("res.partner", agent)
    (employee,) = await admin.call(
        "hr.employee",
        "create",
        vals_list=[{"name": "GOAT IT Agent", "user_id": uid, "work_contact_id": agent}],
    )
    admin.track("hr.employee", employee)
    admin.track("res.users", uid)
    await admin.call("res.partner", "write", ids=[agent], vals={"image_1920": _PHOTO})
    await admin.call(
        "helpdesk.ticket",
        "message_post",
        ids=[ticket_id],
        body="Looking into it",
        message_type="comment",
        subtype_xmlid="mail.mt_comment",
        author_id=agent,
    )
    await admin.call(
        "helpdesk.ticket", "message_subscribe", ids=[ticket_id], partner_ids=[agent]
    )
    await admin.call("helpdesk.ticket", "write", ids=[ticket_id], vals={"user_id": uid})

    # A. archived: Odoo turns their partner into a share partner
    await admin.call("res.users", "write", ids=[uid], vals={"active": False})
    (row,) = await admin.call(
        "res.partner", "read", ids=[agent], fields=["partner_share"]
    )
    assert row["partner_share"] is True
    await _former_staff_checks(client, ticket_id, ref, agent, agent_email)
    detail = await _provider(client).get_ticket(ref)
    assert detail is not None and detail.ticket.agent_name == "GOAT IT Agent"

    # B. user deleted: Odoo refuses while an employee points at the user, so the
    # employee is detached first and stays; the partner stays without any user
    with pytest.raises(AssertionError, match="hr.employee"):
        await admin.call("res.users", "unlink", ids=[uid])
    await admin.call("hr.employee", "write", ids=[employee], vals={"user_id": False})
    await admin.call("res.users", "unlink", ids=[uid])
    await _former_staff_checks(client, ticket_id, ref, agent, agent_email)
    # D. Odoo unassigns the ticket of a deleted user
    detail = await _provider(client).get_ticket(ref)
    assert detail is not None and detail.ticket.agent_name is None

    # C. partner deleted too: the reply stays, from an unknown sender
    await admin.call("hr.employee", "unlink", ids=[employee])
    await admin.call("res.partner", "unlink", ids=[agent])
    detail = await _provider(client).get_ticket(ref)
    assert detail is not None
    (orphan,) = [m for m in detail.messages if m.body_html == "<p>Looking into it</p>"]
    assert (orphan.author_known, orphan.author_contact_id, orphan.is_agent) == (
        False,
        None,
        False,
    )


async def test_customer_contact_archived_deleted_or_merged(
    admin: Admin, client: SupportOdooClient
) -> None:
    provider = _provider(client)
    store = MemoryStore()

    # archived: unlinked; with no other contact for the email there is none
    email = _email("arch")
    archived = await _contact(provider, admin, "GOAT IT Archived", email)
    await _ticket(provider, admin, archived, "contact archived")
    me = store.add_user(email=email, contact_id=archived, org=None)
    await admin.call("res.partner", "write", ids=[archived], vals={"active": False})
    assert await _service(provider, store).list(me.id, "mine", "open") == []
    assert (await store.load_user(me.id)).contact_id is None

    # deleted: relinked to the remaining contact with the verified email
    email = _email("del")
    deleted = await _contact(provider, admin, "GOAT IT Deleted", email)
    survivor = await _contact(provider, admin, "GOAT IT Survivor", email)
    _, ref = await _ticket(provider, admin, survivor, "contact deleted")
    me = store.add_user(email=email, contact_id=deleted, org=None)
    await admin.call("res.partner", "unlink", ids=[deleted])
    items = await _service(provider, store).list(me.id, "mine", "open")
    assert [i.ticket.ref for i in items] == [ref]
    assert (await store.load_user(me.id)).contact_id == survivor

    # merged with Odoo's wizard: the source is gone, its tickets moved to the target
    email = _email("merge")
    source = await _contact(provider, admin, "GOAT IT Merge Source", email)
    target = await _contact(provider, admin, "GOAT IT Merge Target", email)
    ticket_id, ref = await _ticket(provider, admin, source, "contact merged")
    me = store.add_user(email=email, contact_id=source, org=None)
    await _merge(admin, source, target)
    assert await provider.contacts_exist([source, target]) == {target}
    service = _service(provider, store)
    items = await service.list(me.id, "mine", "open")
    assert [i.ticket.ref for i in items] == [ref]
    assert (await store.load_user(me.id)).contact_id == target
    result = await service.reply(me.id, ref, "[TEST] still me after the merge", ())
    assert result.message_id
    detail = await provider.get_ticket(ref)
    assert detail is not None and detail.messages[-1].author_contact_id == target


async def test_colleague_whose_contact_was_merged_is_linked_to_the_survivor(
    admin: Admin, client: SupportOdooClient
) -> None:
    provider = _provider(client)
    store = MemoryStore()
    me_contact = await _contact(provider, admin, "GOAT IT Me", _email("me"))
    ticket_id, ref = await _ticket(
        provider, admin, me_contact, "colleague merged", org_id=str(ORG)
    )
    anna_email = _email("anna")
    stale = await _contact(provider, admin, "GOAT IT Anna Old", anna_email)
    other = await _contact(provider, admin, "GOAT IT Anna Other", anna_email)
    await _merge(admin, stale, other)
    # following the merged-away contact is what happened before: Odoo answers
    # success and follows nobody, so the colleague silently never joined
    await provider.add_followers(ticket_id, [stale])
    before = await provider.get_ticket(ref)
    assert before is not None
    assert stale not in {f.contact_id for f in before.followers}

    me = store.add_user(email="me@example.invalid", contact_id=me_contact)
    anna = store.add_user(email=anna_email, name="GOAT IT Anna", contact_id=stale)
    await _service(provider, store).update_followers(me.id, ref, (anna.id,), ())
    # her email is verified: she is linked to the surviving contact of it
    assert (await store.load_user(anna.id)).contact_id == other
    detail = await provider.get_ticket(ref)
    assert detail is not None
    assert other in {f.contact_id for f in detail.followers if not f.is_internal}


async def test_customer_email_changed_in_odoo_keeps_the_link(
    admin: Admin, client: SupportOdooClient
) -> None:
    provider = _provider(client)
    store = MemoryStore()
    email = _email("old")
    contact = await _contact(provider, admin, "GOAT IT Moved", email)
    _, ref = await _ticket(provider, admin, contact, "email changed")
    me = store.add_user(email=email, contact_id=contact, org=None)
    await admin.call(
        "res.partner", "write", ids=[contact], vals={"email": _email("new")}
    )
    items = await _service(provider, store).list(me.id, "mine", "open")
    assert [i.ticket.ref for i in items] == [ref]
    assert (await store.load_user(me.id)).contact_id == contact
