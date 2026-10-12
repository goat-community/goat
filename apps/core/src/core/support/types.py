"""Neutral support types: no Odoo field names and no SQL live here."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID

Status = Literal["new", "in_progress", "waiting", "solved", "cancelled"]
OPEN_STATUSES: frozenset[Status] = frozenset({"new", "in_progress", "waiting"})
Category = Literal[
    "bug", "how_to", "data_issue", "feature_request", "account_billing", "other"
]
Impact = Literal["blocking", "slowing", "question"]
Rating = Literal["ko", "ok", "top"]
Via = Literal["app", "email"]


@dataclass(frozen=True)
class AttachmentMeta:
    id: int
    name: str
    mimetype: str
    size: int


@dataclass(frozen=True)
class Message:
    id: int
    author_contact_id: int | None
    author_name: str
    is_agent: bool
    via: Via
    created_at: datetime
    body_html: str
    attachments: tuple[AttachmentMeta, ...]
    # False when Odoo no longer has the author (a deleted partner): author_name is ""
    author_known: bool = True


@dataclass(frozen=True)
class Follower:
    contact_id: int
    name: str
    is_internal: bool


@dataclass(frozen=True)
class Ticket:
    id: int
    ref: str
    subject: str
    status: Status
    category: Category
    impact: Impact | None
    customer_contact_id: int | None
    customer_name: str | None
    agent_name: str | None
    org_id: str | None
    request_id: str | None
    via: Via
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    latest_message_id: int | None
    latest_message_author: str | None
    latest_message_is_agent: bool
    latest_message_at: datetime | None

    @property
    def is_open(self) -> bool:
        return self.status in OPEN_STATUSES


@dataclass(frozen=True)
class TicketDetail:
    ticket: Ticket
    messages: tuple[Message, ...]
    followers: tuple[Follower, ...]
    # Staff photos by contact id, as data URIs (only people who have a real one)
    avatars: dict[int, str] = field(default_factory=dict)
    # The assigned agent's own contact (key into `avatars`), known before they have
    # written anything; None while the ticket is unassigned or it could not be read
    agent_contact_id: int | None = None

    @property
    def visible_attachment_ids(self) -> frozenset[int]:
        return frozenset(a.id for m in self.messages for a in m.attachments)


@dataclass(frozen=True)
class UploadedFile:
    name: str
    mimetype: str
    data: bytes


@dataclass(frozen=True)
class NewTicket:
    subject: str
    description_html: str
    category: Category
    impact: Impact | None
    customer_contact_id: int
    org_id: str | None
    user_id: str
    request_id: str


@dataclass(frozen=True)
class PostResult:
    message_id: int | None
    failed_files: tuple[str, ...]


@dataclass(frozen=True)
class TicketQuery:
    """Which tickets to list: customer in `customer_ids`, OR followed by
    `follower_contact_id`, OR stamped with `org_id`. `open`: True = open
    stages only, False = closed only, None = both."""

    customer_ids: tuple[int, ...]
    follower_contact_id: int | None
    org_id: str | None
    open: bool | None
    request_id: str | None = None


@dataclass(frozen=True)
class SupportUser:
    id: UUID
    email: str
    name: str
    lang: Literal["en", "de"]
    org_id: UUID | None
    is_org_admin: bool
    contact_id: int | None


@dataclass(frozen=True)
class EmailProof:
    """What the request's token proves about the caller's email address.

    GOAT stores a changed profile email at once, before it is verified, so the
    stored email may only be used to find or create the user's support contact
    when the token vouches for it.
    """

    verified_email: str | None  # the token's email, only when email_verified
    trust_stored: bool = False  # AUTH off, default identity: the stored email counts

    def covers(self, stored_email: str) -> bool:
        if self.trust_stored:
            return True
        return (
            self.verified_email is not None
            and self.verified_email.strip().lower() == stored_email.strip().lower()
        )


@dataclass(frozen=True)
class Member:
    user_id: UUID
    email: str
    name: str
    contact_id: int | None
