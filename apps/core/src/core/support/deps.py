"""FastAPI dependencies for the support API."""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.core.config import settings
from core.deps.keycloak import get_keycloak_user
from core.endpoints.deps import get_current_token_claims, get_db
from core.support.odoo_client import SupportOdooClient
from core.support.odoo_provider import OdooSupportProvider
from core.support.provider import SupportProvider
from core.support.service import SupportService
from core.support.store import SqlSupportStore
from core.support.throttle import RateLimiter, TTLCache
from core.support.types import EmailProof

# One per process: the provider caches stages/tags/action id, the client keeps
# its connection pool and concurrency cap, cache and limits span requests.
_client: SupportOdooClient | None = None
_provider: OdooSupportProvider | None = None
_cache = TTLCache()
# New tickets: a burst guard; the limit users meet is MAX_OPEN_TICKETS (service).
_ticket_limiter = RateLimiter(limit=20, window=3600)
_reply_limiter = RateLimiter(limit=60, window=3600)
# Resolve / reopen: each stage change emails the ticket's followers.
_status_limiter = RateLimiter(limit=20, window=3600)
# Ticket reads that reach Odoo (detail, actions, downloads, request_id lookups).
_read_limiter = RateLimiter(limit=120, window=300)


def require_support_enabled() -> None:
    """404 while the support settings are unset (self-hosted, or not configured)."""
    if not settings.support_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


async def get_support_provider() -> SupportProvider:
    return _odoo_provider()


def _odoo_provider() -> OdooSupportProvider:
    # Only called on the event loop (from `async def`s), never in the
    # threadpool, so two requests cannot race to build two providers.
    global _client, _provider
    if _provider is None:
        _client = client = SupportOdooClient(
            settings.ODOO_URL or "",
            settings.ODOO_DB or "",
            settings.ODOO_SUPPORT_API_KEY or "",
        )
        _provider = OdooSupportProvider(
            client,
            team_id=settings.ODOO_SUPPORT_TEAM_ID or 0,
            post_action_name=settings.ODOO_SUPPORT_POST_ACTION,
        )
    return _provider


def get_email_proof(request: Request) -> EmailProof:
    """What the token says about the caller's email (see EmailProof).

    With AUTH off and no token the caller is the default identity, whose
    stored email counts as verified (local development only).
    """
    if not settings.AUTH and not request.headers.get("Authorization"):
        return EmailProof(verified_email=None, trust_stored=True)
    claims = get_current_token_claims(request)
    email = claims.get("email")
    if claims.get("email_verified") is True and isinstance(email, str) and email:
        return EmailProof(verified_email=email.strip().lower())
    return EmailProof(verified_email=None)


async def get_support_service(
    async_session: AsyncSession = Depends(get_db),
    provider: SupportProvider = Depends(get_support_provider),
    email_proof: EmailProof = Depends(get_email_proof),
) -> SupportService:
    return SupportService(
        provider,
        SqlSupportStore(async_session),
        cache=_cache,
        ticket_limiter=_ticket_limiter,
        reply_limiter=_reply_limiter,
        email_proof=email_proof,
        keycloak_user=get_keycloak_user,
        status_limiter=_status_limiter,
        read_limiter=_read_limiter,
    )


async def close_support_provider() -> None:
    """Shutdown hook: close the Odoo HTTP session and forget the provider."""
    global _client, _provider
    client, _client, _provider = _client, None, None
    if client is not None:
        await client.close()
