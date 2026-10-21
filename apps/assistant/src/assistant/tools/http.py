"""HTTP calls from tools to GOAT's services (spec §7.5, §8.3).

One client per service, bound to its base URL: a tool names a path, never a
host, so no tool can reach anything but core, geoapi, processes and catalog.
Every call carries the run's user token; the services check permissions as
they do for the web app (but see ``assistant.tools.project`` for the per-layer
gap). Errors become ``ToolFailed`` with a message the model can act on; server
internals of a 5xx are not passed on.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import unquote

import httpx
from pydantic_ai.exceptions import ToolFailed

from assistant.config import AssistantSettings
from assistant.tls import ssl_context

Service = Literal["core", "geoapi", "processes", "catalog"]

SERVICE_LABELS: dict[Service, str] = {
    "core": "GOAT core service",
    "geoapi": "GOAT data service",
    "processes": "GOAT analytics service",
    "catalog": "GOAT data catalog",
}

_DETAIL_CHARS = 300


def _message(service: Service, status: int, detail: str) -> str:
    label = SERVICE_LABELS[service]
    if status == 401:
        return f"The {label} did not accept the user's sign-in. The user may need to sign in again."
    if status == 403:
        return f"The user has no access to this in the {label}."
    if status == 404:
        return f"Not found in the {label}: {detail}"
    if status == 429 or status >= 500:
        return (
            f"The {label} is not available right now (HTTP {status}). Try again later."
        )
    if 300 <= status < 400:
        return f"The {label} answered with a redirect (HTTP {status}), which tools do not follow."
    return f"The {label} rejected the request (HTTP {status}): {detail}"


class ServiceError(ToolFailed):
    """A service answered with an error. ``status`` lets a tool turn a 404 into
    a message that names what was not found."""

    def __init__(self, service: Service, status: int, detail: str) -> None:
        self.service = service
        self.status = status
        self.detail = detail
        super().__init__(_message(service, status, detail))


def service_failed(exc: BaseException) -> bool:
    """Whether a call failed because a service did, not because of what it
    asked: the service answered 429 or a 5xx, did not answer in time, or
    could not be reached. Read from ``exc`` and what caused it (``raise ...
    from``), since a tool may put the failure in words of its own."""
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        if isinstance(current, ServiceError):
            return current.status == 429 or current.status >= 500
        if isinstance(current, httpx.HTTPError):
            return True
        seen.add(id(current))
        current = current.__cause__
    return False


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:_DETAIL_CHARS]
    if isinstance(body, dict):
        for key in ("detail", "description", "message"):
            value = body.get(key)
            if isinstance(value, dict):
                value = value.get("detail") or value.get("message") or json.dumps(value)
            if value:
                return str(value)[:_DETAIL_CHARS]
    return json.dumps(body)[:_DETAIL_CHARS]


def _query(params: Mapping[str, object] | None) -> dict[str, str] | None:
    if params is None:
        return None
    query: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            query[key] = "true" if value else "false"
        elif isinstance(value, (list, tuple)):
            query[key] = ",".join(str(item) for item in value)
        else:
            query[key] = str(value)
    return query


@dataclass
class ServiceClients:
    core: httpx.AsyncClient
    geoapi: httpx.AsyncClient
    processes: httpx.AsyncClient
    catalog: httpx.AsyncClient
    #: For refreshing a run's login (``assistant.login``); None with AUTH=False.
    keycloak: httpx.AsyncClient | None = None

    @classmethod
    def from_settings(cls, settings: AssistantSettings) -> "ServiceClients":
        timeout = httpx.Timeout(settings.tool_timeout_seconds, connect=5.0)
        # GOAT_CA_BUNDLE on top of the system CAs, for services and a Keycloak
        # behind a company CA; without it httpx's default verification.
        verify = ssl_context(settings.goat_ca_bundle)

        def client(base_url: str) -> httpx.AsyncClient:
            # No redirects: a service never sends a tool somewhere else.
            return httpx.AsyncClient(
                base_url=base_url.rstrip("/"),
                timeout=timeout,
                follow_redirects=False,
                verify=verify,
            )

        keycloak = (
            client(settings.keycloak_server_url)
            if settings.auth and settings.keycloak_server_url
            else None
        )
        return cls(
            core=client(settings.core_url),
            geoapi=client(settings.geoapi_url),
            processes=client(settings.processes_url),
            catalog=client(settings.catalog_url),
            keycloak=keycloak,
        )

    def client(self, service: Service) -> httpx.AsyncClient:
        by_service: dict[str, httpx.AsyncClient] = {
            "core": self.core,
            "geoapi": self.geoapi,
            "processes": self.processes,
            "catalog": self.catalog,
        }
        try:
            return by_service[service]
        except KeyError:
            raise ValueError(f"Unknown service {service!r}") from None

    async def aclose(self) -> None:
        for client in (
            self.core,
            self.geoapi,
            self.processes,
            self.catalog,
            self.keycloak,
        ):
            if client is not None:
                await client.aclose()


async def call_service(
    clients: ServiceClients,
    service: Service,
    method: str,
    path: str,
    *,
    bearer: str | None,
    params: Mapping[str, object] | None = None,
    json_body: object | None = None,
    headers: Mapping[str, str] | None = None,
) -> Any:
    """One request to a service; the decoded JSON body, or None for an empty one.

    ``headers`` are added to the request's (``Accept-Language``). An
    ``Authorization`` among them, in any spelling, is dropped, with a bearer or
    without one: only the run's own sign-in is sent."""
    # A path on the client's own service and nothing else: no host, no scheme,
    # no query or fragment (those go through ``params``), no control characters,
    # and no dot segments that would climb out of the intended route. Segments
    # are checked after percent-decoding, since a server decodes ``%2e%2e``
    # before it routes; other ``%XX`` escapes (quoted ids) stay allowed.
    if (
        not path.startswith("/")
        or path.startswith("//")
        or "://" in path
        or "?" in path
        or "#" in path
        or "\\" in path
        or not path.isprintable()
        or any(segment in (".", "..") for segment in unquote(path).split("/")[1:])
    ):
        raise ValueError(
            f"A tool may only name a path on its service, got {path[:80]!r}"
        )
    label = SERVICE_LABELS[service]
    # A caller's header never stands in for the run's sign-in, in any spelling.
    sent = {"Accept": "application/json"}
    sent.update(
        (name, value)
        for name, value in (headers or {}).items()
        if name.lower() != "authorization"
    )
    if bearer:
        sent["Authorization"] = f"Bearer {bearer}"
    try:
        response = await clients.client(service).request(
            method, path, params=_query(params), json=json_body, headers=sent
        )
    except httpx.InvalidURL as exc:
        raise ValueError(
            f"A tool may only name a path on its service, got {path[:80]!r}"
        ) from exc
    except httpx.TimeoutException as exc:
        raise ToolFailed(
            f"The {label} did not answer in time. Try a narrower request."
        ) from exc
    except httpx.HTTPError as exc:
        raise ToolFailed(f"The {label} is not reachable right now.") from exc
    # Redirects are not followed (``follow_redirects=False``); a 3xx is an error too.
    if response.status_code >= 300:
        raise ServiceError(service, response.status_code, _detail(response))
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise ToolFailed(f"The {label} sent an answer that is not JSON.") from exc
