"""Domain errors; the endpoint layer maps each to one HTTP status."""


class SupportError(Exception):
    """Base class."""


class SupportUnavailable(SupportError):  # noqa: N818
    """Odoo timed out, refused the connection or answered 5xx (→ 503)."""


class TicketNotFound(SupportError):  # noqa: N818
    """Unknown ticket, or one the caller may not see (→ 404)."""


class SupportForbidden(SupportError):  # noqa: N818
    """The caller may see the ticket but not do this (→ 403)."""


class SupportEmailNotVerified(SupportError):  # noqa: N818
    """Linking the user to a support contact needs a verified email (→ 403)."""


class SupportRejected(SupportError):  # noqa: N818
    """The ticket system answered but refused the call (access/validation error)."""


class SupportCompanyRefused(SupportRejected):
    """The ticket system refused the company a new contact was to belong to."""


class SupportStaffEmail(SupportRejected):
    """The ticket system refused a contact with a staff member's email (current or
    former staff): staff use the ticket system itself, not GOAT's support pages."""


class SupportRateLimited(SupportError):  # noqa: N818
    """Too many tickets or replies in the last hour (→ 429)."""


class SupportInvalid(SupportError):  # noqa: N818
    """The request is well-formed but not allowed in this state (→ 422)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
