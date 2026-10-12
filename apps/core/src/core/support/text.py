"""Plain text from GOAT users → safe HTML for Odoo's HTML fields."""

import html
import re

_WS = re.compile(r"\s+")
SUBJECT_MAX = 200


def plain_text_to_html(text: str) -> str:
    """Escape everything, then blank lines → paragraphs and newlines → <br>.

    The same rule as the Odoo server action, so a description and a reply
    look alike in Odoo.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip("\n") for p in re.split(r"\n\s*\n", normalized)]
    return "".join(
        "<p>" + html.escape(p).replace("\n", "<br>") + "</p>"
        for p in paragraphs
        if p.strip()
    )


def clean_subject(text: str) -> str:
    """One line of plain text, at most 200 characters (Odoo char field)."""
    return _WS.sub(" ", text).strip()[:SUBJECT_MAX]


def technical_block(details: dict[str, str]) -> str:
    """The "Technical details" list appended to a ticket's description."""
    if not details:
        return ""
    items = "".join(
        f"<li>{html.escape(key)}: {html.escape(value)}</li>"
        for key, value in details.items()
    )
    return f"<p><strong>Technical details</strong></p><ul>{items}</ul>"
