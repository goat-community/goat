"""SupportProvider on Odoo Helpdesk, as the bridge portal user ("GOAT Support Bot").

The bridge cannot read ir.model, cannot post as someone else and cannot create
or edit contacts: customer posts, ratings and new contacts go through the server
action of the goat_support Odoo module. It reads no contacts, followers or
ratings either, so finding contacts by email, checking stored links, names and
photos of ticket participants, followers, followed tickets and ratings are
server action ops as well. Odoo stores log notes and automatic mails as
comment / non-internal messages with an internal subtype, and the bridge
cannot read internal subtypes, so "customer facing" is an allow-list of public
subtypes (see odoo_mapping.is_customer_facing), not only a message_type check.

"Staff" is more than `partner_share = False`: Odoo recomputes partner_share
from active users only, so the partner of an archived (or deleted) staff user
turns customer-side. The bridge cannot read users or employees; the server
action's read-only "staff" op answers which partners are or were staff, and
every staff decision here (agent replies, internal followers, staff photos,
contacts a GOAT user may be linked to) uses it.
"""

import base64
import logging
import unicodedata
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta
from typing import Any, Literal

from core.support import odoo_mapping as m
from core.support.errors import (
    SupportCompanyRefused,
    SupportStaffEmail,
    SupportUnavailable,
)
from core.support.odoo_client import OdooRejected, SupportOdooClient
from core.support.throttle import TTLCache
from core.support.types import (
    AttachmentMeta,
    Follower,
    Message,
    NewTicket,
    PostResult,
    Rating,
    Status,
    Ticket,
    TicketDetail,
    TicketQuery,
    UploadedFile,
)

TICKET_FIELDS = [
    "ticket_ref",
    "name",
    "stage_id",
    "tag_ids",
    "priority",
    "partner_id",
    "user_id",
    "create_date",
    "write_date",
    "close_date",
    "x_goat_organization_id",
    "x_goat_request_id",
]
RATING_VALUE: dict[Rating, int] = {"ko": 1, "ok": 3, "top": 5}
_LANG = {"en": "en_US", "de": "de_DE"}
LIST_LIMIT = 200
# The files of a new ticket are posted right after it is created, as a message
# without text; within this window it is shown as part of the description.
FILES_MESSAGE_WINDOW = timedelta(minutes=10)
AVATAR_TTL = 3600.0
# Who is (or was) staff changes rarely: when someone joins or leaves.
STAFF_TTL = 600.0
# The assigned agent's partner: keyed by ticket and handler, so a reassignment shows at once.
AGENT_TTL = 600.0
# A server action from before the "agent" op answers "unknown operation": asked again after this.
AGENT_OP_MISSING_TTL = 600.0
# The server action's partner ops (staff, people, exist) refuse larger batches.
STAFF_BATCH = 1000
# The server action's "find" op takes this many emails at once.
FIND_BATCH = 50
# The contact op refuses longer names.
CONTACT_NAME_MAX = 200

logger = logging.getLogger(__name__)


def _required_datetime(value: str | None) -> datetime:
    parsed: datetime | None = m.parse_datetime(value)
    if parsed is None:
        raise ValueError("Odoo record is missing a required datetime")
    return parsed


class OdooSupportProvider:
    def __init__(
        self, client: SupportOdooClient, *, team_id: int, post_action_name: str
    ) -> None:
        self._odoo = client
        self._team_id = team_id
        self._post_action_name = post_action_name
        self._stage_status: dict[int, Status] | None = None
        self._tag_names: dict[int, str] | None = None
        self._action_id: int | None = None
        self._public_subtype_ids: frozenset[int] | None = None
        self._bridge_partner_id: int | None = None
        # staff photo per partner id; "" = known to have none
        self._avatars = TTLCache(max_size=2_000)
        # per partner id: True = current or former staff
        self._staff_flags = TTLCache(max_size=50_000)
        # per (ticket id, handler user id): the handler's partner id, 0 = none;
        # ("agent_op_missing",): the server action has no "agent" op yet
        self._agent_partners = TTLCache()

    # ----------------------------------------------------------------- lookups
    # Stages, tags and subtypes are cached for the life of the process, but an
    # empty answer never is: it would break status mapping, tagging or the
    # thread until the next restart.
    async def _stages(self) -> dict[int, Status]:
        if self._stage_status is None:
            rows = await self._odoo.call(
                "helpdesk.stage",
                "search_read",
                domain=[["team_ids", "in", [self._team_id]]],
                fields=["name"],
                context={"lang": "en_US"},
            )
            stages: dict[int, Status] = {
                r["id"]: m.STATUS_BY_STAGE_NAME[r["name"]]
                for r in rows
                if r["name"] in m.STATUS_BY_STAGE_NAME
            }
            if not stages:
                return stages
            self._stage_status = stages
        return self._stage_status

    async def _stage_id(self, status: Status) -> int:
        for stage_id, s in (await self._stages()).items():
            if s == status:
                return stage_id
        raise LookupError(f"no Odoo stage for status {status}")

    async def _tags(self) -> dict[int, str]:
        if self._tag_names is None:
            wanted = [t for t in m.TAG_BY_CATEGORY.values() if t]
            rows = await self._odoo.call(
                "helpdesk.tag",
                "search_read",
                domain=[["name", "in", wanted]],
                fields=["name"],
            )
            tags = {r["id"]: r["name"] for r in rows}
            if not tags:
                return tags
            self._tag_names = tags
        return self._tag_names

    async def _public_subtypes(self) -> frozenset[int]:
        # The portal bridge cannot read internal subtypes (it gets []), so the
        # filter is an allow-list of the public ones it can read. An empty
        # answer is never cached: it would hide every message until restart.
        if self._public_subtype_ids is None:
            rows = await self._odoo.call(
                "mail.message.subtype",
                "search_read",
                domain=[["internal", "=", False]],
                fields=["id"],
            )
            ids = frozenset(int(r["id"]) for r in rows)
            if not ids:
                return ids
            self._public_subtype_ids = ids
        return self._public_subtype_ids

    async def _post_action(self) -> int:
        if self._action_id is None:
            ids = await self._odoo.call(
                "ir.actions.server",
                "search",
                domain=[["name", "=", self._post_action_name]],
            )
            if not ids:
                raise LookupError(
                    f"Odoo server action {self._post_action_name!r} not found"
                )
            self._action_id = int(ids[0])
        return self._action_id

    async def bridge_contact_id(self) -> int | None:
        """The bridge user's own partner (read once): never a customer contact."""
        if self._bridge_partner_id is None:
            context = await self._odoo.call("res.users", "context_get")
            uid = int((context or {}).get("uid") or 0)
            if not uid:
                return None
            rows = await self._odoo.call(
                "res.users", "read", ids=[uid], fields=["partner_id"]
            )
            partner = m.many2one_id(rows[0].get("partner_id")) if rows else None
            if partner is None:
                return None
            self._bridge_partner_id = partner
        return self._bridge_partner_id

    async def _run_op(
        self, op: str, ticket_id: int | None = None, **values: Any
    ) -> dict[str, Any]:
        """One read-only operation of the server action, `values` as its context,
        on `ticket_id` when given."""
        try:
            action = await self._post_action()
        except LookupError as exc:
            raise SupportUnavailable(str(exc)) from exc
        context: dict[str, Any] = {"goat_op": op, **values}
        if ticket_id is not None:
            context |= {
                "active_model": "helpdesk.ticket",
                "active_id": ticket_id,
                "active_ids": [ticket_id],
            }
        result = await self._odoo.call(
            "ir.actions.server", "run", ids=[action], context=context
        )
        return result or {}

    async def _staff(self, partner_ids: Iterable[int]) -> set[int]:
        """Which of these partners are or were staff (an internal user or an
        employee record, active or archived), from the server action.

        Answers are cached per partner for STAFF_TTL; a failure raises
        SupportUnavailable / OdooRejected and caches nothing.
        """
        ids = sorted({p for p in partner_ids if p})
        missing = [p for p in ids if self._staff_flags.get(("staff", p)) is None]
        if missing:
            for start in range(0, len(missing), STAFF_BATCH):
                batch = missing[start : start + STAFF_BATCH]
                result = await self._run_op("staff", goat_partner_ids=batch)
                staff = {int(i) for i in result.get("goat_staff_ids") or []}
                for pid in batch:
                    self._staff_flags.set(("staff", pid), pid in staff, STAFF_TTL)
        return {p for p in ids if self._staff_flags.get(("staff", p))}

    async def _agent_partner(self, ticket_id: int, handler_user_id: int) -> int | None:
        """The assigned agent's partner id, from the server action's read-only "agent" op.

        The bridge cannot read users, and the partner is only known from the
        ticket's messages once the agent has written. Cosmetic (the photo of
        "Handled by"): a failure gives None and caches nothing, except that a
        server action without the op (an older goat_support module) is not
        asked again for AGENT_OP_MISSING_TTL.
        """
        if self._agent_partners.get(("agent_op_missing",)):
            return None
        key = ("agent", ticket_id, handler_user_id)
        cached = self._agent_partners.get(key)
        if cached is None:
            try:
                result = await self._odoo.call(
                    "ir.actions.server",
                    "run",
                    ids=[await self._post_action()],
                    context={
                        "active_model": "helpdesk.ticket",
                        "active_id": ticket_id,
                        "active_ids": [ticket_id],
                        "goat_op": "agent",
                    },
                )
                partner = (result or {}).get("goat_agent_partner_id")
            except OdooRejected as exc:
                if exc.message == "unknown operation":
                    logger.warning(
                        "support: the Odoo server action has no 'agent' op; "
                        "update the goat_support module in Odoo"
                    )
                    self._agent_partners.set(
                        ("agent_op_missing",), True, AGENT_OP_MISSING_TTL
                    )
                else:
                    logger.warning(
                        "support: reading the agent of %s failed: %r", ticket_id, exc
                    )
                return None
            except (SupportUnavailable, LookupError) as exc:
                logger.warning(
                    "support: reading the agent of %s failed: %r", ticket_id, exc
                )
                return None
            cached = int(partner) if partner else 0
            self._agent_partners.set(key, cached, AGENT_TTL)
        return cached or None

    async def _is_staff(
        self, partner_id: int, shares: dict[int, dict[str, Any]]
    ) -> bool:
        """Whether a partner is (or was) staff, from `shares` when it is there.

        For photos only: a failed lookup counts as "not staff" (no photo).
        """
        if partner_id in shares:
            return bool(shares[partner_id]["staff"])
        try:
            return partner_id in await self._staff([partner_id])
        except (OdooRejected, SupportUnavailable) as exc:
            logger.warning("support: reading who is staff failed: %r", exc)
            return False

    async def _people(
        self, partner_ids: Sequence[int], *, photos: bool = False
    ) -> dict[int, dict[str, Any]]:
        """Plain name and "staff" flag (current or former staff) per partner,
        plus `photo` (base64) for staff with a photo when asked for.

        From the server action's "people" op, which answers for partners taking
        part in a GOAT ticket and for GOAT contacts only; others are left out
        (their names fall back to the many2one's).
        """
        ids = sorted({p for p in partner_ids if p})
        people: dict[int, dict[str, Any]] = {}
        for start in range(0, len(ids), STAFF_BATCH):
            result = await self._run_op(
                "people",
                goat_partner_ids=ids[start : start + STAFF_BATCH],
                goat_with_photos=photos,
            )
            for person in result.get("goat_people") or []:
                people[int(person["id"])] = person
                self._staff_flags.set(
                    ("staff", int(person["id"])), bool(person["staff"]), STAFF_TTL
                )
        return people

    async def _staff_avatars(self, partner_ids: Sequence[int]) -> dict[int, str]:
        """Data-URI photos of staff partners; people without a real photo are left out.

        The "people" op sends `image_128` of staff only (avatar_128 would be a
        generated SVG for people without a photo). Both photos and "no photo"
        are cached for an hour. The photos are cosmetic: a failed read gives
        none and is not cached.
        """
        ids = sorted({p for p in partner_ids if p})
        missing = [p for p in ids if self._avatars.get(("avatar", p)) is None]
        if missing:
            try:
                people = await self._people(missing, photos=True)
            except (OdooRejected, SupportUnavailable) as exc:
                logger.warning("support: reading staff photos failed: %r", exc)
            else:
                found = {
                    pid: m.photo_data_uri(person.get("photo")) or ""
                    for pid, person in people.items()
                }
                for pid in missing:
                    self._avatars.set(("avatar", pid), found.get(pid, ""), AVATAR_TTL)
        return {
            p: uri for p in ids if (uri := self._avatars.get(("avatar", p))) and uri
        }

    # ---------------------------------------------------------------- contacts
    async def find_contacts_by_email(
        self, emails: Sequence[str], prefer_company_id: int | None = None
    ) -> dict[str, int]:
        """Customer contacts by email, from the server action's "find" op: never
        staff (current or former), companies or the bridge; per email the one in
        `prefer_company_id`, else the most recently written. Odoo marks them as
        GOAT contacts, which the bridge may then read and open tickets for.
        """
        normalized = sorted({e.strip().lower() for e in emails if e and e.strip()})
        found: dict[str, int] = {}
        for start in range(0, len(normalized), FIND_BATCH):
            result = await self._run_op(
                "find",
                goat_emails=normalized[start : start + FIND_BATCH],
                goat_prefer_company_id=prefer_company_id or 0,
            )
            for email, contact_id in (result.get("goat_contacts") or {}).items():
                found[str(email)] = int(contact_id)
        return found

    async def contacts_exist(self, contact_ids: Sequence[int]) -> set[int]:
        """The GOAT contacts among these that are active and not (former) staff."""
        ids = sorted({c for c in contact_ids if c})
        alive: set[int] = set()
        for start in range(0, len(ids), STAFF_BATCH):
            result = await self._run_op(
                "exist", goat_partner_ids=ids[start : start + STAFF_BATCH]
            )
            alive |= {int(i) for i in result.get("goat_contact_ids") or []}
        return alive

    async def create_contact(
        self,
        *,
        name: str,
        email: str,
        lang: Literal["en", "de"],
        company_id: int | None,
    ) -> int:
        # The bridge has no create/write right on res.partner; the server action
        # creates individuals only, under a customer company at most. It refuses
        # control characters and names over CONTACT_NAME_MAX.
        clean = " ".join(
            "".join(" " if unicodedata.category(c) == "Cc" else c for c in name).split()
        )
        try:
            result = await self._odoo.call(
                "ir.actions.server",
                "run",
                ids=[await self._post_action()],
                context={
                    "goat_op": "contact",
                    "goat_name": clean[:CONTACT_NAME_MAX].strip() or email,
                    "goat_email": email,
                    "goat_lang": _LANG[lang],
                    "goat_parent_id": company_id or 0,
                },
            )
        except OdooRejected as exc:
            if exc.message == "invalid parent company":
                raise SupportCompanyRefused(str(exc)) from exc
            if exc.message == "email belongs to staff":
                raise SupportStaffEmail(str(exc)) from exc
            raise
        return int(result["goat_contact_id"])

    # ----------------------------------------------------------------- tickets
    def _to_ticket(
        self,
        rec: dict[str, Any],
        stages: dict[int, Status],
        tags: dict[int, str],
        latest: dict[str, Any] | None,
        latest_is_agent: bool,
        partners: dict[int, dict[str, Any]],
    ) -> Ticket:
        created = _required_datetime(rec["create_date"])
        latest_at = m.parse_datetime(latest["date"]) if latest else None
        return Ticket(
            id=rec["id"],
            ref=rec["ticket_ref"],
            subject=rec["name"],
            status=stages.get(m.many2one_id(rec["stage_id"]) or 0, "in_progress"),
            category=m.category_from_tag_names(
                tags.get(t, "") for t in rec.get("tag_ids") or []
            ),
            impact=m.impact_from_priority(rec.get("priority")),
            customer_contact_id=m.many2one_id(rec.get("partner_id")),
            customer_name=m.partner_name(rec.get("partner_id"), partners),
            # The bridge cannot read res.users, but a user's many2one name is the
            # plain name of their partner (res.users has no company-prefixed
            # display_name); a deleted user is False and so has no agent.
            agent_name=m.many2one_name(rec.get("user_id")),
            org_id=rec.get("x_goat_organization_id") or None,
            request_id=rec.get("x_goat_request_id") or None,
            via="app" if rec.get("x_goat_request_id") else "email",
            created_at=created,
            # Latest customer-visible activity, not write_date: stamping the
            # organization or an internal edit must not move a ticket up.
            updated_at=max(latest_at, created) if latest_at else created,
            closed_at=m.parse_datetime(rec.get("close_date")),
            latest_message_id=latest["id"] if latest else None,
            latest_message_author=m.partner_name(latest["author_id"], partners)
            if latest
            else None,
            latest_message_is_agent=latest_is_agent,
            latest_message_at=latest_at,
        )

    async def list_tickets(self, query: TicketQuery) -> list[Ticket]:
        alternatives: list[list[Any]] = []
        if query.customer_ids:
            alternatives.append(["partner_id", "in", list(query.customer_ids)])
        if query.follower_contact_id:
            result = await self._run_op(
                "followed", goat_partner_id=query.follower_contact_id
            )
            followed = sorted({int(i) for i in result.get("goat_ticket_ids") or []})
            if followed:
                alternatives.append(["id", "in", followed])
        if query.org_id:
            alternatives.append(["x_goat_organization_id", "=", query.org_id])
        if not alternatives:
            return []
        stages = await self._stages()
        tags = await self._tags()
        domain: list[Any] = [["team_id", "=", self._team_id]]
        if query.open is not None:
            open_ids = sorted(
                i for i, s in stages.items() if s in ("new", "in_progress", "waiting")
            )
            domain.append(["stage_id", "in" if query.open else "not in", open_ids])
        if query.request_id:
            domain.append(["x_goat_request_id", "=", query.request_id])
        domain += ["|"] * (len(alternatives) - 1) + alternatives
        records = await self._odoo.call(
            "helpdesk.ticket",
            "search_read",
            domain=domain,
            fields=TICKET_FIELDS,
            order="write_date desc",
            limit=LIST_LIMIT,
        )
        if not records:
            return []
        messages = await self._odoo.call(
            "mail.message",
            "search_read",
            domain=[
                ["model", "=", "helpdesk.ticket"],
                ["res_id", "in", [r["id"] for r in records]],
                ["message_type", "in", ["comment", "email"]],
            ],
            fields=[
                "res_id",
                "author_id",
                "date",
                "message_type",
                "is_internal",
                "subtype_id",
            ],
            order="id desc",
        )
        public = await self._public_subtypes()
        latest: dict[int, dict[str, Any]] = {}
        for msg in messages:
            if m.is_customer_facing(msg, public):
                latest.setdefault(msg["res_id"], msg)
        shares = await self._people(
            [m.many2one_id(x["author_id"]) or 0 for x in latest.values()]
            + [m.many2one_id(r.get("partner_id")) or 0 for r in records]
        )
        return [
            self._to_ticket(
                rec,
                stages,
                tags,
                latest.get(rec["id"]),
                self._is_agent(latest.get(rec["id"]), shares),
                shares,
            )
            for rec in records
        ]

    @staticmethod
    def _is_agent(
        message: dict[str, Any] | None, shares: dict[int, dict[str, Any]]
    ) -> bool:
        if not message:
            return False
        author = shares.get(m.many2one_id(message["author_id"]) or 0)
        return author is not None and bool(author["staff"])

    async def get_ticket(self, ref: str) -> TicketDetail | None:
        records = await self._odoo.call(
            "helpdesk.ticket",
            "search_read",
            domain=[["team_id", "=", self._team_id], ["ticket_ref", "=", ref]],
            fields=[*TICKET_FIELDS, "description"],
            limit=1,
        )
        if not records:
            return None
        rec = records[0]
        raw = await self._odoo.call(
            "mail.message",
            "search_read",
            domain=[["model", "=", "helpdesk.ticket"], ["res_id", "=", rec["id"]]],
            fields=[
                "author_id",
                "date",
                "body",
                "message_type",
                "is_internal",
                "subtype_id",
                "attachment_ids",
            ],
            order="id asc",
        )
        public = await self._public_subtypes()
        visible = [msg for msg in raw if m.is_customer_facing(msg, public)]
        attachment_ids = sorted(
            {a for msg in visible for a in msg.get("attachment_ids") or []}
        )
        attachments: dict[int, AttachmentMeta] = {}
        if attachment_ids:
            for row in await self._odoo.call(
                "ir.attachment",
                "read",
                ids=attachment_ids,
                fields=["name", "mimetype", "file_size"],
            ):
                attachments[row["id"]] = AttachmentMeta(
                    row["id"],
                    m.file_name(row["name"]),
                    row["mimetype"] or "",
                    int(row["file_size"] or 0),
                )
        result = await self._run_op("followers", rec["id"])
        follower_ids = [int(i) for i in result.get("goat_partner_ids") or []]
        shares = await self._people(
            [m.many2one_id(msg["author_id"]) or 0 for msg in visible]
            + follower_ids
            + [m.many2one_id(rec.get("partner_id")) or 0]
        )
        messages = tuple(
            Message(
                id=msg["id"],
                author_contact_id=m.many2one_id(msg["author_id"]),
                author_name=m.partner_name(msg["author_id"], shares) or "",
                is_agent=self._is_agent(msg, shares),
                via="email" if msg["message_type"] == "email" else "app",
                created_at=_required_datetime(msg["date"]),
                body_html=m.strip_odoo_images(msg.get("body") or ""),
                attachments=tuple(
                    attachments[a]
                    for a in msg.get("attachment_ids") or []
                    if a in attachments
                ),
                author_known=m.many2one_id(msg["author_id"]) is not None,
            )
            for msg in visible
        )
        if rec.get("x_goat_request_id"):
            messages = self._with_description(rec, messages, shares)
        followers = tuple(
            Follower(pid, shares[pid]["name"], bool(shares[pid]["staff"]))
            for pid in follower_ids
            if pid in shares
        )
        latest = visible[-1] if visible else None
        ticket = self._to_ticket(
            rec,
            await self._stages(),
            await self._tags(),
            latest,
            self._is_agent(latest, shares),
            shares,
        )
        # Staff only: customers keep GOAT's own avatars, their photos never leave Odoo.
        staff = [
            m.many2one_id(msg["author_id"]) or 0
            for msg in visible
            if self._is_agent(msg, shares)
        ]
        handler = m.many2one_id(rec.get("user_id"))
        agent = await self._agent_partner(rec["id"], handler) if handler else None
        agent_photo = agent if agent and await self._is_staff(agent, shares) else 0
        return TicketDetail(
            ticket=ticket,
            messages=messages,
            followers=followers,
            avatars=await self._staff_avatars([*staff, agent_photo]),
            agent_contact_id=agent,
        )

    @staticmethod
    def _with_description(
        rec: dict[str, Any],
        messages: tuple[Message, ...],
        partners: dict[int, dict[str, Any]],
    ) -> tuple[Message, ...]:
        """GOAT tickets: the description opens the thread, as the customer's.

        Odoo keeps the text a GOAT user typed in the ticket's description, not
        in a message. The files of a new ticket follow as a message without
        text; that one is merged in (its id kept), so the first message shows
        text and files together. Read markers, the latest message and the
        visible attachments are unchanged by this.
        """
        body = m.strip_odoo_images(rec.get("description") or "")
        if not m.html_has_text(body):
            return messages
        created = _required_datetime(rec["create_date"])
        customer = m.many2one_id(rec.get("partner_id"))
        first = messages[0] if messages else None
        merge = (
            first is not None
            and not first.is_agent
            and first.author_contact_id == customer
            and bool(first.attachments)
            and not m.html_has_text(first.body_html)
            and first.created_at - created <= FILES_MESSAGE_WINDOW
        )
        opening = Message(
            id=first.id if merge and first else 0,
            author_contact_id=customer,
            author_name=m.partner_name(rec.get("partner_id"), partners) or "",
            is_agent=False,
            via="app",
            created_at=created,
            body_html=body,
            attachments=first.attachments if merge and first else (),
            author_known=customer is not None,
        )
        return (opening, *(messages[1:] if merge else messages))

    async def stamp_org(self, ticket_ids: Sequence[int], org_id: str) -> None:
        if ticket_ids:
            await self._odoo.call(
                "helpdesk.ticket",
                "write",
                ids=list(ticket_ids),
                vals={"x_goat_organization_id": org_id},
            )

    async def create_ticket(self, new: NewTicket) -> Ticket:
        tags = {name: tid for tid, name in (await self._tags()).items()}
        vals: dict[str, Any] = {
            "name": new.subject,
            "team_id": self._team_id,
            "partner_id": new.customer_contact_id,
            "description": new.description_html,
            "priority": m.PRIORITY_BY_IMPACT[new.impact] if new.impact else "0",
        }
        tag = m.TAG_BY_CATEGORY[new.category]
        if tag and tag in tags:
            vals["tag_ids"] = [[6, 0, [tags[tag]]]]
        vals |= {
            "x_goat_organization_id": new.org_id or False,
            "x_goat_user_id": new.user_id,
            "x_goat_request_id": new.request_id,
        }
        (ticket_id,) = await self._odoo.call(
            "helpdesk.ticket", "create", vals_list=[vals]
        )
        (rec,) = await self._odoo.call(
            "helpdesk.ticket", "read", ids=[ticket_id], fields=TICKET_FIELDS
        )
        try:
            partners = await self._people([new.customer_contact_id])
        except (OdooRejected, SupportUnavailable) as exc:
            # the ticket exists: the name falls back to the many2one's
            logger.warning("support: reading the customer's name failed: %r", exc)
            partners = {}
        return self._to_ticket(
            rec, await self._stages(), await self._tags(), None, False, partners
        )

    # ---------------------------------------------------------------- messages
    async def post_message(
        self,
        ticket_id: int,
        author_contact_id: int,
        text: str,
        files: Sequence[UploadedFile],
    ) -> PostResult:
        uploaded: list[int] = []
        failed: list[str] = []
        for f in files:
            try:
                (att_id,) = await self._odoo.call(
                    "ir.attachment",
                    "create",
                    vals_list=[
                        {
                            "name": f.name,
                            "res_model": "helpdesk.ticket",
                            "res_id": ticket_id,
                            "datas": base64.b64encode(f.data).decode(),
                            "mimetype": f.mimetype,
                        }
                    ],
                )
                uploaded.append(int(att_id))
            except (OdooRejected, SupportUnavailable) as exc:
                logger.warning("support: upload of a file failed: %r", exc)
                failed.append(f.name)
        if not text.strip() and not uploaded:
            return PostResult(message_id=None, failed_files=tuple(failed))
        result = await self._odoo.call(
            "ir.actions.server",
            "run",
            ids=[await self._post_action()],
            context={
                "active_model": "helpdesk.ticket",
                "active_id": ticket_id,
                "active_ids": [ticket_id],
                "goat_op": "post",
                "goat_author_id": author_contact_id,
                "goat_body_text": text,
                "goat_attachment_ids": uploaded,
            },
        )
        return PostResult(
            message_id=int(result["goat_message_id"]), failed_files=tuple(failed)
        )

    async def set_status(self, ticket_id: int, status: Status) -> None:
        await self._odoo.call(
            "helpdesk.ticket",
            "write",
            ids=[ticket_id],
            vals={"stage_id": await self._stage_id(status)},
        )

    async def add_followers(self, ticket_id: int, contact_ids: Sequence[int]) -> None:
        if contact_ids:
            await self._odoo.call(
                "helpdesk.ticket",
                "message_subscribe",
                ids=[ticket_id],
                partner_ids=list(contact_ids),
            )

    async def remove_followers(
        self, ticket_id: int, contact_ids: Sequence[int]
    ) -> None:
        if contact_ids:
            await self._odoo.call(
                "helpdesk.ticket",
                "message_unsubscribe",
                ids=[ticket_id],
                partner_ids=list(contact_ids),
            )

    async def rate(
        self, ticket_id: int, contact_id: int, rating: Rating, comment: str
    ) -> None:
        await self._odoo.call(
            "ir.actions.server",
            "run",
            ids=[await self._post_action()],
            context={
                "active_model": "helpdesk.ticket",
                "active_id": ticket_id,
                "active_ids": [ticket_id],
                "goat_op": "rate",
                "goat_author_id": contact_id,
                "goat_rating": RATING_VALUE[rating],
                "goat_feedback": comment,
            },
        )

    async def my_rating(self, ticket_id: int, contact_id: int) -> Rating | None:
        result = await self._run_op("my_rating", ticket_id, goat_partner_id=contact_id)
        if not result.get("goat_rating"):
            return None
        value = int(round(float(result["goat_rating"])))
        return next((r for r, v in RATING_VALUE.items() if v == value), None)

    async def download(self, attachment_id: int) -> tuple[AttachmentMeta, bytes]:
        (row,) = await self._odoo.call(
            "ir.attachment",
            "read",
            ids=[attachment_id],
            fields=["name", "mimetype", "file_size", "datas"],
        )
        meta = AttachmentMeta(
            row["id"],
            m.file_name(row["name"]),
            row["mimetype"] or "application/octet-stream",
            int(row["file_size"] or 0),
        )
        return meta, base64.b64decode(row["datas"] or b"")
