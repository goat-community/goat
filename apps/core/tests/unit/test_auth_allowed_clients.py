"""core accepts tokens only from the clients in AUTH_ALLOWED_CLIENTS.

Every core route that needs a login verifies the token through
``core.deps.auth.decode_token`` (``auth_z``, ``auth``, ``user_token``), which
delegates to goatlib's ``KeycloakAuth``. These tests swap in a ``KeycloakAuth``
that trusts a locally generated RSA key, so tokens are signed here and no
Keycloak is involved.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from core.core.config import Settings, settings
from core.deps import auth as auth_deps
from core.endpoints.deps import get_current_token_claims
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from goatlib.auth import KeycloakAuth
from httpx import AsyncClient
from jose import jwt
from starlette.requests import Request

CORE_DIR = Path(__file__).resolve().parents[2]
ISSUER = "http://kc/realms/goat"


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


def _token(private_pem: str, azp: str) -> str:
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "sub": settings.DEFAULT_USER_ID,
        "aud": "account",
        "azp": azp,
        "iat": now,
        "exp": now + 300,
    }
    return jwt.encode(claims, private_pem, algorithm="RS256")


def _request(token: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
        }
    )


def _use_keycloak(
    monkeypatch: pytest.MonkeyPatch, public_pem: str, allowed: str
) -> None:
    """Turn AUTH on and verify tokens against the local key and ``allowed``."""
    keycloak = KeycloakAuth("http://kc", "goat", allowed_clients=allowed)
    keycloak._public_key = public_pem
    monkeypatch.setattr(auth_deps, "_keycloak_auth", keycloak)
    monkeypatch.setattr(settings, "AUTH", True)


def test_token_of_an_allowed_client_is_accepted(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web,goat-scripts")
    token = _token(private_pem, azp="goat-web")

    assert get_current_token_claims(_request(token))["azp"] == "goat-web"
    assert auth_deps.auth(_request(token)) == token


def test_token_of_another_client_is_401(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web")
    token = _token(private_pem, azp="other-app")

    with pytest.raises(HTTPException) as claims_err:
        get_current_token_claims(_request(token))
    assert claims_err.value.status_code == 401
    # Like any other invalid claim: no setting name, no client list.
    assert claims_err.value.detail == "Invalid authorized party"

    with pytest.raises(HTTPException) as auth_err:
        auth_deps.auth(_request(token))
    assert auth_err.value.status_code == 401
    assert auth_err.value.detail == "Invalid authorized party"


async def _route_allowed(*_: object) -> bool:
    return True


async def test_auth_z_rejects_another_client(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    """Refused even where the route-level authorization would let it in."""
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web")
    monkeypatch.setattr(auth_deps, "_validate_authorization", _route_allowed)

    allowed = _token(private_pem, azp="goat-web")
    assert await auth_deps.auth_z(_request(allowed), async_session=None) is True  # type: ignore[arg-type]

    other = _token(private_pem, azp="other-app")
    with pytest.raises(HTTPException) as err:
        await auth_deps.auth_z(_request(other), async_session=None)  # type: ignore[arg-type]
    assert err.value.status_code == 401


async def test_route_answers_401_for_another_client(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str], client: AsyncClient
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web")
    monkeypatch.setattr(auth_deps, "_validate_authorization", _route_allowed)
    token = _token(private_pem, azp="other-app")

    response = await client.get(
        f"{settings.API_V2_STR}/users/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_unset_accepts_every_client(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "")
    token = _token(private_pem, azp="other-app")

    assert get_current_token_claims(_request(token))["azp"] == "other-app"


def test_auth_off_is_unaffected(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web")
    monkeypatch.setattr(settings, "AUTH", False)
    token = _token(private_pem, azp="other-app")

    assert get_current_token_claims(_request(token))["azp"] == "other-app"
    assert auth_deps.auth(_request(token)) == token


def _auth_on_env(monkeypatch: pytest.MonkeyPatch, allowed: str, own: str) -> None:
    monkeypatch.setenv("AUTH", "true")
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    monkeypatch.setenv("AUTH_ALLOWED_CLIENTS", allowed)
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", own)


def test_core_refuses_a_list_without_its_own_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Such a list would refuse every user signing in through the web app."""
    _auth_on_env(monkeypatch, "goat-scripts", "goat-web")
    with pytest.raises(ValueError, match="KEYCLOAK_CLIENT_ID"):
        Settings()


@pytest.mark.parametrize("allowed", ["goat-web", " goat-scripts , goat-web ", ""])
def test_core_starts_with_its_own_client_listed_or_no_list(
    monkeypatch: pytest.MonkeyPatch, allowed: str
) -> None:
    _auth_on_env(monkeypatch, allowed, "goat-web")
    assert Settings().AUTH_ALLOWED_CLIENTS == allowed


def test_own_client_check_needs_auth_on(monkeypatch: pytest.MonkeyPatch) -> None:
    _auth_on_env(monkeypatch, "goat-scripts", "goat-web")
    monkeypatch.setenv("AUTH", "false")
    assert Settings().AUTH_ALLOWED_CLIENTS == "goat-scripts"


def test_settings_read_the_bare_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    monkeypatch.delenv("AUTH_ALLOWED_CLIENTS", raising=False)
    assert Settings().AUTH_ALLOWED_CLIENTS == ""
    monkeypatch.setenv("AUTH_ALLOWED_CLIENTS", "goat-web,goat-scripts")
    assert Settings().AUTH_ALLOWED_CLIENTS == "goat-web,goat-scripts"


def test_core_verifies_with_the_setting() -> None:
    """The KeycloakAuth core builds at import carries AUTH_ALLOWED_CLIENTS."""
    env = {
        **os.environ,
        "AUTH": "true",
        "KEYCLOAK_SERVER_URL": "http://kc",
        "KEYCLOAK_CLIENT_ID": "goat-web",
        "AUTH_ALLOWED_CLIENTS": "goat-web, goat-scripts",
    }
    out = subprocess.run(
        [
            sys.executable,
            "-c",
            "from core.deps.auth import _keycloak_auth as k;"
            "print(','.join(sorted(k.allowed_clients)))",
        ],
        cwd=CORE_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert out.stdout.strip().splitlines()[-1] == "goat-scripts,goat-web"
