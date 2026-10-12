"""With authorization on, only a properly signed token gets through.

These tests run the app the way production does (see `auth_on` in
conftest.py). They also prove the harness is really on: if it were not, the
forged-token requests below would be accepted.
"""

import base64
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
from core.core.config import settings
from core.db.models.organization import Organization
from core.db.models.user import User
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.conftest import _rsa_keys, bearer, signed_token

S = settings.SCHEMA
TEAMS = f"{settings.API_V2_STR}/teams"
ORGANIZATIONS = f"{settings.API_V2_STR}/organizations"


def _segment(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


@pytest.fixture
async def viewer(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> UUID:
    org = await make_org()
    user = await make_user(org.id)
    await db_session.execute(
        text(f"INSERT INTO {S}.user_role (user_id, role_id) VALUES (:u, :r)"),
        {"u": user.id, "r": roles["organization-viewer"]},
    )
    await db_session.commit()
    return user.id


@pytest.mark.asyncio
async def test_a_signed_token_of_a_member_gets_through(
    client: AsyncClient, auth_on: Callable[..., dict[str, str]], viewer: UUID
) -> None:
    response = await client.get(TEAMS, headers=auth_on(viewer))
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_a_request_without_a_token_is_refused(
    client: AsyncClient, auth_on: Callable[..., dict[str, str]]
) -> None:
    assert (await client.get(TEAMS)).status_code == 401


@pytest.mark.asyncio
async def test_forged_tokens_are_refused(
    client: AsyncClient, auth_on: Callable[..., dict[str, str]], viewer: UUID
) -> None:
    from jose import jwt

    claims = {"sub": str(viewer), "exp": int(time.time()) + 600}
    unsigned = f"{_segment({'alg': 'none', 'typ': 'JWT'})}.{_segment(claims)}."
    # The public key used as an HMAC secret: the classic algorithm confusion.
    hmac_with_public_key = _segment({"alg": "HS256", "typ": "JWT"})
    import hashlib
    import hmac

    body = f"{hmac_with_public_key}.{_segment(claims)}"
    signature = hmac.new(_rsa_keys()[1].encode(), body.encode(), hashlib.sha256)
    confused = (
        f"{body}.{base64.urlsafe_b64encode(signature.digest()).rstrip(b'=').decode()}"
    )

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    other_key = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        .private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        .decode()
    )
    foreign = signed_token(viewer, private_pem=other_key)
    expired = signed_token(viewer, exp=int(time.time()) - 60)
    tampered = jwt.encode(claims, _rsa_keys()[0], algorithm="RS256")[:-4] + "AAAA"

    for name, token in (
        ("unsigned", unsigned),
        ("HS256 with the public key", confused),
        ("signed by another key", foreign),
        ("expired", expired),
        ("tampered signature", tampered),
    ):
        response = await client.get(TEAMS, headers=bearer(token))
        assert response.status_code == 401, f"{name} token was accepted"


@pytest.mark.asyncio
async def test_listing_all_organizations_needs_a_superuser(
    client: AsyncClient, auth_on: Callable[..., dict[str, str]], viewer: UUID
) -> None:
    for query in ("", "?throw_error=false"):
        response = await client.get(f"{ORGANIZATIONS}{query}", headers=auth_on(viewer))
        assert response.status_code == 401, f"{query or 'no query'}: {response.text}"
    superuser = await client.get(
        ORGANIZATIONS, headers=auth_on(viewer, roles=["superuser"])
    )
    assert superuser.status_code == 200, superuser.text
