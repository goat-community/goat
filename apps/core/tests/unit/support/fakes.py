"""Test doubles for the support module."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from core.support.errors import SupportCompanyRefused, SupportStaffEmail
from core.support.types import (
    AttachmentMeta,
    Follower,
    Member,
    Message,
    NewTicket,
    PostResult,
    Status,
    SupportUser,
    Ticket,
    TicketDetail,
    TicketQuery,
    UploadedFile,
)

Handler = Callable[[dict[str, Any]], Any]


class FakeOdooClient:
    """Stands in for OdooClient: answers from registered handlers, records calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self._handlers: dict[tuple[str, str], Handler] = {}
        self._ops: dict[str, Handler] = {}

    def on(self, model: str, method: str, handler: Handler) -> "FakeOdooClient":
        self._handlers[(model, method)] = handler
        return self

    def on_op(self, op: str, handler: Handler) -> "FakeOdooClient":
        """Answer one server action op (`handler` gets the context), whatever
        answers the other runs."""
        self._ops[op] = handler
        return self

    async def call(self, model: str, method: str, **kwargs: Any) -> Any:
        self.calls.append((model, method, kwargs))
        op = (kwargs.get("context") or {}).get("goat_op")
        if (model, method) == ("ir.actions.server", "run") and op in self._ops:
            return self._ops[op](kwargs["context"])
        handler = self._handlers.get((model, method))
        if handler is None:
            raise AssertionError(f"unexpected Odoo call {model}.{method} {kwargs}")
        return handler(kwargs)

    def calls_to(self, model: str, method: str) -> list[dict[str, Any]]:
        return [kw for m, meth, kw in self.calls if (m, meth) == (model, method)]


STAGES = [
    {"id": 1, "name": "New"},
    {"id": 2, "name": "In Progress"},
    {"id": 3, "name": "Waiting on Customer"},
    {"id": 4, "name": "Solved"},
    {"id": 5, "name": "Cancelled"},
]
TAGS = [
    {"id": 1, "name": "bug"},
    {"id": 3, "name": "how-to"},
    {"id": 4, "name": "data-question"},
    {"id": 2, "name": "feature-request"},
    {"id": 5, "name": "account-billing"},
]


def ticket_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "id": 31,
        "ticket_ref": "00031",
        "name": "Catchment area fails",
        "stage_id": [2, "In Progress"],
        "tag_ids": [1],
        "priority": "2",
        "partner_id": [100, "Marco Albrecht"],
        "user_id": [10, "Lena Schmidt"],
        "create_date": "2026-09-28 09:14:00",
        "write_date": "2026-09-30 11:02:00",
        "close_date": False,
        "x_goat_organization_id": "org-1",
        "x_goat_request_id": "req-1",
    }
    record.update(overrides)
    return record


def staff_op(staff: Sequence[int] = ()) -> Handler:
    """The server action's "staff" op: which of the asked partners are (former) staff."""

    def handler(kw: dict[str, Any]) -> Any:
        ctx = kw.get("context") or {}
        assert ctx.get("goat_op") == "staff", ctx
        return {"goat_staff_ids": [p for p in ctx["goat_partner_ids"] if p in staff]}

    return handler


def action_ops(
    staff: Sequence[int] = (),
    agent_partner: int | None = None,
    people: Mapping[int, Mapping[str, Any]] | None = None,
    contacts: Mapping[str, int] | None = None,
    goat_contacts: Sequence[int] = (),
) -> Handler:
    """The server action's read-only ops, answered like the goat_support module does.

    `staff`: former staff (the "staff" op names them; staff in "people" and
    "exist" too). `agent_partner`: the "agent" op's answer. `people`: the
    participants "people" knows, {id: {"name", "staff", "photo"?}}; it sends a
    photo of staff only, when asked for photos. `contacts`: what "find"
    matches, {normalized email: id}. `goat_contacts`: the active GOAT contacts
    "exist" answers for.
    """
    staff_handler = staff_op(staff)
    known = people or {}
    matches = contacts or {}

    def handler(kw: dict[str, Any]) -> Any:
        ctx = kw.get("context") or {}
        op = ctx.get("goat_op")
        if op == "agent":
            return {"goat_agent_partner_id": agent_partner or False}
        if op == "people":
            found = []
            for pid in ctx["goat_partner_ids"]:
                if pid not in known:
                    continue
                is_staff = bool(known[pid].get("staff")) or pid in staff
                person = {
                    "id": pid,
                    "name": known[pid].get("name") or "",
                    "staff": is_staff,
                }
                if ctx.get("goat_with_photos") and is_staff and known[pid].get("photo"):
                    person["photo"] = known[pid]["photo"]
                found.append(person)
            return {"goat_people": found}
        if op == "find":
            return {
                "goat_contacts": {
                    e: matches[e] for e in ctx["goat_emails"] if e in matches
                }
            }
        if op == "followers":
            return {"goat_partner_ids": []}
        if op == "followed":
            return {"goat_ticket_ids": []}
        if op == "my_rating":
            return {"goat_rating": False}
        if op == "exist":
            return {
                "goat_contact_ids": [
                    p
                    for p in ctx["goat_partner_ids"]
                    if p in goat_contacts and p not in staff
                ]
            }
        return staff_handler(kw)

    return handler


def op_calls(odoo: FakeOdooClient, op: str) -> list[dict[str, Any]]:
    """The contexts of the server action runs of one op, in order."""
    return [
        kw["context"]
        for kw in odoo.calls_to("ir.actions.server", "run")
        if (kw.get("context") or {}).get("goat_op") == op
    ]


def base_odoo(
    staff: Sequence[int] = (),
    agent_partner: int | None = None,
    people: Mapping[int, Mapping[str, Any]] | None = None,
    contacts: Mapping[str, int] | None = None,
    goat_contacts: Sequence[int] = (),
) -> FakeOdooClient:
    """A fake with stages, tags, public subtypes and the post action registered.

    The keyword arguments are what the server action's read-only ops answer
    (see action_ops).
    """
    return (
        FakeOdooClient()
        .on(
            "ir.actions.server",
            "run",
            action_ops(staff, agent_partner, people, contacts, goat_contacts),
        )
        .on("helpdesk.stage", "search_read", lambda kw: STAGES)
        .on("helpdesk.tag", "search_read", lambda kw: TAGS)
        .on(
            "mail.message.subtype", "search_read", lambda kw: [{"id": 1}]
        )  # 1 = "Discussions"
        .on("ir.actions.server", "search", lambda kw: [1562])
        .on("res.users", "context_get", lambda kw: {"uid": 16, "lang": "en_US"})
        .on(
            "res.users",
            "read",
            lambda kw: [{"id": 16, "partner_id": [43402, "GOAT Support Bot"]}],
        )
    )


# --------------------------------------------------------------------------
# Service-level doubles
# --------------------------------------------------------------------------

T0 = datetime(2026, 9, 28, 9, 0, tzinfo=UTC)
ORG = uuid4()


def make_ticket(**overrides: Any) -> Ticket:
    base = dict(
        id=31,
        ref="00031",
        subject="Catchment area fails",
        status="in_progress",
        category="bug",
        impact="blocking",
        customer_contact_id=100,
        customer_name="Marco",
        agent_name="Lena",
        org_id=str(ORG),
        request_id="req-1",
        via="app",
        created_at=T0,
        updated_at=T0,
        closed_at=None,
        latest_message_id=60,
        latest_message_author="Marco",
        latest_message_is_agent=False,
        latest_message_at=T0,
    )
    base.update(overrides)
    return Ticket(**base)  # type: ignore[arg-type]


def make_message(
    id: int,
    author: int,
    *,
    agent: bool = False,
    attachments: tuple[AttachmentMeta, ...] = (),
) -> Message:
    return Message(
        id, author, f"p{author}", agent, "app", T0, f"<p>m{id}</p>", attachments
    )


class FakeProvider:
    def __init__(self) -> None:
        self.contacts: dict[str, int] = {}
        self.created_contacts: list[dict[str, Any]] = []
        self.tickets: dict[str, TicketDetail] = {}
        self.stamped: list[tuple[tuple[int, ...], str]] = []
        self.created: list[NewTicket] = []
        self.posts: list[tuple[int, int, str, tuple[str, ...]]] = []
        self.statuses: list[tuple[int, Status]] = []
        self.follower_changes: list[tuple[str, int, tuple[int, ...]]] = []
        self.ratings: list[tuple[int, int, str, str]] = []
        self.my_ratings: dict[tuple[int, int], str] = {}
        self.my_rating_error: Exception | None = None
        self.my_rating_calls: list[tuple[int, int]] = []
        self.next_contact = 5000
        self.bridge: int | None = 7  # the bridge user's own partner
        self.email_lookups: list[tuple[str, ...]] = []
        self.dead_contacts: set[int] = set()  # deleted, archived or merged away
        self.contact_checks: list[tuple[int, ...]] = []
        self.contacts_exist_error: Exception | None = None
        self.refused_companies: set[int] = set()  # the contact op's parent guard
        self.staff_emails: set[str] = set()  # the contact op's staff guard
        self.list_calls = 0

    def add(
        self,
        ticket: Ticket,
        messages: tuple[Message, ...] = (),
        followers: tuple[Follower, ...] = (),
    ) -> None:
        self.tickets[ticket.ref] = TicketDetail(ticket, messages, followers)

    async def bridge_contact_id(self) -> int | None:
        return self.bridge

    async def find_contacts_by_email(
        self, emails: Sequence[str], prefer_company_id: int | None = None
    ) -> dict[str, int]:
        self.email_lookups.append(tuple(emails))
        return {
            e.strip().lower(): self.contacts[e.strip().lower()]
            for e in emails
            if e.strip().lower() in self.contacts
        }

    async def contacts_exist(self, contact_ids: Sequence[int]) -> set[int]:
        self.contact_checks.append(tuple(contact_ids))
        if self.contacts_exist_error is not None:
            raise self.contacts_exist_error
        return {c for c in contact_ids if c not in self.dead_contacts}

    async def create_contact(
        self, *, name: str, email: str, lang: str, company_id: int | None
    ) -> int:
        if company_id in self.refused_companies:
            raise SupportCompanyRefused("invalid parent company")
        if email.lower() in self.staff_emails:
            raise SupportStaffEmail("email belongs to staff")
        self.next_contact += 1
        self.contacts[email.lower()] = self.next_contact
        self.created_contacts.append(
            {"name": name, "email": email, "lang": lang, "company_id": company_id}
        )
        return self.next_contact

    async def list_tickets(self, query: TicketQuery) -> list[Ticket]:
        self.list_calls += 1
        out = []
        for d in self.tickets.values():
            t = d.ticket
            followed = query.follower_contact_id in {f.contact_id for f in d.followers}
            match = (
                t.customer_contact_id in query.customer_ids
                or followed
                or (query.org_id is not None and t.org_id == query.org_id)
            )
            if query.open is not None and t.is_open != query.open:
                match = False
            if query.request_id and t.request_id != query.request_id:
                match = False
            if match:
                out.append(t)
        return out

    async def get_ticket(self, ref: str) -> TicketDetail | None:
        return self.tickets.get(ref)

    async def stamp_org(self, ticket_ids: Sequence[int], org_id: str) -> None:
        self.stamped.append((tuple(ticket_ids), org_id))
        for ref, d in list(self.tickets.items()):
            if d.ticket.id in ticket_ids:
                self.tickets[ref] = replace(d, ticket=replace(d.ticket, org_id=org_id))

    async def create_ticket(self, new: NewTicket) -> Ticket:
        self.created.append(new)
        t = make_ticket(
            id=40 + len(self.created),
            ref=f"{40 + len(self.created):05d}",
            subject=new.subject,
            status="new",
            customer_contact_id=new.customer_contact_id,
            org_id=new.org_id,
            request_id=new.request_id,
            latest_message_id=None,
            latest_message_author=None,
            latest_message_at=None,
        )
        self.add(t)
        return t

    async def post_message(
        self,
        ticket_id: int,
        author_contact_id: int,
        text: str,
        files: Sequence[UploadedFile],
    ) -> PostResult:
        self.posts.append(
            (ticket_id, author_contact_id, text, tuple(f.name for f in files))
        )
        failed = tuple(f.name for f in files if f.name.startswith("broken"))
        return PostResult(message_id=900 + len(self.posts), failed_files=failed)

    async def set_status(self, ticket_id: int, status: Status) -> None:
        self.statuses.append((ticket_id, status))

    async def add_followers(self, ticket_id: int, contact_ids: Sequence[int]) -> None:
        self.follower_changes.append(("add", ticket_id, tuple(contact_ids)))

    async def remove_followers(
        self, ticket_id: int, contact_ids: Sequence[int]
    ) -> None:
        self.follower_changes.append(("remove", ticket_id, tuple(contact_ids)))

    async def rate(
        self, ticket_id: int, contact_id: int, rating: str, comment: str
    ) -> None:
        self.ratings.append((ticket_id, contact_id, rating, comment))

    async def my_rating(self, ticket_id: int, contact_id: int) -> str | None:
        self.my_rating_calls.append((ticket_id, contact_id))
        if self.my_rating_error is not None:
            raise self.my_rating_error
        return self.my_ratings.get((ticket_id, contact_id))

    async def download(self, attachment_id: int) -> tuple[AttachmentMeta, bytes]:
        return AttachmentMeta(attachment_id, "f.png", "image/png", 3), b"PNG"


class MemoryStore:
    def __init__(self) -> None:
        self.users: dict[UUID, SupportUser] = {}
        self.members: dict[UUID, list[Member]] = {}
        self.companies: dict[UUID, int] = {}
        self.markers: dict[UUID, dict[int, int]] = {}
        self.cleared: list[UUID] = []

    def add_user(
        self,
        *,
        email: str,
        admin: bool = False,
        contact_id: int | None = None,
        org: UUID | None = ORG,
        name: str = "Marco Albrecht",
        user_id: UUID | None = None,
    ) -> SupportUser:
        u = SupportUser(user_id or uuid4(), email, name, "de", org, admin, contact_id)
        self.users[u.id] = u
        if org:
            self.members.setdefault(org, []).append(
                Member(u.id, email, name, contact_id)
            )
        return u

    async def load_user(self, user_id: UUID) -> SupportUser:
        return self.users[user_id]

    async def save_contact_id(self, user_id: UUID, contact_id: int) -> None:
        self.users[user_id] = replace(self.users[user_id], contact_id=contact_id)
        for org, ms in self.members.items():
            self.members[org] = [
                replace(m, contact_id=contact_id) if m.user_id == user_id else m
                for m in ms
            ]

    async def clear_contact_id(self, user_id: UUID) -> None:
        self.cleared.append(user_id)
        self.users[user_id] = replace(self.users[user_id], contact_id=None)
        for org, ms in self.members.items():
            self.members[org] = [
                replace(m, contact_id=None) if m.user_id == user_id else m for m in ms
            ]

    async def org_company_id(self, org_id: UUID) -> int | None:
        return self.companies.get(org_id)

    async def org_members(self, org_id: UUID) -> list[Member]:
        return list(self.members.get(org_id, []))

    async def seeded_contact(self, user_id: UUID) -> int | None:
        return self.markers.get(user_id, {}).get(0)

    async def set_seeded_contact(self, user_id: UUID, contact_id: int) -> None:
        self.markers.setdefault(user_id, {})[0] = contact_id

    async def read_markers(
        self, user_id: UUID, ticket_ids: Sequence[int]
    ) -> dict[int, int]:
        mine = self.markers.get(user_id, {})
        return {t: mine[t] for t in ticket_ids if t in mine}

    async def set_read_markers(self, user_id: UUID, markers: Mapping[int, int]) -> None:
        mine = self.markers.setdefault(user_id, {})
        for t, msg in markers.items():
            mine[t] = max(mine.get(t, 0), msg)


def at(seconds: float) -> datetime:
    """A write date `seconds` after T0."""
    return T0 + timedelta(seconds=seconds)
