"""Pure mapping between Odoo helpdesk records and the neutral support types."""

import base64
import binascii
import re
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from typing import Any

from core.support.types import Category, Impact, Status

# English stage names (read with lang=en_US; Odoo translates them).
STATUS_BY_STAGE_NAME: dict[str, Status] = {
    "New": "new",
    "In Progress": "in_progress",
    "Waiting on Customer": "waiting",
    "Solved": "solved",
    "Cancelled": "cancelled",
}
STAGE_NAME_BY_STATUS: dict[Status, str] = {
    v: k for k, v in STATUS_BY_STAGE_NAME.items()
}

TAG_BY_CATEGORY: dict[Category, str | None] = {
    "bug": "bug",
    "how_to": "how-to",
    "data_issue": "data-question",
    "feature_request": "feature-request",
    "account_billing": "account-billing",
    "other": None,
}
_CATEGORY_BY_TAG = {tag: cat for cat, tag in TAG_BY_CATEGORY.items() if tag}

PRIORITY_BY_IMPACT: dict[Impact, str] = {
    "blocking": "2",
    "slowing": "1",
    "question": "0",
}
_IMPACT_BY_PRIORITY: dict[str, Impact] = {
    "3": "blocking",
    "2": "blocking",
    "1": "slowing",
    "0": "question",
}

_ODOO_IMG = re.compile(
    r"<img\b[^>]*\bsrc=\"[^\"]*(?:/web/image|/web/content|access_token=)[^\"]*\"[^>]*>",
    re.IGNORECASE,
)


def category_from_tag_names(names: Iterable[str]) -> Category:
    for name in names:
        if name in _CATEGORY_BY_TAG:
            return _CATEGORY_BY_TAG[name]
    return "other"


def impact_from_priority(priority: str | None) -> Impact | None:
    return _IMPACT_BY_PRIORITY.get(priority) if priority else None


def is_customer_facing(
    message: dict[str, Any], public_subtype_ids: frozenset[int]
) -> bool:
    """Discussion messages and emails only; never notes, tracking or auto mails.

    Allow-list on the subtype: log notes, stage notifications and auto mails are
    stored as comment / non-internal messages and differ only by their internal
    subtype, so a message counts only if its subtype is a known public one. A
    missing or unknown subtype is not customer facing (fails closed).
    """
    if message.get("message_type") not in ("comment", "email"):
        return False
    if message.get("is_internal"):
        return False
    subtype_id = many2one_id(message.get("subtype_id"))
    return subtype_id is not None and subtype_id in public_subtype_ids


# Direction controls (LRM/RLM, embeddings, overrides, isolates, ALM): a name
# like "invoice\u202efdp.exe" would show as "invoiceexe.pdf".
_BIDI = re.compile("[\u200e\u200f\u202a-\u202e\u2066-\u2069\u061c]")


def file_name(value: object) -> str:
    """An attachment's name for display and download, without direction controls."""
    return _BIDI.sub("", str(value or "")) or "file"


def strip_odoo_images(body: str) -> str:
    """Drop images whose URL carries an Odoo path or access token (v1 does not proxy them)."""
    return _ODOO_IMG.sub("", body or "")


_TAG = re.compile(r"<[^>]*>")


def html_has_text(body: str) -> bool:
    """False for "", "<p></p>", "<p><br></p>", "&nbsp;" and the like."""
    text = _TAG.sub("", body or "").replace("&nbsp;", " ").replace("\xa0", " ")
    return bool(text.strip())


def parse_datetime(value: str | bool | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


def many2one_id(value: object) -> int | None:
    return int(value[0]) if isinstance(value, list) and value else None


def many2one_name(value: object) -> str | None:
    return str(value[1]) if isinstance(value, list) and len(value) > 1 else None


def partner_name(
    value: object, partners: Mapping[int, Mapping[str, Any]]
) -> str | None:
    """A person's plain `name`, not Odoo's display name.

    Odoo prefixes an individual's display_name with their company ("Test, Majk
    Shkurti"), which is how a many2one shows the partner. The plain name comes
    from a partner read; the many2one's name is only the fallback when that read
    has no row or no name for the partner.
    """
    partner_id = many2one_id(value)
    row = partners.get(partner_id) if partner_id else None
    return (row.get("name") if row else None) or many2one_name(value)


MAX_PHOTO_BYTES = 64 * 1024


def photo_data_uri(encoded: object) -> str | None:
    """A data URI for a real JPEG/PNG/WebP photo, else None.

    The type comes from the decoded bytes, never from Odoo: an SVG placeholder,
    an empty field, a corrupt value or anything over MAX_PHOTO_BYTES is no photo.
    """
    if not encoded or not isinstance(encoded, str | bytes):
        return None
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return None
    if not data or len(data) > MAX_PHOTO_BYTES:
        return None
    if data.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        return None
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"
