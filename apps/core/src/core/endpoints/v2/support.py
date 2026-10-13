"""Support tickets (Odoo Helpdesk). SaaS only: 404 while unconfigured.

Visibility is enforced by SupportService on every call; the authz resource
entry `support` only requires an authenticated user.
"""

import json
import logging
from collections.abc import Awaitable
from typing import Literal, TypeVar
from urllib.parse import quote
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Response,
    UploadFile,
    status,
)

from core.deps.auth import auth_z
from core.endpoints.deps import get_user_id
from core.schemas.support import (
    AttachmentOut,
    ColleagueOut,
    FollowerOut,
    FollowersUpdate,
    MessageOut,
    RatingIn,
    SummaryOut,
    TicketDetailOut,
    TicketOut,
    WriteResultOut,
)
from core.support.deps import get_support_service, require_support_enabled
from core.support.errors import (
    SupportEmailNotVerified,
    SupportForbidden,
    SupportInvalid,
    SupportRateLimited,
    SupportUnavailable,
    TicketNotFound,
)
from core.support.odoo_client import OdooRejected
from core.support.service import (
    NewTicketInput,
    SupportService,
    TicketListItem,
    TicketView,
    WriteResult,
)
from core.support.types import Category, Impact, UploadedFile

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_support_enabled), Depends(auth_z)])

MAX_FILES = 10
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 50 * 1024 * 1024
MAX_COLLEAGUES = 20
REF = Path(..., pattern=r"^[0-9]{1,10}$")
T = TypeVar("T")


async def _call(awaitable: Awaitable[T]) -> T:
    try:
        return await awaitable
    except TicketNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not Found") from None
    except SupportForbidden:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden") from None
    except SupportEmailNotVerified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "email_not_verified") from None
    except SupportRateLimited:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "rate_limited") from None
    except SupportInvalid as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, exc.message
        ) from None
    except SupportUnavailable:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "support_unavailable"
        ) from None
    except (OdooRejected, LookupError) as exc:
        # Odoo refused the bridge user (access/validation error) or a stage,
        # tag or server action we rely on is missing: a setup problem on our
        # side, not something the caller can fix.
        logger.warning("support backend rejected the request: %r", exc)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "support_unavailable"
        ) from None


async def _read_files(files: list[UploadFile]) -> tuple[UploadedFile, ...]:
    if len(files) > MAX_FILES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "too_many_files")
    out, total = [], 0
    for f in files:
        data = await f.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "file_too_large")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "files_too_large")
        out.append(
            UploadedFile(
                f.filename or "file", f.content_type or "application/octet-stream", data
            )
        )
    return tuple(out)


def _ascii_name(name: str) -> str:
    """Header-safe fallback name for clients that ignore `filename*`."""
    safe = "".join(c if c.isascii() and c.isprintable() else "_" for c in name)
    return safe.replace("\\", "_").replace('"', "_") or "file"


def _ticket_out(item: TicketListItem, me: int | None) -> TicketOut:
    t = item.ticket
    return TicketOut(
        ref=t.ref,
        subject=t.subject,
        status=t.status,
        category=t.category,
        impact=t.impact,
        customer_name=t.customer_name,
        customer_contact_id=t.customer_contact_id,
        is_mine=me is not None and t.customer_contact_id == me,
        agent_name=t.agent_name,
        via=t.via,
        created_at=t.created_at,
        updated_at=t.updated_at,
        closed_at=t.closed_at,
        latest_message_author=t.latest_message_author,
        latest_message_is_agent=t.latest_message_is_agent,
        latest_message_at=t.latest_message_at,
        unread=item.unread,
        needs_my_reply=item.needs_my_reply,
    )


def _detail_out(view: TicketView) -> TicketDetailOut:
    d, me = view.detail, view.me_contact_id
    item = TicketListItem(
        d.ticket,
        unread=False,
        needs_my_reply=d.ticket.status == "waiting" and view.on_ticket,
    )
    return TicketDetailOut(
        ticket=_ticket_out(item, me),
        messages=[
            MessageOut(
                id=m.id,
                author_contact_id=m.author_contact_id if m.is_agent else None,
                author_name=m.author_name,
                author_known=m.author_known,
                is_agent=m.is_agent,
                is_me=m.author_known and me is not None and m.author_contact_id == me,
                via=m.via,
                created_at=m.created_at,
                body_html=m.body_html,
                attachments=[
                    AttachmentOut(
                        id=a.id, name=a.name, mimetype=a.mimetype, size=a.size
                    )
                    for a in m.attachments
                ],
            )
            for m in d.messages
        ],
        followers=[
            FollowerOut(contact_id=f.contact_id, name=f.name, is_me=f.contact_id == me)
            for f in d.followers
        ],
        on_ticket=view.on_ticket,
        can_manage_people=view.can_manage_people,
        avatars=d.avatars,
        agent_contact_id=d.agent_contact_id,
        my_rating=view.my_rating,
    )


def _write_out(result: WriteResult) -> WriteResultOut:
    return WriteResultOut(
        ref=result.ref,
        message_id=result.message_id,
        failed_files=list(result.failed_files),
    )


@router.get("/summary", response_model=SummaryOut)
async def get_summary(
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> SummaryOut:
    s = await _call(service.summary(user_id))
    return SummaryOut(needs_reply=s.needs_reply, unread=s.unread)


@router.get("/tickets", response_model=list[TicketOut])
async def list_tickets(
    scope: Literal["mine", "org"] = Query("mine"),
    state: Literal["open", "closed"] = Query("open"),
    q: str = Query("", max_length=200),
    request_id: str | None = Query(None, max_length=64),
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> list[TicketOut]:
    items = await _call(service.list(user_id, scope, state, q, request_id))
    me = await _call(service.my_contact_id(user_id))
    return [_ticket_out(i, me) for i in items]


@router.get("/tickets/{ref}", response_model=TicketDetailOut)
async def get_ticket(
    ref: str = REF,
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> TicketDetailOut:
    return _detail_out(await _call(service.get(user_id, ref)))


@router.post(
    "/tickets", response_model=WriteResultOut, status_code=status.HTTP_201_CREATED
)
async def create_ticket(
    subject: str = Form(..., min_length=3, max_length=200),
    description: str = Form(..., min_length=1, max_length=20000),
    category: Category = Form(...),
    impact: Impact | None = Form(None),
    request_id: str = Form(..., min_length=8, max_length=64),
    colleague_ids: list[UUID] = Form(default=[], max_length=MAX_COLLEAGUES),
    technical: str = Form("{}", max_length=4000),
    files: list[UploadFile] = File(default=[]),
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> WriteResultOut:
    try:
        details = {str(k): str(v) for k, v in json.loads(technical).items()}
    except (ValueError, RecursionError, AttributeError, TypeError):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "invalid_technical"
        ) from None
    data = NewTicketInput(
        subject=subject,
        description=description,
        category=category,
        impact=None if category == "feature_request" else impact,
        request_id=request_id,
        colleague_ids=tuple(colleague_ids),
        technical=details,
        files=await _read_files(files),
    )
    return _write_out(await _call(service.create(user_id, data)))


@router.post(
    "/tickets/{ref}/messages",
    response_model=WriteResultOut,
    status_code=status.HTTP_201_CREATED,
)
async def reply(
    ref: str = REF,
    text: str = Form("", max_length=50000),
    files: list[UploadFile] = File(default=[]),
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> WriteResultOut:
    return _write_out(
        await _call(service.reply(user_id, ref, text, await _read_files(files)))
    )


@router.post("/tickets/{ref}/resolve", status_code=status.HTTP_204_NO_CONTENT)
async def resolve(
    ref: str = REF,
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> None:
    await _call(service.resolve(user_id, ref))


@router.post("/tickets/{ref}/reopen", status_code=status.HTTP_204_NO_CONTENT)
async def reopen(
    ref: str = REF,
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> None:
    await _call(service.reopen(user_id, ref))


@router.put("/tickets/{ref}/followers", status_code=status.HTTP_204_NO_CONTENT)
async def update_followers(
    body: FollowersUpdate,
    ref: str = REF,
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> None:
    await _call(
        service.update_followers(
            user_id, ref, tuple(body.add_user_ids), tuple(body.remove_contact_ids)
        )
    )


@router.post("/tickets/{ref}/rating", status_code=status.HTTP_204_NO_CONTENT)
async def rate(
    body: RatingIn,
    ref: str = REF,
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> None:
    await _call(service.rate(user_id, ref, body.rating, body.comment))


@router.get("/tickets/{ref}/attachments/{attachment_id}")
async def download(
    ref: str = REF,
    attachment_id: int = Path(..., ge=1),
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> Response:
    meta, data = await _call(service.download(user_id, ref, attachment_id))
    return Response(
        content=data,
        media_type=meta.mimetype,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_ascii_name(meta.name)}"; '
                f"filename*=UTF-8''{quote(meta.name, safe='')}"
            ),
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/colleagues", response_model=list[ColleagueOut])
async def colleagues(
    user_id: UUID = Depends(get_user_id),
    service: SupportService = Depends(get_support_service),
) -> list[ColleagueOut]:
    return [
        ColleagueOut(
            user_id=m.user_id, name=m.name, email=m.email, contact_id=m.contact_id
        )
        for m in await _call(service.colleagues(user_id))
    ]
