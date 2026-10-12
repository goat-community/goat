"""HTTP layer: feature gate, multipart limits, error mapping, download."""

import json
from collections.abc import AsyncIterator, Iterator
from dataclasses import replace
from uuid import UUID

import pytest
from core.core.config import settings
from core.main import app
from core.support.body_limit import SupportBodyLimit
from core.support.deps import get_email_proof, get_support_service
from core.support.errors import SupportUnavailable
from core.support.odoo_client import OdooRejected
from core.support.service import SupportService
from core.support.throttle import RateLimiter, TTLCache
from core.support.types import AttachmentMeta, EmailProof
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from jose import jwt

from .fakes import FakeProvider, MemoryStore, make_message, make_ticket

pytestmark = pytest.mark.unit
BASE = f"{settings.API_V2_STR}/support"
ME = UUID(settings.DEFAULT_USER_ID)
MB = 1024 * 1024


@pytest.fixture
def enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ODOO_URL", "https://odoo.example")
    monkeypatch.setattr(settings, "ODOO_DB", "db")
    monkeypatch.setattr(settings, "ODOO_SUPPORT_API_KEY", "key")
    monkeypatch.setattr(settings, "ODOO_SUPPORT_TEAM_ID", 1)


@pytest.fixture
def world(enabled: None) -> Iterator[tuple[FakeProvider, MemoryStore]]:
    provider, store = FakeProvider(), MemoryStore()
    store.add_user(email="m@x.de", contact_id=100, user_id=ME)
    provider.add(
        make_ticket(latest_message_id=60),
        messages=(
            make_message(
                60,
                100,
                attachments=(AttachmentMeta(900, "map.png", "image/png", 3),),
            ),
        ),
    )
    service = SupportService(
        provider,
        store,
        cache=TTLCache(),
        ticket_limiter=RateLimiter(10, 3600),
        reply_limiter=RateLimiter(60, 3600),
        email_proof=EmailProof(verified_email=None, trust_stored=True),
    )
    app.dependency_overrides[get_support_service] = lambda: service
    yield provider, store
    app.dependency_overrides.pop(get_support_service, None)


def _form(**overrides: str) -> dict[str, str]:
    data = {
        "subject": "Heatmap empty",
        "description": "Nothing shows up.",
        "category": "bug",
        "impact": "blocking",
        "request_id": "req-12345678",
        "technical": json.dumps({"GOAT version": "3.0.1"}),
    }
    data.update(overrides)
    return data


async def test_everything_is_404_when_disabled(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in (
        "ODOO_URL",
        "ODOO_DB",
        "ODOO_SUPPORT_API_KEY",
        "ODOO_SUPPORT_TEAM_ID",
    ):
        monkeypatch.setattr(settings, name, None)
    for path in ("/summary", "/tickets", "/tickets/00031", "/colleagues"):
        assert (await client.get(BASE + path)).status_code == 404
    assert (await client.post(f"{BASE}/tickets", data=_form())).status_code == 404


async def test_summary_and_list(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    assert (await client.get(f"{BASE}/summary")).json() == {
        "needs_reply": 0,
        "unread": 0,
    }
    body = (
        await client.get(f"{BASE}/tickets", params={"scope": "mine", "state": "open"})
    ).json()
    assert [t["ref"] for t in body] == ["00031"]
    assert body[0]["is_mine"] is True and body[0]["status"] == "in_progress"


async def test_ticket_detail(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    body = (await client.get(f"{BASE}/tickets/00031")).json()
    assert body["ticket"]["ref"] == "00031"
    assert body["messages"][0]["is_me"] is True
    assert body["messages"][0]["attachments"][0]["name"] == "map.png"


async def test_ticket_detail_carries_staff_photos_by_contact_id(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    detail = provider.tickets["00031"]
    uri = "data:image/jpeg;base64,/9j/AAAA"
    provider.tickets["00031"] = replace(
        detail,
        messages=(*detail.messages, make_message(61, 300, agent=True)),
        avatars={300: uri},
    )
    body = (await client.get(f"{BASE}/tickets/00031")).json()
    assert body["avatars"] == {"300": uri}
    customer, agent = body["messages"]
    # the key to the photos is only ever given for GOAT team members
    assert customer["author_contact_id"] is None
    assert agent["author_contact_id"] == 300


async def test_ticket_detail_without_photos_has_empty_avatars(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    body = (await client.get(f"{BASE}/tickets/00031")).json()
    assert body["avatars"] == {}


async def test_ticket_detail_names_the_agent_contact_before_they_write(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    detail = provider.tickets["00031"]
    uri = "data:image/jpeg;base64,/9j/AAAA"
    provider.tickets["00031"] = replace(
        detail, avatars={300: uri}, agent_contact_id=300
    )
    body = (await client.get(f"{BASE}/tickets/00031")).json()
    assert body["agent_contact_id"] == 300
    assert body["avatars"] == {"300": uri}
    assert all(m["author_contact_id"] is None for m in body["messages"])


async def test_ticket_detail_without_agent_or_rating_has_nulls(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    body = (await client.get(f"{BASE}/tickets/00031")).json()
    assert body["agent_contact_id"] is None
    assert body["my_rating"] is None


async def test_ticket_detail_carries_my_rating_of_a_solved_ticket(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    detail = provider.tickets["00031"]
    provider.tickets["00031"] = replace(
        detail, ticket=replace(detail.ticket, status="solved")
    )
    provider.my_ratings[(31, 100)] = "top"
    body = (await client.get(f"{BASE}/tickets/00031")).json()
    assert body["my_rating"] == "top"


async def test_message_of_a_deleted_author_is_unknown_and_never_mine(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    detail = provider.tickets["00031"]
    orphan = replace(
        make_message(61, 0), author_contact_id=None, author_name="", author_known=False
    )
    provider.tickets["00031"] = replace(detail, messages=(*detail.messages, orphan))
    first, second = (await client.get(f"{BASE}/tickets/00031")).json()["messages"]
    assert first["author_known"] is True and first["is_me"] is True
    assert (
        second["author_known"],
        second["author_name"],
        second["is_agent"],
        second["is_me"],
    ) == (False, "", False, False)


async def test_create_with_files(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    files = [
        ("files", ("a.png", b"PNG", "image/png")),
        ("files", ("b.txt", b"hello", "text/plain")),
    ]
    r = await client.post(f"{BASE}/tickets", data=_form(), files=files)
    assert r.status_code == 201, r.text
    assert r.json() == {"ref": "00041", "message_id": 901, "failed_files": []}
    assert provider.posts == [(41, 100, "", ("a.png", "b.txt"))]


@pytest.mark.parametrize(
    ("files", "detail"),
    [
        (
            [("files", (f"f{i}.txt", b"x", "text/plain")) for i in range(11)],
            "too_many_files",
        ),
        (
            [
                (
                    "files",
                    ("big.bin", b"x" * (10 * MB + 1), "application/octet-stream"),
                )
            ],
            "file_too_large",
        ),
        (
            [
                (
                    "files",
                    (f"f{i}.bin", b"x" * (9 * MB), "application/octet-stream"),
                )
                for i in range(6)
            ],
            "files_too_large",
        ),
    ],
)
async def test_file_limits(
    client: AsyncClient,
    world: tuple[FakeProvider, MemoryStore],
    files: list,
    detail: str,
) -> None:
    r = await client.post(f"{BASE}/tickets", data=_form(), files=files)
    assert r.status_code == 413
    assert r.json()["detail"] == detail


async def test_reply_and_state_changes(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    r = await client.post(f"{BASE}/tickets/00031/messages", data={"text": "Thanks"})
    assert r.status_code == 201
    assert (await client.post(f"{BASE}/tickets/00031/resolve")).status_code == 204
    assert provider.statuses == [(31, "solved")]


async def test_error_mapping(
    client: AsyncClient,
    world: tuple[FakeProvider, MemoryStore],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = world
    assert (await client.get(f"{BASE}/tickets/99999")).status_code == 404
    assert (
        await client.get(f"{BASE}/tickets", params={"scope": "org"})
    ).status_code == 403
    r = await client.post(f"{BASE}/tickets/00031/messages", data={"text": "  "})
    assert (r.status_code, r.json()["detail"]) == (422, "empty_reply")

    async def down(*_: object, **__: object) -> None:
        raise SupportUnavailable("timeout")

    monkeypatch.setattr(provider, "get_ticket", down)
    r = await client.get(f"{BASE}/tickets/00031")
    assert (r.status_code, r.json()["detail"]) == (503, "support_unavailable")


@pytest.mark.parametrize(
    "exc",
    [OdooRejected(403, "odoo.exceptions.AccessError", "no"), LookupError("stage")],
)
async def test_odoo_rejection_and_missing_config_are_503(
    client: AsyncClient,
    world: tuple[FakeProvider, MemoryStore],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    exc: Exception,
) -> None:
    provider, _ = world

    async def boom(*_: object, **__: object) -> None:
        raise exc

    monkeypatch.setattr(provider, "get_ticket", boom)
    with caplog.at_level("WARNING"):
        r = await client.get(f"{BASE}/tickets/00031")
    assert (r.status_code, r.json()["detail"]) == (503, "support_unavailable")
    assert any(rec.levelname == "WARNING" for rec in caplog.records)


async def test_download(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    r = await client.get(f"{BASE}/tickets/00031/attachments/900")
    assert r.status_code == 200
    assert r.content == b"PNG"
    disposition = r.headers["content-disposition"]
    assert disposition.startswith('attachment; filename="f.png"; filename*=UTF-8')
    assert "filename*=UTF-8''f.png" in disposition
    assert r.headers["x-content-type-options"] == "nosniff"
    assert (
        await client.get(f"{BASE}/tickets/00031/attachments/901")
    ).status_code == 404


async def test_colleagues_exclude_me(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    _, store = world
    store.add_user(email="anna@x.de", name="Anna Keller", contact_id=101)
    body = (await client.get(f"{BASE}/colleagues")).json()
    assert [c["email"] for c in body] == ["anna@x.de"]
    # the web matches colleagues to followers by contact, not by name
    assert body[0]["contact_id"] == 101


async def test_download_header_is_injection_safe(
    client: AsyncClient,
    world: tuple[FakeProvider, MemoryStore],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = world

    async def nasty(attachment_id: int) -> tuple[AttachmentMeta, bytes]:
        return AttachmentMeta(attachment_id, 'a"b/\u00fc;.png', "image/png", 3), b"x"

    monkeypatch.setattr(provider, "download", nasty)
    r = await client.get(f"{BASE}/tickets/00031/attachments/900")
    assert r.headers["content-disposition"] == (
        "attachment; filename=\"a_b/_;.png\"; filename*=UTF-8''a%22b%2F%C3%BC%3B.png"
    )


@pytest.mark.parametrize("technical", ["[" * 4000, "[1, 2]", "not json", "null"])
async def test_invalid_technical_is_422(
    client: AsyncClient,
    world: tuple[FakeProvider, MemoryStore],
    technical: str,
) -> None:
    r = await client.post(f"{BASE}/tickets", data=_form(technical=technical))
    assert (r.status_code, r.json()["detail"]) == (422, "invalid_technical")


async def test_feature_request_drops_impact(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, _ = world
    r = await client.post(
        f"{BASE}/tickets",
        data=_form(category="feature_request", impact="blocking"),
    )
    assert r.status_code == 201, r.text
    assert provider.created[-1].impact is None


async def test_too_many_colleagues_is_422(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    ids = [str(UUID(int=i + 1)) for i in range(21)]
    r = await client.post(f"{BASE}/tickets", data={**_form(), "colleague_ids": ids})
    assert r.status_code == 422


async def test_blank_description_is_422(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    r = await client.post(f"{BASE}/tickets", data=_form(description="   "))
    assert (r.status_code, r.json()["detail"]) == (422, "empty_description")


async def test_non_ascii_digits_are_not_a_ref(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    assert (await client.get(f"{BASE}/tickets/\u0663\u0661")).status_code == 422


async def test_ticket_limit_is_429(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, store = world
    service = SupportService(
        provider,
        store,
        cache=TTLCache(),
        ticket_limiter=RateLimiter(1, 3600),
        reply_limiter=RateLimiter(60, 3600),
        email_proof=EmailProof(verified_email=None, trust_stored=True),
    )
    app.dependency_overrides[get_support_service] = lambda: service
    first = await client.post(f"{BASE}/tickets", data=_form())
    second = await client.post(f"{BASE}/tickets", data=_form(request_id="req-87654321"))
    assert first.status_code == 201
    assert (second.status_code, second.json()["detail"]) == (429, "rate_limited")


async def test_reopen_rating_and_followers(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, store = world
    anna = store.add_user(email="anna@x.de", name="Anna Keller", contact_id=200)
    provider.add(
        make_ticket(
            id=32, ref="00032", status="solved", closed_at=make_ticket().created_at
        ),
        messages=(make_message(61, 100),),
    )
    assert (await client.post(f"{BASE}/tickets/00032/reopen")).status_code == 204
    assert provider.statuses == [(32, "in_progress")]

    provider.add(make_ticket(id=33, ref="00033", status="solved"))
    r = await client.post(
        f"{BASE}/tickets/00033/rating", json={"rating": "top", "comment": "Danke"}
    )
    assert r.status_code == 204
    assert provider.ratings == [(33, 100, "top", "Danke")]

    r = await client.put(
        f"{BASE}/tickets/00031/followers",
        json={"add_user_ids": [str(anna.id)], "remove_contact_ids": []},
    )
    assert r.status_code == 204
    assert provider.follower_changes == [("add", 31, (200,))]


# ------------------------------------------------------------- body size cap
async def _asgi_call(
    app_: object,
    *,
    headers: list[tuple[bytes, bytes]],
    chunks: list[bytes],
    path: str = f"{BASE}/tickets",
) -> tuple[int, bytes]:
    sent: list[dict] = []
    queue = list(chunks)

    async def receive() -> dict:
        if queue:
            return {
                "type": "http.request",
                "body": queue.pop(0),
                "more_body": bool(queue),
            }
        return {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        sent.append(message)

    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": headers,
    }
    await app_(scope, receive, send)  # type: ignore[operator]
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    body = b"".join(
        m.get("body", b"") for m in sent if m["type"] == "http.response.body"
    )
    return status, body


class _Inner:
    def __init__(self) -> None:
        self.ran = False

    async def __call__(self, scope: dict, receive: object, send: object) -> None:
        self.ran = True
        total = 0
        while True:
            message = await receive()  # type: ignore[operator]
            total += len(message.get("body", b""))
            if not message.get("more_body"):
                break
        await send({"type": "http.response.start", "status": 200, "headers": []})  # type: ignore[operator]
        await send({"type": "http.response.body", "body": str(total).encode()})  # type: ignore[operator]


def _limited(inner: _Inner) -> SupportBodyLimit:
    return SupportBodyLimit(inner, max_bytes=100, prefix=BASE)  # type: ignore[arg-type]


async def test_body_limit_rejects_declared_size_without_running_the_endpoint() -> None:
    inner = _Inner()
    status, body = await _asgi_call(
        _limited(inner), headers=[(b"content-length", b"101")], chunks=[b"x"]
    )
    assert (status, json.loads(body)) == (413, {"detail": "files_too_large"})
    assert inner.ran is False


async def test_body_limit_lets_normal_and_foreign_requests_pass() -> None:
    inner = _Inner()
    status, body = await _asgi_call(
        _limited(inner), headers=[(b"content-length", b"100")], chunks=[b"x" * 100]
    )
    assert (status, body) == (200, b"100")
    other = _Inner()
    status, _ = await _asgi_call(
        _limited(other),
        headers=[(b"content-length", b"5000")],
        chunks=[b"x" * 5000],
        path=f"{settings.API_V2_STR}/layer",
    )
    assert status == 200 and other.ran


async def test_body_limit_is_installed_on_the_app(
    world: tuple[FakeProvider, MemoryStore],
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        r = await ac.post(
            f"{BASE}/tickets",
            content=b"x",
            headers={"content-length": str(56 * MB)},
        )
    assert (r.status_code, r.json()["detail"]) == (413, "files_too_large")


async def test_streamed_multipart_over_the_cap_is_413_on_the_real_app(
    world: tuple[FakeProvider, MemoryStore],
) -> None:
    boundary = "b0undary"
    sent = 0

    async def body() -> AsyncIterator[bytes]:
        nonlocal sent
        yield (
            f'--{boundary}\r\nContent-Disposition: form-data; name="files"; '
            'filename="a.bin"\r\nContent-Type: application/octet-stream\r\n\r\n'
        ).encode()
        for _ in range(60):  # no Content-Length: chunked
            sent += 1
            yield b"x" * MB
        yield f"\r\n--{boundary}--\r\n".encode()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        r = await ac.post(
            f"{BASE}/tickets",
            content=body(),
            headers={"content-type": f"multipart/form-data; boundary={boundary}"},
        )
    assert (r.status_code, r.json()["detail"]) == (413, "files_too_large")
    assert sent < 60  # aborted while streaming, not after the whole body


async def test_provider_is_a_singleton_until_closed(enabled: None) -> None:
    from core.support import deps

    await deps.close_support_provider()
    first = await deps.get_support_provider()
    assert await deps.get_support_provider() is first
    await deps.close_support_provider()
    assert deps._provider is None and deps._client is None
    assert await deps.get_support_provider() is not first
    await deps.close_support_provider()


# ------------------------------------------------------------ email proof
async def test_unverified_email_write_is_403_email_not_verified(
    client: AsyncClient, world: tuple[FakeProvider, MemoryStore]
) -> None:
    provider, store = world
    store.users[ME] = replace(store.users[ME], contact_id=None)
    service = SupportService(
        provider,
        store,
        cache=TTLCache(),
        ticket_limiter=RateLimiter(10, 3600),
        reply_limiter=RateLimiter(60, 3600),
        email_proof=EmailProof(verified_email=None),
    )
    app.dependency_overrides[get_support_service] = lambda: service
    r = await client.post(f"{BASE}/tickets", data=_form())
    assert (r.status_code, r.json()["detail"]) == (403, "email_not_verified")
    body = (await client.get(f"{BASE}/tickets")).json()
    assert body == []


def _request(headers: dict[str, str]) -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "headers": raw})


def _bearer(claims: dict[str, object]) -> dict[str, str]:
    return {"Authorization": "Bearer " + jwt.encode(claims, "k", algorithm="HS256")}


def test_email_proof_from_the_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "AUTH", False)
    # AUTH off and no token: the default identity, stored email trusted
    assert get_email_proof(_request({})) == EmailProof(None, trust_stored=True)
    verified = _bearer({"sub": str(ME), "email": "A@X.de", "email_verified": True})
    assert get_email_proof(_request(verified)) == EmailProof("a@x.de")
    for claims in (
        {"sub": str(ME), "email": "a@x.de", "email_verified": False},
        {"sub": str(ME), "email": "a@x.de"},
        {"sub": str(ME), "email_verified": True},
        {"sub": str(ME), "email": "a@x.de", "email_verified": "true"},
    ):
        assert get_email_proof(_request(_bearer(claims))) == EmailProof(None)


def test_email_proof_with_auth_uses_the_verified_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from core.support import deps

    monkeypatch.setattr(settings, "AUTH", True)
    monkeypatch.setattr(
        deps,
        "get_current_token_claims",
        lambda request: {"email": "a@x.de", "email_verified": True},
    )
    # never the "trust the stored email" shortcut while AUTH is on
    assert get_email_proof(_request({})) == EmailProof("a@x.de")
