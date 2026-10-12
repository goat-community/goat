"""Resolve what a public dashboard may ask for from its published snapshot.

Two readers share one cached fetch of `customer.project_public.config`: the
searchable-layers config for layer-search, and the SQL scope for preview-sql —
the queries the dashboard's author saved in its widgets, and the layers the
published project contains.
"""

import json
import logging
import threading
import time
import uuid
from collections.abc import Callable
from typing import Any, TypedDict

import duckdb
from goatlib.storage import (
    cap_catalog_connections,
    configure_baked_extensions,
    uri_with_application_name,
)

from processes.config import settings

logger = logging.getLogger(__name__)

CONFIG_TTL_SECONDS = 30.0
MAX_LAYER_ENTRIES = 20
MAX_COLUMNS = 3
CACHE_MAX = 512


class SearchLayerSpec(TypedDict):
    layer_id: str
    columns: list[str]
    label_column: str | None
    limit: int


class PublicSqlScope(TypedDict):
    """What an anonymous preview-sql may run against a published project."""

    queries: set[str]
    layer_ids: set[str]


def parse_search_config(config: dict[str, Any]) -> list[SearchLayerSpec]:
    """Extract searchable-layer specs from a project_public.config snapshot."""
    search = (
        config.get("project", {})
        .get("builder_config", {})
        .get("settings", {})
        .get("search")
        or {}
    )
    entries = search.get("layers") or []
    uuid_by_project_layer = {
        layer.get("id"): layer.get("layer_id") for layer in config.get("layers") or []
    }

    specs: list[SearchLayerSpec] = []
    for entry in entries[:MAX_LAYER_ENTRIES]:
        layer_uuid = uuid_by_project_layer.get(entry.get("layer_project_id"))
        columns = [c for c in (entry.get("columns") or []) if isinstance(c, str)]
        if not layer_uuid or not columns:
            continue
        limit = entry.get("limit")
        valid_limit = (
            isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 10
        )
        specs.append(
            SearchLayerSpec(
                layer_id=str(layer_uuid),
                columns=columns[:MAX_COLUMNS],
                label_column=entry.get("label_column"),
                limit=int(limit) if valid_limit else 5,
            )
        )
    return specs


def _stored_sql_queries(node: Any, out: set[str]) -> None:
    """Collect every `sql_query` string anywhere under `node`.

    Widgets sit at varying depths of the builder config (pages, panels,
    nested widgets); the key is the contract, not the path.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "sql_query" and isinstance(value, str):
                out.add(value)
            else:
                _stored_sql_queries(value, out)
    elif isinstance(node, list):
        for item in node:
            _stored_sql_queries(item, out)


def parse_sql_scope(config: dict[str, Any]) -> PublicSqlScope:
    """The saved widget queries and layer ids of a project_public.config snapshot."""
    queries: set[str] = set()
    _stored_sql_queries(config.get("project", {}).get("builder_config") or {}, queries)
    layer_ids = {
        str(layer["layer_id"])
        for layer in config.get("layers") or []
        if isinstance(layer, dict) and layer.get("layer_id")
    }
    return PublicSqlScope(queries=queries, layer_ids=layer_ids)


_lock = threading.Lock()
_fetch_lock = threading.Lock()
# Keyed by "<kind>:<project uuid>", one entry per reader of the snapshot.
_cache: dict[str, tuple[float, Any]] = {}
_con: duckdb.DuckDBPyConnection | None = None


def _reset_connection() -> None:
    """Drop the cached connection, closing it so its fds aren't leaked.

    Called on every DuckDB error, so a flapping Postgres would otherwise leak
    one handle per failure.
    """
    global _con
    con, _con = _con, None
    if con is not None:
        try:
            con.close()
        except Exception:  # noqa: BLE001 - a dead connection is what we're discarding
            logger.debug("Discarding a DuckDB connection that failed to close")


def _get_connection() -> duckdb.DuckDBPyConnection:
    global _con
    if _con is None:
        con = duckdb.connect()
        if not configure_baked_extensions(con):
            con.execute("INSTALL postgres;")
        con.execute("LOAD postgres;")
        cap_catalog_connections(con, 1)
        uri = uri_with_application_name(
            settings.POSTGRES_DATABASE_URI, "goat-processes"
        )
        con.execute(f"ATTACH '{uri}' AS pubcfg (TYPE postgres, READ_ONLY)")
        _con = con
    return _con


def _fetch_config(project_id: uuid.UUID) -> dict[str, Any] | None:
    con = _get_connection()
    # postgres_query takes a SQL literal; project_id is a validated UUID.
    # Read to the end: an unread result keeps the attach's transaction open.
    rows = con.execute(
        "SELECT * FROM postgres_query('pubcfg', "
        f"'SELECT config::text AS config FROM customer.project_public "
        f"WHERE project_id = ''{project_id}''')"
    ).fetchall()
    return json.loads(rows[0][0]) if rows else None


def _cache_get(key: str, now: float) -> Any | None:
    with _lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < CONFIG_TTL_SECONDS:
            return cached[1]
    return None


def _evict_for_insert(now: float) -> None:
    """Make room in `_cache` for a new key. Caller holds `_lock`."""
    expired = [k for k, (ts, _) in _cache.items() if now - ts >= CONFIG_TTL_SECONDS]
    for k in expired:
        del _cache[k]
    if len(_cache) >= CACHE_MAX:
        oldest_key = min(_cache, key=lambda k: _cache[k][0])
        del _cache[oldest_key]


def _cache_put(key: str, now: float, value: Any) -> Any:
    with _lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < CONFIG_TTL_SECONDS:
            return cached[1]
        if key not in _cache and len(_cache) >= CACHE_MAX:
            _evict_for_insert(now)
        _cache[key] = (now, value)
        return value


def _cached_snapshot_read(
    kind: str, project_id: str, parse: Callable[[dict[str, Any] | None], Any]
) -> Any:
    """`parse(snapshot)` for a published project, TTL-cached per process.

    Cache reads take a short lock so one slow fetch never blocks lookups for
    other keys; the Postgres fetch itself is serialized on `_fetch_lock`
    since the underlying DuckDB connection is not thread-safe.
    """
    pid = uuid.UUID(project_id)
    key = f"{kind}:{pid}"

    cached = _cache_get(key, time.monotonic())
    if cached is not None:
        return cached

    with _fetch_lock:
        try:
            config = _fetch_config(pid)
        except duckdb.Error:
            _reset_connection()  # reconnect on next call (e.g. stale PG connection)
            raise
        value = parse(config)

    return _cache_put(key, time.monotonic(), value)


def get_public_search_layers(project_id: str) -> list[SearchLayerSpec]:
    """Searchable-layer specs for a published project."""
    specs: list[SearchLayerSpec] = _cached_snapshot_read(
        "search",
        project_id,
        lambda config: parse_search_config(config) if config else [],
    )
    return specs


_UNPUBLISHED = object()


def get_public_sql_scope(project_id: str) -> PublicSqlScope | None:
    """The stored queries and layers of a published project; None if unpublished.

    Unpublished is cached too (as a sentinel), so a scan of random ids costs
    one Postgres round trip per id per TTL, not one per request.
    """
    value = _cached_snapshot_read(
        "sql",
        project_id,
        lambda config: parse_sql_scope(config) if config else _UNPUBLISHED,
    )
    return None if value is _UNPUBLISHED else value
