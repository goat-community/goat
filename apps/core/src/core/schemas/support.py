from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from core.support.types import Category, Impact, Rating, Status, Via


class AttachmentOut(BaseModel):
    id: int
    name: str
    mimetype: str
    size: int


class MessageOut(BaseModel):
    id: int
    # Only set for GOAT team members: the key into TicketDetailOut.avatars
    author_contact_id: int | None = None
    author_name: str
    # False when the sender's contact no longer exists: author_name is then ""
    author_known: bool = True
    is_agent: bool
    is_me: bool
    via: Via
    created_at: datetime
    body_html: str
    attachments: list[AttachmentOut]


class FollowerOut(BaseModel):
    contact_id: int
    name: str
    is_me: bool


class TicketOut(BaseModel):
    ref: str
    subject: str
    status: Status
    category: Category
    impact: Impact | None
    customer_name: str | None
    # The customer's contact: the people panel leaves them out of "add colleague".
    customer_contact_id: int | None
    is_mine: bool
    agent_name: str | None
    via: Via
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    latest_message_author: str | None
    latest_message_is_agent: bool
    latest_message_at: datetime | None
    unread: bool
    needs_my_reply: bool


class TicketDetailOut(BaseModel):
    ticket: TicketOut
    messages: list[MessageOut]
    followers: list[FollowerOut]
    on_ticket: bool
    can_manage_people: bool
    # GOAT team photos by contact id, data URIs; people without a photo are absent
    avatars: dict[int, str] = Field(default_factory=dict)
    # The assigned agent's contact id (key into avatars), also before they have written
    agent_contact_id: int | None = None
    # What the requesting contact rated this ticket, once solved; None = not rated
    my_rating: Rating | None = None


class SummaryOut(BaseModel):
    needs_reply: int
    unread: int


class WriteResultOut(BaseModel):
    ref: str
    message_id: int | None
    failed_files: list[str]


class FollowersUpdate(BaseModel):
    add_user_ids: list[UUID] = Field(default_factory=list, max_length=20)
    remove_contact_ids: list[int] = Field(default_factory=list, max_length=20)


class RatingIn(BaseModel):
    rating: Rating
    comment: str = Field("", max_length=2000)


class ColleagueOut(BaseModel):
    user_id: UUID
    name: str
    email: str
    # Matches a follower (FollowerOut.contact_id); None until they get a contact.
    contact_id: int | None
