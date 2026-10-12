"""The support bridge's client: its allow-list, and Odoo's errors as support errors."""

from collections.abc import AsyncIterator

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from core import odoo
from core.support.errors import SupportRejected, SupportUnavailable
from core.support.odoo_client import OdooRejected, SupportOdooClient

pytestmark = pytest.mark.unit


@pytest.fixture
async def server() -> AsyncIterator[TestServer]:
    async def handler(request: web.Request) -> web.Response:
        body = await request.json()
        if body.get("domain") == ["boom"]:
            return web.Response(status=500, text="oops")
        if body.get("domain") == ["denied"]:
            return web.json_response(
                {"name": "odoo.exceptions.AccessError", "message": "no"}, status=403
            )
        return web.json_response({"ok": True})

    app = web.Application()
    app.router.add_post("/json/2/{model}/{method}", handler)
    srv = TestServer(app)
    await srv.start_server()
    yield srv
    await srv.close()


def _client(srv: TestServer) -> SupportOdooClient:
    return SupportOdooClient(str(srv.make_url("")).rstrip("/"), "db", "key")


async def test_the_bridge_calls_go_through(server: TestServer) -> None:
    client = _client(server)
    assert await client.call("helpdesk.ticket", "read", ids=[1]) == {"ok": True}
    await client.close()


async def test_calls_outside_the_bridge_allow_list_are_refused() -> None:
    client = SupportOdooClient("http://127.0.0.1:9", "db", "key")
    for model, method in (
        ("account.move", "search_read"),
        ("helpdesk.ticket", "unlink"),
        # ratings are read only (the server action writes them)
        ("rating.rating", "write"),
        ("rating.rating", "create"),
        # contacts are created through the server action; search_count is unused
        ("res.partner", "create"),
        ("res.partner", "write"),
        ("helpdesk.ticket", "search_count"),
    ):
        with pytest.raises(PermissionError):
            await client.call(model, method)
    await client.close()


async def test_an_unavailable_odoo_is_support_unavailable(server: TestServer) -> None:
    client = _client(server)
    with pytest.raises(SupportUnavailable) as exc:
        await client.call("helpdesk.ticket", "search_read", domain=["boom"])
    await client.close()
    assert isinstance(exc.value.__cause__, odoo.OdooUnavailable)


async def test_a_refusal_is_a_support_rejection_with_odoo_details(
    server: TestServer,
) -> None:
    client = _client(server)
    with pytest.raises(OdooRejected) as exc:
        await client.call("helpdesk.ticket", "search_read", domain=["denied"])
    await client.close()
    assert isinstance(exc.value, SupportRejected)
    assert isinstance(exc.value, odoo.OdooRejected)
    assert (exc.value.status, exc.value.name) == (403, "odoo.exceptions.AccessError")
