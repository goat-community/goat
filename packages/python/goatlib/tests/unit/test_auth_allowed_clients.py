"""AUTH_ALLOWED_CLIENTS: a verified token must come from an allowed client.

In a Keycloak realm shared with other applications, every client of the realm
can obtain a token that GOAT's signature check accepts. With an allow-list
set, ``KeycloakAuth`` also requires the token's ``azp`` (the client Keycloak
issued it to) to be on the list. Tokens are signed here with a locally
generated RSA key; no Keycloak is involved.
"""

import logging
import time
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from goatlib.auth import (
    KeycloakAuth,
    create_keycloak_auth,
    parse_allowed_clients,
    require_own_client_allowed,
)
from jose import JOSEError, jwt

pytestmark = pytest.mark.unit

KEYCLOAK_URL = "http://kc"
REALM = "goat"
ISSUER = f"{KEYCLOAK_URL}/realms/{REALM}"


@pytest.fixture(scope="module")
def key_pair() -> tuple[str, str]:
    """A fresh RSA key pair as (private PEM, public PEM)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = (
        key.public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


def _token(private_pem: str, **claims: Any) -> str:
    """A Keycloak-shaped access token: ``aud`` is ``account``, as by default."""
    now = int(time.time())
    payload = {
        "iss": ISSUER,
        "sub": "744e4fd1-685c-495c-8b02-efebce875359",
        "aud": "account",
        "typ": "Bearer",
        "iat": now,
        "exp": now + 300,
        **claims,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return jwt.encode(payload, private_pem, algorithm="RS256")


def _auth(
    public_pem: str, allowed: str | None, verify_signature: bool = True
) -> KeycloakAuth:
    auth = KeycloakAuth(
        KEYCLOAK_URL,
        REALM,
        verify_signature=verify_signature,
        allowed_clients=allowed,
    )
    # Skip the network fetch of the realm key.
    auth._public_key = public_pem
    return auth


def test_token_of_an_allowed_client_is_accepted(key_pair: tuple[str, str]) -> None:
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, "goat-web,goat-scripts")
    claims = auth.decode_token(_token(private_pem, azp="goat-scripts"))
    assert claims["azp"] == "goat-scripts"


def test_token_of_another_client_is_rejected(key_pair: tuple[str, str]) -> None:
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, "goat-web")
    with pytest.raises(JOSEError) as err:
        auth.decode_token(_token(private_pem, azp="other-app"))
    # The caller learns neither the setting nor which clients it allows.
    assert str(err.value) == "Invalid authorized party"


def test_token_without_azp_is_rejected_when_clients_are_set(
    key_pair: tuple[str, str],
) -> None:
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, "goat-web")
    with pytest.raises(JOSEError) as err:
        auth.decode_token(_token(private_pem, azp=None))
    assert str(err.value) == "Invalid authorized party"


def test_refused_client_is_logged_once_as_a_warning(
    key_pair: tuple[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    """The operator sees which client was refused; repeats go to debug."""
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, "goat-web")
    token = _token(private_pem, azp="other-app")
    caplog.set_level(logging.DEBUG, logger="goatlib.auth")
    for _ in range(3):
        with pytest.raises(JOSEError):
            auth.decode_token(token)
    refused = [r for r in caplog.records if "other-app" in r.getMessage()]
    assert [r.levelno for r in refused] == [
        logging.WARNING,
        logging.DEBUG,
        logging.DEBUG,
    ]
    assert all(token not in r.getMessage() for r in caplog.records)


def test_audience_does_not_stand_in_for_the_client(
    key_pair: tuple[str, str],
) -> None:
    """A token of another client that lists GOAT's client in ``aud`` (as an
    audience mapper or a client role of GOAT's client would add) is still
    another client's token."""
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, "goat-web")
    token = _token(private_pem, azp="other-app", aud=["goat-web", "account"])
    with pytest.raises(JOSEError):
        auth.decode_token(token)


@pytest.mark.parametrize("allowed", [None, "", " , "])
def test_unset_accepts_every_client(
    key_pair: tuple[str, str], allowed: str | None
) -> None:
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, allowed)
    assert auth.decode_token(_token(private_pem, azp="other-app"))["azp"] == (
        "other-app"
    )
    assert auth.decode_token(_token(private_pem, azp=None))["sub"]


def test_auth_off_skips_the_check(key_pair: tuple[str, str]) -> None:
    """Without signature verification (AUTH=False) nothing changes."""
    private_pem, public_pem = key_pair
    auth = _auth(public_pem, "goat-web", verify_signature=False)
    assert auth.decode_token(_token(private_pem, azp="other-app"))["azp"] == (
        "other-app"
    )


def test_signature_is_still_checked(key_pair: tuple[str, str]) -> None:
    """An allowed client does not excuse a token signed with another key."""
    _, public_pem = key_pair
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_pem = other.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    auth = _auth(public_pem, "goat-web")
    with pytest.raises(JOSEError):
        auth.decode_token(_token(other_pem, azp="goat-web"))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, frozenset()),
        ("", frozenset()),
        (" , ,", frozenset()),
        ("goat", frozenset({"goat"})),
        ("goat-web, goat-scripts ,", frozenset({"goat-web", "goat-scripts"})),
        (["goat-web", " ", "goat-scripts"], frozenset({"goat-web", "goat-scripts"})),
    ],
)
def test_parse_allowed_clients(raw: object, expected: frozenset[str]) -> None:
    assert parse_allowed_clients(raw) == expected  # type: ignore[arg-type]


def test_create_keycloak_auth_without_the_setting_accepts_every_client() -> None:
    """Settings objects that predate AUTH_ALLOWED_CLIENTS still work."""

    class _Settings:
        AUTH = True
        KEYCLOAK_SERVER_URL = KEYCLOAK_URL
        REALM_NAME = REALM

    assert create_keycloak_auth(_Settings()).allowed_clients == frozenset()


@pytest.mark.parametrize(
    ("auth", "allowed", "own"),
    [
        (True, "", "goat-web"),
        (True, None, "goat-web"),
        (True, "goat-web, goat-scripts", "goat-web"),
        (True, "goat-scripts", None),
        (True, "goat-scripts", ""),
        (False, "goat-scripts", "goat-web"),
    ],
)
def test_own_client_check_passes(
    auth: bool, allowed: str | None, own: str | None
) -> None:
    require_own_client_allowed(auth, allowed, own)


def test_own_client_missing_from_the_list_is_refused() -> None:
    with pytest.raises(ValueError, match="KEYCLOAK_CLIENT_ID"):
        require_own_client_allowed(True, "goat-scripts", "goat-web")


def test_create_keycloak_auth_reads_the_setting() -> None:
    class _Settings:
        AUTH = True
        KEYCLOAK_SERVER_URL = KEYCLOAK_URL
        REALM_NAME = REALM
        AUTH_ALLOWED_CLIENTS = "goat-web,goat-scripts"

    auth = create_keycloak_auth(_Settings())
    assert auth.allowed_clients == frozenset({"goat-web", "goat-scripts"})
