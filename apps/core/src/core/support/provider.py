"""What the support service needs from a ticket system (Odoo today)."""

from collections.abc import Sequence
from typing import Literal, Protocol

from core.support.types import (
    AttachmentMeta,
    NewTicket,
    PostResult,
    Rating,
    Status,
    Ticket,
    TicketDetail,
    TicketQuery,
    UploadedFile,
)


class SupportProvider(Protocol):
    async def bridge_contact_id(self) -> int | None:
        """The ticket system's own contact for the bridge user, if known."""
        ...

    async def find_contacts_by_email(
        self, emails: Sequence[str], prefer_company_id: int | None = None
    ) -> dict[str, int]: ...

    async def contacts_exist(self, contact_ids: Sequence[int]) -> set[int]:
        """Which of these contacts still exist and are active (not deleted,
        archived or merged away)."""
        ...

    async def create_contact(
        self,
        *,
        name: str,
        email: str,
        lang: Literal["en", "de"],
        company_id: int | None,
    ) -> int: ...

    async def list_tickets(self, query: TicketQuery) -> list[Ticket]: ...

    async def get_ticket(self, ref: str) -> TicketDetail | None: ...

    async def stamp_org(self, ticket_ids: Sequence[int], org_id: str) -> None: ...

    async def create_ticket(self, new: NewTicket) -> Ticket: ...

    async def post_message(
        self,
        ticket_id: int,
        author_contact_id: int,
        text: str,
        files: Sequence[UploadedFile],
    ) -> PostResult: ...

    async def set_status(self, ticket_id: int, status: Status) -> None: ...

    async def add_followers(
        self, ticket_id: int, contact_ids: Sequence[int]
    ) -> None: ...

    async def remove_followers(
        self, ticket_id: int, contact_ids: Sequence[int]
    ) -> None: ...

    async def rate(
        self, ticket_id: int, contact_id: int, rating: Rating, comment: str
    ) -> None: ...

    async def my_rating(self, ticket_id: int, contact_id: int) -> Rating | None:
        """The rating this contact gave the ticket, if any."""
        ...

    async def download(self, attachment_id: int) -> tuple[AttachmentMeta, bytes]: ...
