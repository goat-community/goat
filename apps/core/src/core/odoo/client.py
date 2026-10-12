"""Odoo JSON-2 client.

Every call must be in the caller's allow-list: each integration's Odoo user
already has narrow rights, and this keeps a bug in GOAT from turning into
"any call on any model" as well. Timeouts, refused connections, redirects and
5xx become OdooUnavailable; 4xx become OdooRejected with Odoo's error name.

A hanging Odoo must not tie up GOAT's requests (each holds a DB session while
it waits): waiting for a free connection slot is time-boxed, and after a few
consecutive failures a circuit breaker answers OdooUnavailable at once for a
while, then lets one probe call through (half-open). Slots and breaker are per
instance: each integration builds its own client with its own key.
"""

import asyncio
import json
import ssl
import time
from collections.abc import Callable, Collection
from typing import Any

import aiohttp
import certifi

from core.odoo.errors import OdooRejected, OdooUnavailable

Call = tuple[str, str]


def _ssl_context(ca_bundle: str | None) -> ssl.SSLContext:
    # The slim core image has no system CA store; certifi's bundle plus the
    # optional company CA (GOAT_CA_BUNDLE), like the SMTP client.
    context = ssl.create_default_context(cafile=certifi.where())
    if ca_bundle:
        context.load_verify_locations(cafile=ca_bundle)
    return context


class OdooClient:
    def __init__(
        self,
        url: str,
        db: str,
        api_key: str,
        *,
        allowed_calls: Collection[Call],
        upload_calls: Collection[Call] = (),
        ca_bundle: str | None = None,
        timeout: float = 10.0,
        upload_timeout: float = 120.0,
        max_concurrency: int = 10,
        acquire_timeout: float = 2.0,
        failure_threshold: int = 3,
        open_seconds: float = 30.0,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        """`upload_calls` carry files: they get `upload_timeout`, and a slow one
        says more about the file than about Odoo, so its timeout does not count
        towards the circuit breaker. `ca_bundle`: an extra CA file to trust.
        Nothing here reads GOAT's settings, so the module can move as it is."""
        self._url = url.rstrip("/")
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"bearer {api_key}",
            "X-Odoo-Database": db,
        }
        self._allowed = frozenset(allowed_calls)
        self._uploads = frozenset(upload_calls)
        self._ca_bundle = ca_bundle
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._upload_timeout = aiohttp.ClientTimeout(total=upload_timeout)
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._acquire_timeout = acquire_timeout
        self._session: aiohttp.ClientSession | None = None
        # circuit breaker
        self._failure_threshold = failure_threshold
        self._open_seconds = open_seconds
        self._now = now
        self._failures = 0
        self._open_until = 0.0
        self._probing = False

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                ssl=_ssl_context(self._ca_bundle)
                if self._url.startswith("https")
                else False
            )
            self._session = aiohttp.ClientSession(
                connector=connector, timeout=self._timeout
            )
        return self._session

    async def call(self, model: str, method: str, **kwargs: Any) -> Any:
        if (model, method) not in self._allowed:
            raise PermissionError(f"Odoo call {model}.{method} is not allowed")
        probe = self._enter_breaker(model, method)
        try:
            result = await self._call_with_slot(model, method, kwargs)
        except OdooUnavailable as exc:
            if exc.counts_for_breaker:
                self._record_failure()
            elif probe:
                self._probing = False
            raise
        except OdooRejected:
            self._record_success()  # Odoo answered: it is up
            raise
        except BaseException:
            # e.g. the caller went away: says nothing about Odoo, but a probe
            # must not stay "in flight" forever.
            if probe:
                self._probing = False
            raise
        self._record_success()
        return result

    def _record_success(self) -> None:
        self._failures = 0
        self._probing = False

    def _enter_breaker(self, model: str, method: str) -> bool:
        """Fail fast while the breaker is open; True when this call is the probe."""
        if self._failures < self._failure_threshold:
            return False
        if self._now() < self._open_until or self._probing:
            raise OdooUnavailable(f"Odoo {model}.{method}: circuit open")
        self._probing = True
        return True

    def _record_failure(self) -> None:
        self._failures += 1
        self._probing = False
        if self._failures >= self._failure_threshold:
            self._open_until = self._now() + self._open_seconds

    async def _call_with_slot(
        self, model: str, method: str, kwargs: dict[str, Any]
    ) -> Any:
        try:
            async with asyncio.timeout(self._acquire_timeout):
                await self._semaphore.acquire()
        except TimeoutError:
            # Every slot is busy: Odoo is slow. Not counted as a breaker
            # failure; the calls holding the slots count when they time out.
            raise OdooUnavailable(
                f"Odoo {model}.{method}: no free connection slot",
                counts_for_breaker=False,
            ) from None
        try:
            return await self._post(model, method, kwargs)
        finally:
            self._semaphore.release()

    async def _post(self, model: str, method: str, kwargs: dict[str, Any]) -> Any:
        upload = (model, method) in self._uploads
        try:
            async with self._get_session().post(
                f"{self._url}/json/2/{model}/{method}",
                data=json.dumps(kwargs),
                headers=self._headers,
                allow_redirects=False,
                timeout=self._upload_timeout if upload else self._timeout,
            ) as response:
                if response.status >= 500 or 300 <= response.status < 400:
                    raise OdooUnavailable(
                        f"Odoo {model}.{method}: HTTP {response.status}"
                    )
                if response.status >= 400:
                    try:
                        error = await response.json(content_type=None)
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        error = {}
                    if not isinstance(error, dict):
                        error = {}
                    raise OdooRejected(
                        response.status,
                        str(error.get("name", "")),
                        str(error.get("message", "")),
                    )
                try:
                    return await response.json(content_type=None)
                except ValueError as exc:
                    raise OdooUnavailable(
                        f"Odoo {model}.{method}: invalid JSON response"
                    ) from exc
        except TimeoutError as exc:
            raise OdooUnavailable(
                f"Odoo {model}.{method}: {exc!r}", counts_for_breaker=not upload
            ) from exc
        except aiohttp.ClientError as exc:
            raise OdooUnavailable(f"Odoo {model}.{method}: {exc!r}") from exc

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
