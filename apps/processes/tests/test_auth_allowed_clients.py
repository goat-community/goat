"""processes accepts tokens only from the clients in AUTH_ALLOWED_CLIENTS.

The check itself lives in goatlib's ``KeycloakAuth`` (tested there); these
tests cover processes's wiring: the setting reaches the ``KeycloakAuth`` the
service builds, and a token of another client gets the same 401 as any
invalid token. Tokens are signed with a locally generated RSA key.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from goatlib.auth import KeycloakAuth
from jose import jwt
from starlette.requests import Request

from processes.config import settings
from processes.deps import auth as auth_deps

SERVICE_DIR = Path(__file__).resolve().parents[1]
USER_ID = "744e4fd1-685c-495c-8b02-efebce875359"


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
        "iss": "http://kc/realms/goat",
        "sub": USER_ID,
        "aud": "account",
        "azp": azp,
        "iat": now,
        "exp": now + 300,
    }
    return jwt.encode(claims, private_pem, algorithm="RS256")


def _request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


def _use_keycloak(
    monkeypatch: pytest.MonkeyPatch, public_pem: str, allowed: str
) -> None:
    """Turn AUTH on and verify tokens against the local key and ``allowed``."""
    keycloak = KeycloakAuth("http://kc", "goat", allowed_clients=allowed)
    keycloak._public_key = public_pem
    monkeypatch.setattr(auth_deps, "_keycloak_auth", keycloak)
    monkeypatch.setattr(settings, "AUTH", True)


async def test_token_of_an_allowed_client_is_accepted(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web,goat-scripts")
    token = _token(private_pem, azp="goat-web")

    claims = await auth_deps.get_user_token(_request(), token=token)
    assert claims["azp"] == "goat-web"


async def test_token_of_another_client_is_401(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web")
    token = _token(private_pem, azp="other-app")

    with pytest.raises(HTTPException) as err:
        await auth_deps.get_user_token(_request(), token=token)
    assert err.value.status_code == 401
    # Like any other invalid claim: no setting name, no client list.
    assert err.value.detail == "Invalid token: Invalid authorized party"


async def test_optional_routes_treat_another_client_as_anonymous(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    """As with an invalid token: public data only, never the token's user."""
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "goat-web")
    token = _token(private_pem, azp="other-app")

    assert await auth_deps.get_optional_user_id(_request(), token=token) is None


async def test_unset_accepts_every_client(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    private_pem, public_pem = key_pair
    _use_keycloak(monkeypatch, public_pem, "")
    token = _token(private_pem, azp="other-app")

    claims = await auth_deps.get_user_token(_request(), token=token)
    assert claims["azp"] == "other-app"


async def test_auth_off_is_unaffected(
    monkeypatch: pytest.MonkeyPatch, key_pair: tuple[str, str]
) -> None:
    """With AUTH=False the service decodes tokens unverified, as before."""
    private_pem, _ = key_pair
    keycloak = KeycloakAuth(
        "http://kc", "goat", verify_signature=False, allowed_clients="goat-web"
    )
    monkeypatch.setattr(auth_deps, "_keycloak_auth", keycloak)
    monkeypatch.setattr(settings, "AUTH", False)
    token = _token(private_pem, azp="other-app")

    claims = await auth_deps.get_user_token(_request(), token=token)
    assert claims["azp"] == "other-app"


def test_service_verifies_with_the_setting() -> None:
    """The KeycloakAuth built at import carries the bare AUTH_ALLOWED_CLIENTS."""
    env = {
        **os.environ,
        "AUTH": "true",
        "KEYCLOAK_SERVER_URL": "http://kc",
        "AUTH_ALLOWED_CLIENTS": "goat-web, goat-scripts",
    }
    out = subprocess.run(
        [
            sys.executable,
            "-c",
            "from processes.deps.auth import _keycloak_auth as k;"
            "print(','.join(sorted(k.allowed_clients)))",
        ],
        cwd=SERVICE_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert out.stdout.strip().splitlines()[-1] == "goat-scripts,goat-web"
