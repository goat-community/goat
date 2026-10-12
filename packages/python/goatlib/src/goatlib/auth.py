"""Authentication utilities for GOAT services.

Provides shared JWT token validation and Keycloak authentication
used across core, geoapi, and processes services.
"""

import logging
import threading
import time
from typing import Annotated, Any, Protocol

import requests
from jose import JOSEError, jwt
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


def require_keycloak_url(auth: bool, keycloak_server_url: str | None) -> None:
    """Refuse a configuration that enables auth without a Keycloak server.

    Raises:
        ValueError: If ``auth`` is on and ``keycloak_server_url`` is empty.
    """
    if auth and not keycloak_server_url:
        raise ValueError("AUTH is on but KEYCLOAK_SERVER_URL is not set")


class AuthSettings(Protocol):
    """Protocol for settings objects that configure authentication."""

    AUTH: bool
    KEYCLOAK_SERVER_URL: str
    REALM_NAME: str


class KeycloakAuth:
    """Keycloak authentication handler.

    Handles JWT token validation using Keycloak's public key.
    Supports both production (signature verification) and development
    (signature bypass) modes.

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
        """
        self._verify_signature = verify_signature
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
            JOSEError: If token is invalid, verification fails, or the
                Keycloak public key cannot be fetched
        """
        if self._verify_signature and self._ensure_public_key() is None:
            raise JOSEError("Keycloak public key unavailable")
        return jwt.decode(
            token,
            key=self._public_key,
            options={
                "verify_signature": self._verify_signature,
                "verify_aud": False,
                "verify_iss": self._issuer_url if self._verify_signature else False,
            },
        )

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


def create_keycloak_auth(settings: AuthSettings) -> KeycloakAuth:
    """Create a KeycloakAuth instance from settings.

    Convenience function that extracts settings from a Pydantic settings object.

    Args:
        settings: Settings object with AUTH, KEYCLOAK_SERVER_URL, REALM_NAME

    Returns:
        Configured KeycloakAuth instance
    """
    return KeycloakAuth(
        keycloak_url=settings.KEYCLOAK_SERVER_URL,
        realm=settings.REALM_NAME,
        verify_signature=settings.AUTH,
    )


# Re-export JOSEError for convenience
__all__ = [
    "AuthFlag",
    "KeycloakAuth",
    "AuthSettings",
    "create_keycloak_auth",
    "require_keycloak_url",
    "JOSEError",
]
