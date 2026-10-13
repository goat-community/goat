"""Authentication utilities for GOAT services.

Provides shared JWT token validation and Keycloak authentication
used across core, geoapi, and processes services.
"""

import logging
import threading
import time
from collections.abc import Iterable
from typing import Annotated, Any, Protocol

import requests
from jose import JOSEError, jwt
from jose.exceptions import JWTClaimsError
from pydantic import BeforeValidator

logger = logging.getLogger(__name__)


def _unset_auth_is_on(value: object) -> object:
    """Map an unset or empty AUTH value to True; leave the rest to pydantic."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return True
    return value


AuthFlag = Annotated[bool, BeforeValidator(_unset_auth_is_on)]
"""The repo-wide ``AUTH`` flag as a settings field type.

Parsed with pydantic's bool rules (``true/1/yes/on/t/y`` on,
``false/0/no/off/f/n`` off, any case); unset or empty keeps auth on. The web
reads the same variable with the same table (``isAuthDisabled`` in
``apps/web/lib/utils/auth-flag.ts``).
"""


def parse_allowed_clients(value: str | Iterable[str] | None) -> frozenset[str]:
    """Parse ``AUTH_ALLOWED_CLIENTS`` into a set of Keycloak client IDs.

    Accepts a comma-separated string (``"goat,goat-scripts"``) or an iterable
    of IDs. Blank entries are dropped, so ``None``, ``""`` and ``" , "`` all
    mean "no restriction".
    """
    if value is None:
        return frozenset()
    parts = value.split(",") if isinstance(value, str) else value
    return frozenset(part.strip() for part in parts if part and part.strip())


def require_keycloak_url(auth: bool, keycloak_server_url: str | None) -> None:
    """Refuse a configuration that enables auth without a Keycloak server.

    Raises:
        ValueError: If ``auth`` is on and ``keycloak_server_url`` is empty.
    """
    if auth and not keycloak_server_url:
        raise ValueError("AUTH is on but KEYCLOAK_SERVER_URL is not set")


def require_own_client_allowed(
    auth: bool,
    allowed_clients: str | Iterable[str] | None,
    own_client: str | None,
) -> None:
    """Refuse an allow-list that leaves out GOAT's own Keycloak client.

    The web app signs users in with ``own_client`` (``KEYCLOAK_CLIENT_ID``),
    so a non-empty ``AUTH_ALLOWED_CLIENTS`` without it refuses every user.

    Raises:
        ValueError: If ``auth`` is on, ``allowed_clients`` is not empty and
            ``own_client`` is set but not in it.
    """
    allowed = parse_allowed_clients(allowed_clients)
    if auth and allowed and own_client and own_client.strip() not in allowed:
        raise ValueError(
            f"AUTH_ALLOWED_CLIENTS ({', '.join(sorted(allowed))}) does not include "
            f"KEYCLOAK_CLIENT_ID ({own_client.strip()}): GOAT's own client must be "
            "on the list, or every user is refused"
        )


class AuthSettings(Protocol):
    """Protocol for settings objects that configure authentication."""

    AUTH: bool
    KEYCLOAK_SERVER_URL: str
    REALM_NAME: str
    # AUTH_ALLOWED_CLIENTS is optional: create_keycloak_auth reads it with
    # getattr, and a settings object without it accepts every client.


class KeycloakAuth:
    """Keycloak authentication handler.

    Handles JWT token validation using Keycloak's public key.
    Supports both production (signature verification) and development
    (signature bypass) modes.

    With ``allowed_clients`` set, a verified token is accepted only if its
    ``azp`` claim (the client Keycloak issued it to) is one of them. In a
    realm shared with other applications, this keeps tokens those
    applications obtained from working on GOAT's APIs. Keycloak puts the
    requesting client in ``azp`` on every access token, while ``aud`` holds
    only what audience mappers and client roles add (by default just
    ``account``), so the client is checked rather than the audience. Without
    signature verification (``AUTH=False``) the check is skipped.

    Example:
        from goatlib.auth import KeycloakAuth

        auth = KeycloakAuth(
            keycloak_url="https://auth.example.com",
            realm="myrealm",
            verify_signature=True,
        )
        user_data = auth.decode_token(token)
    """

    def __init__(
        self: "KeycloakAuth",
        keycloak_url: str,
        realm: str,
        verify_signature: bool = True,
        timeout: int = 10,
        retry_interval: float = 10.0,
        allowed_clients: str | Iterable[str] | None = None,
    ) -> None:
        """Initialize Keycloak authentication.

        The realm public key is fetched on the first ``decode_token`` call, not
        here, so a service can start while Keycloak is still unreachable.

        Args:
            keycloak_url: Base URL of Keycloak server
            realm: Keycloak realm name
            verify_signature: Whether to verify JWT signatures
            timeout: HTTP request timeout in seconds
            retry_interval: Minimum seconds between two key fetch attempts
                while the key is missing
            allowed_clients: Client IDs whose tokens are accepted, as a
                comma-separated string or an iterable (see
                ``parse_allowed_clients``); empty accepts any client
        """
        self._verify_signature = verify_signature
        self._allowed_clients = parse_allowed_clients(allowed_clients)
        self._refused_clients: set[str] = set()
        self._issuer_url = f"{keycloak_url}/realms/{realm}"
        self._public_key: str | None = None
        self._timeout = timeout
        self._retry_interval = retry_interval
        self._last_attempt: float | None = None
        self._lock = threading.Lock()

    def _fetch_public_key(self: "KeycloakAuth") -> None:
        """Fetch Keycloak public key for JWT verification."""
        try:
            response = requests.get(self._issuer_url, timeout=self._timeout)
            response.raise_for_status()
            raw_key = response.json().get("public_key")
            if raw_key:
                self._public_key = (
                    f"-----BEGIN PUBLIC KEY-----\n{raw_key}\n-----END PUBLIC KEY-----"
                )
                logger.info("Successfully loaded Keycloak public key")
            else:
                logger.warning("No public key in Keycloak response")
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch Keycloak public key: {e}")
        except Exception as e:
            logger.warning(f"Error processing Keycloak response: {e}")

    def _ensure_public_key(self: "KeycloakAuth") -> str | None:
        """Return the cached public key, fetching it if it is missing.

        While the key is missing, at most one fetch is attempted per
        ``retry_interval`` seconds; calls in between return ``None``.
        """
        if self._public_key is not None:
            return self._public_key
        with self._lock:
            if self._public_key is not None:
                return self._public_key
            now = time.monotonic()
            if (
                self._last_attempt is None
                or now - self._last_attempt >= self._retry_interval
            ):
                self._last_attempt = now
                self._fetch_public_key()
        return self._public_key

    def decode_token(self: "KeycloakAuth", token: str) -> dict[str, Any]:
        """Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload as dict

        Raises:
            JOSEError: If token is invalid, verification fails, the
                Keycloak public key cannot be fetched, or the token was
                issued to a client outside ``allowed_clients``
        """
        if self._verify_signature and self._ensure_public_key() is None:
            raise JOSEError("Keycloak public key unavailable")
        claims = jwt.decode(
            token,
            key=self._public_key,
            options={
                "verify_signature": self._verify_signature,
                "verify_aud": False,
                "verify_iss": self._issuer_url if self._verify_signature else False,
            },
        )
        if self._verify_signature:
            self._check_client(claims)
        return claims

    def _check_client(self: "KeycloakAuth", claims: dict[str, Any]) -> None:
        """Reject a token whose ``azp`` is not an allowed client.

        The caller gets the same kind of message as for any other invalid
        claim; the client that was refused is logged here instead, as a
        warning the first time per client and at debug level after that
        (each request can decode its token more than once).

        Raises:
            JWTClaimsError: If ``allowed_clients`` is set and the token's
                ``azp`` is missing or not in it
        """
        if not self._allowed_clients:
            return
        client = claims.get("azp")
        if isinstance(client, str) and client in self._allowed_clients:
            return
        client_label = str(client) if client else "(no azp claim)"
        if client_label in self._refused_clients:
            log = logger.debug
        else:
            self._refused_clients.add(client_label)
            log = logger.warning
        log(
            "Refused a token of Keycloak client %s: not in AUTH_ALLOWED_CLIENTS",
            client_label,
        )
        raise JWTClaimsError("Invalid authorized party")

    @property
    def issuer_url(self: "KeycloakAuth") -> str:
        """Get the Keycloak issuer URL."""
        return self._issuer_url

    @property
    def public_key(self: "KeycloakAuth") -> str | None:
        """Get the Keycloak public key (PEM format)."""
        return self._public_key

    @property
    def verify_signature(self: "KeycloakAuth") -> bool:
        """Check if signature verification is enabled."""
        return self._verify_signature

    @property
    def allowed_clients(self: "KeycloakAuth") -> frozenset[str]:
        """Client IDs whose tokens are accepted; empty accepts any client."""
        return self._allowed_clients


def create_keycloak_auth(settings: AuthSettings) -> KeycloakAuth:
    """Create a KeycloakAuth instance from settings.

    Convenience function that extracts settings from a Pydantic settings object.

    Args:
        settings: Settings object with AUTH, KEYCLOAK_SERVER_URL, REALM_NAME
            and optionally AUTH_ALLOWED_CLIENTS (missing accepts every client)

    Returns:
        Configured KeycloakAuth instance
    """
    return KeycloakAuth(
        keycloak_url=settings.KEYCLOAK_SERVER_URL,
        realm=settings.REALM_NAME,
        verify_signature=settings.AUTH,
        allowed_clients=getattr(settings, "AUTH_ALLOWED_CLIENTS", None),
    )


# Re-export JOSEError for convenience
__all__ = [
    "AuthFlag",
    "KeycloakAuth",
    "AuthSettings",
    "create_keycloak_auth",
    "parse_allowed_clients",
    "require_keycloak_url",
    "require_own_client_allowed",
    "JOSEError",
]
