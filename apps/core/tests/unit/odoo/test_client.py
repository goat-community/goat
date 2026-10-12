"""The client talks JSON-2, enforces the caller's allow-list, timeouts, the
concurrency cap and the circuit breaker."""

import asyncio
from collections.abc import AsyncIterator

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from core.odoo import OdooClient, OdooRejected, OdooUnavailable

pytestmark = pytest.mark.unit

CALLS = {
    ("helpdesk.ticket", "read"),
    ("helpdesk.ticket", "search_read"),
    ("ir.attachment", "create"),
}
UPLOADS = {("ir.attachment", "create")}


@pytest.fixture
async def server() -> AsyncIterator[tuple[TestServer, list[dict]]]:
    seen: list[dict] = []
    state = {"in_flight": 0, "max_in_flight": 0}

    async def handler(request: web.Request) -> web.Response:
        model, method = request.match_info["model"], request.match_info["method"]
        body = await request.json()
        seen.append(
            {
                "model": model,
                "method": method,
                "body": body,
                "headers": dict(request.headers),
            }
        )
        if method == "search_read" and body.get("domain") == ["boom"]:
            return web.Response(status=500, text="oops")
        if method == "search_read" and body.get("domain") == ["denied"]:
            return web.json_response(
                {"name": "odoo.exceptions.AccessError", "message": "no"}, status=403
            )
        if method == "search_read" and body.get("domain") == ["slow"]:
            await asyncio.sleep(0.5)
        if model == "ir.attachment" and method == "create":
            await asyncio.sleep(float(body.get("delay", 0)))
        if method == "search_read" and body.get("domain") == ["busy"]:
            state["in_flight"] += 1
            state["max_in_flight"] = max(state["max_in_flight"], state["in_flight"])
            await asyncio.sleep(0.05)
            state["in_flight"] -= 1
            return web.json_response(state["max_in_flight"])
        if method == "search_read" and body.get("domain") == ["maintenance"]:
            return web.Response(status=200, text="<html>maintenance</html>")
        if method == "search_read" and body.get("domain") == ["bad_json_error"]:
            return web.Response(
                status=400, text='["x"]', content_type="application/json"
            )
        if method == "search_read" and body.get("domain") == ["redirect"]:
            return web.Response(status=302, headers={"Location": "https://example.org"})
        return web.json_response({"ok": True})

    app = web.Application()
    app.router.add_post("/json/2/{model}/{method}", handler)
    srv = TestServer(app)
    await srv.start_server()
    yield srv, seen
    await srv.close()


def _client(srv: TestServer, **kw: float) -> OdooClient:
    return _at(str(srv.make_url("")).rstrip("/"), **kw)


def _at(url: str, **kw: float) -> OdooClient:
    return OdooClient(
        url, "the-db", "the-key", allowed_calls=CALLS, upload_calls=UPLOADS, **kw
    )


async def test_sends_json2_request(server: tuple[TestServer, list[dict]]) -> None:
    srv, seen = server
    client = _client(srv)
    assert await client.call("helpdesk.ticket", "read", ids=[1], fields=["name"]) == {
        "ok": True
    }
    await client.close()
    req = seen[0]
    assert (req["model"], req["method"]) == ("helpdesk.ticket", "read")
    assert req["body"] == {"ids": [1], "fields": ["name"]}
    assert req["headers"]["Authorization"] == "bearer the-key"
    assert req["headers"]["X-Odoo-Database"] == "the-db"


async def test_rejects_calls_outside_the_allow_list(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, seen = server
    client = _client(srv)
    with pytest.raises(PermissionError):
        await client.call("account.move", "search_read", domain=[])
    with pytest.raises(PermissionError):
        await client.call("helpdesk.ticket", "unlink", ids=[1])
    await client.close()
    assert seen == []


async def test_4xx_is_rejected_with_odoo_error(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv)
    with pytest.raises(OdooRejected) as exc:
        await client.call("helpdesk.ticket", "search_read", domain=["denied"])
    await client.close()
    assert exc.value.status == 403
    assert exc.value.name == "odoo.exceptions.AccessError"


async def test_5xx_and_timeouts_are_unavailable(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv, timeout=0.1)
    with pytest.raises(OdooUnavailable):
        await client.call("helpdesk.ticket", "search_read", domain=["boom"])
    with pytest.raises(OdooUnavailable):
        await client.call("helpdesk.ticket", "search_read", domain=["slow"])
    await client.close()


async def test_connection_refused_is_unavailable() -> None:
    client = _at("http://127.0.0.1:9", timeout=1)
    with pytest.raises(OdooUnavailable):
        await client.call("helpdesk.ticket", "search_read", domain=[])
    await client.close()


async def test_concurrency_is_capped(server: tuple[TestServer, list[dict]]) -> None:
    srv, _ = server
    client = _client(srv, max_concurrency=2)
    results = await asyncio.gather(
        *(
            client.call("helpdesk.ticket", "search_read", domain=["busy"])
            for _ in range(6)
        )
    )
    await client.close()
    assert max(results) <= 2


async def test_2xx_with_non_json_body_is_unavailable(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv)
    with pytest.raises(OdooUnavailable):
        await client.call("helpdesk.ticket", "search_read", domain=["maintenance"])
    await client.close()


async def test_4xx_with_non_dict_json_body(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv)
    with pytest.raises(OdooRejected) as exc:
        await client.call("helpdesk.ticket", "search_read", domain=["bad_json_error"])
    await client.close()
    assert exc.value.status == 400
    assert exc.value.name == ""


async def test_redirect_is_unavailable(server: tuple[TestServer, list[dict]]) -> None:
    srv, _ = server
    client = _client(srv)
    with pytest.raises(OdooUnavailable):
        await client.call("helpdesk.ticket", "search_read", domain=["redirect"])
    await client.close()


async def test_waiting_for_a_slot_is_time_boxed(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv, max_concurrency=1, acquire_timeout=0.05)
    slow = asyncio.create_task(
        client.call("helpdesk.ticket", "search_read", domain=["slow"])
    )
    await asyncio.sleep(0.01)
    loop = asyncio.get_running_loop()
    for _ in range(4):  # more than the breaker threshold
        started = loop.time()
        with pytest.raises(OdooUnavailable, match="slot"):
            await client.call("helpdesk.ticket", "search_read", domain=[])
        assert loop.time() - started < 0.4
    await slow
    # a busy pool is not an outage: the breaker stayed closed
    assert await client.call("helpdesk.ticket", "read", ids=[1]) == {"ok": True}
    await client.close()


async def test_circuit_breaker_fails_fast_then_lets_one_probe_through(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, seen = server
    clock = [1000.0]
    client = _client(srv, open_seconds=30, now=lambda: clock[0])
    for _ in range(3):
        with pytest.raises(OdooUnavailable, match="HTTP 500"):
            await client.call("helpdesk.ticket", "search_read", domain=["boom"])
    sent = len(seen)
    with pytest.raises(OdooUnavailable, match="circuit open"):
        await client.call("helpdesk.ticket", "read", ids=[1])
    clock[0] += 29
    with pytest.raises(OdooUnavailable, match="circuit open"):
        await client.call("helpdesk.ticket", "read", ids=[1])
    assert len(seen) == sent  # nothing reached Odoo while open
    # half-open: one probe goes through; it fails, so the breaker opens again
    clock[0] += 2
    with pytest.raises(OdooUnavailable, match="HTTP 500"):
        await client.call("helpdesk.ticket", "search_read", domain=["boom"])
    with pytest.raises(OdooUnavailable, match="circuit open"):
        await client.call("helpdesk.ticket", "read", ids=[1])
    # the next probe succeeds and closes it
    clock[0] += 31
    assert await client.call("helpdesk.ticket", "read", ids=[1]) == {"ok": True}
    assert await client.call("helpdesk.ticket", "read", ids=[2]) == {"ok": True}
    await client.close()


async def test_odoo_refusals_do_not_open_the_breaker(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv)
    for _ in range(5):
        with pytest.raises(OdooRejected):
            await client.call("helpdesk.ticket", "search_read", domain=["denied"])
    assert await client.call("helpdesk.ticket", "read", ids=[1]) == {"ok": True}
    await client.close()


async def test_only_one_probe_at_a_time_while_half_open(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    clock = [0.0]
    client = _client(srv, now=lambda: clock[0])
    for _ in range(3):
        with pytest.raises(OdooUnavailable):
            await client.call("helpdesk.ticket", "search_read", domain=["boom"])
    clock[0] += 31
    probe = asyncio.create_task(
        client.call("helpdesk.ticket", "search_read", domain=["slow"])
    )
    await asyncio.sleep(0.01)
    with pytest.raises(OdooUnavailable, match="circuit open"):
        await client.call("helpdesk.ticket", "read", ids=[1])
    await probe  # succeeds: closed again
    assert await client.call("helpdesk.ticket", "read", ids=[1]) == {"ok": True}
    await client.close()


async def test_slow_uploads_get_their_own_timeout_and_do_not_open_the_breaker(
    server: tuple[TestServer, list[dict]],
) -> None:
    srv, _ = server
    client = _client(srv, timeout=0.05, upload_timeout=0.3)
    # longer than the normal timeout, within the upload timeout
    assert await client.call("ir.attachment", "create", delay=0.1) == {"ok": True}
    for _ in range(4):  # more than the breaker threshold
        with pytest.raises(OdooUnavailable):
            await client.call("ir.attachment", "create", delay=0.5)
    assert await client.call("helpdesk.ticket", "read", ids=[1]) == {"ok": True}
    await client.close()
