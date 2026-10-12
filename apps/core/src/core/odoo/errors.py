"""What can go wrong when GOAT calls Odoo."""


class OdooError(Exception):
    """Base class."""


class OdooUnavailable(OdooError):  # noqa: N818
    """Odoo timed out, refused the connection, answered 5xx or a redirect, or
    the circuit breaker is open."""

    def __init__(self, message: str = "", *, counts_for_breaker: bool = True) -> None:
        super().__init__(message)
        # False when the failure says more about the call than about Odoo
        # (no free connection slot, a slow upload).
        self.counts_for_breaker = counts_for_breaker


class OdooRejected(OdooError):  # noqa: N818
    """Odoo answered 4xx (access error, validation error, …)."""

    def __init__(self, status: int, name: str, message: str) -> None:
        super().__init__(f"{status} {name}: {message}")
        self.status = status
        self.name = name
        self.message = message
