"""The support bridge's Odoo client: core.odoo's client with the bridge's
allow-list, and Odoo's errors as support errors.

The bridge's Odoo rights are already narrow; ALLOWED_CALLS keeps a bug in
GOAT from turning into "any call on any model" as well. OdooUnavailable
becomes SupportUnavailable (503); a 4xx becomes this module's OdooRejected,
which is both a SupportRejected and a core.odoo OdooRejected.
"""

from typing import Any

from core import odoo
from core.core.config import settings
from core.support.errors import SupportRejected, SupportUnavailable

ALLOWED_CALLS: frozenset[tuple[str, str]] = frozenset(
    {
        ("res.users", "context_get"),
        ("res.users", "read"),
        ("helpdesk.ticket", "search_read"),
        ("helpdesk.ticket", "read"),
        ("helpdesk.ticket", "create"),
        ("helpdesk.ticket", "write"),
        ("helpdesk.ticket", "message_subscribe"),
        ("helpdesk.ticket", "message_unsubscribe"),
        ("helpdesk.stage", "search_read"),
        ("helpdesk.tag", "search_read"),
        ("mail.message", "search_read"),
        ("mail.message.subtype", "search_read"),
        ("ir.attachment", "create"),
        ("ir.attachment", "read"),
        ("ir.actions.server", "search"),
        ("ir.actions.server", "run"),
    }
)

# Uploads carry up to 10 MB (more as base64): the longer timeout, and a slow
# one does not count towards the circuit breaker.
UPLOAD_CALL = ("ir.attachment", "create")


class OdooRejected(SupportRejected, odoo.OdooRejected):
    """Odoo answered 4xx (access error, validation error, …)."""


class SupportOdooClient:
    def __init__(self, url: str, db: str, api_key: str, **options: Any) -> None:
        """`options` go to core.odoo.OdooClient (timeouts, concurrency, breaker)."""
        self._odoo = odoo.OdooClient(
            url,
            db,
            api_key,
            allowed_calls=ALLOWED_CALLS,
            upload_calls=(UPLOAD_CALL,),
            ca_bundle=settings.GOAT_CA_BUNDLE,
            **options,
        )

    async def call(self, model: str, method: str, **kwargs: Any) -> Any:
        try:
            return await self._odoo.call(model, method, **kwargs)
        except odoo.OdooUnavailable as exc:
            raise SupportUnavailable(str(exc)) from exc
        except odoo.OdooRejected as exc:
            raise OdooRejected(exc.status, exc.name, exc.message) from exc

    async def close(self) -> None:
        await self._odoo.close()
