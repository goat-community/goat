"""PostgreSQL sessions held by the DuckLake managers and pools.

A DuckDB result that is not read to the end keeps its transaction open, and
with it the transaction of every catalog connection the query used: the server
shows those sessions as `idle in transaction` until the next statement runs on
that DuckDB connection. DuckDB also caches catalog connections per attach.
These tests pin down that the managers leave no transaction open and keep only
as many catalog connections as they can use at once.

Run explicitly with:
    uv run pytest tests/integration/test_ducklake_pg_sessions.py -m integration -v
"""

import time
import uuid
from typing import Any, Callable

import duckdb
import pytest
from goatlib.storage import BaseDuckLakeManager, DuckLakePool
from goatlib.storage.ducklake import execute_with_retry, fetch_one

pytestmark = pytest.mark.integration

COUNT = "SELECT count(*) FROM lake.main.t_first"

States = Callable[[str], list[str]]


def _application_name() -> str:
    return f"goat-test-{uuid.uuid4().hex[:8]}"


def _settle() -> None:
    """Let pg_stat_activity catch up with the backends' last state change."""
    time.sleep(0.3)


def test_pinned_manager_leaves_no_transaction_open(
    lake_env: tuple[Any, BaseDuckLakeManager], pg_session_states: States
) -> None:
    settings, _ = lake_env
    name = _application_name()
    manager = BaseDuckLakeManager(
        read_only=True, pin_snapshot=True, refresh_interval=0.2, application_name=name
    )
    manager.init(settings)
    try:
        time.sleep(0.6)  # a few snapshot polls
        # Warm-up and polls alone: no query has touched the connection yet.
        assert "idle in transaction" not in pg_session_states(name)

        assert manager.execute_one(COUNT) == (1,)
        with manager.connection() as con:
            assert con.execute(COUNT).fetchone() == (1,)
        _settle()

        states = pg_session_states(name)
        assert states, "no session carries the manager's application_name"
        assert "idle in transaction" not in states
    finally:
        manager.close()


def test_pinned_pool_leaves_no_transaction_open(
    lake_env: tuple[Any, BaseDuckLakeManager], pg_session_states: States
) -> None:
    settings, _ = lake_env
    name = _application_name()
    pool = DuckLakePool(
        pool_size=2, pin_snapshot=True, refresh_interval=0.2, application_name=name
    )
    pool.init(settings)
    try:
        time.sleep(0.6)  # a few snapshot polls
        assert pool.execute_with_retry(COUNT, fetch_all=False) == (1,)
        assert execute_with_retry(pool, COUNT, fetch_all=False)[0] == (1,)
        for _ in range(2):  # reach both cursors
            with pool.connection() as con:
                assert con.execute(COUNT).fetchone() == (1,)
        _settle()

        states = pg_session_states(name)
        assert states, "no session carries the pool's application_name"
        assert "idle in transaction" not in states
    finally:
        pool.close()


def test_unrelated_timeout_still_releases_the_result(
    lake_env: tuple[Any, BaseDuckLakeManager], pg_session_states: States
) -> None:
    """Only the pool's own query timeout skips the release; a socket or
    HTTP timeout raised while a cursor is checked out must not."""
    settings, _ = lake_env
    name = _application_name()
    pool = DuckLakePool(
        pool_size=1, pin_snapshot=True, refresh_interval=999.0, application_name=name
    )
    pool.init(settings)
    try:
        with pytest.raises(TimeoutError):
            with pool.connection() as con:
                assert con.execute(COUNT).fetchone() == (1,)
                raise TimeoutError("an unrelated socket timeout")
        _settle()

        assert "idle in transaction" not in pg_session_states(name)
    finally:
        pool.close()


def test_fetch_one_leaves_no_transaction_open(
    lake_env: tuple[Any, BaseDuckLakeManager], pg_session_states: States
) -> None:
    """A connection no manager takes back, as a tool run holds its own."""
    settings, _ = lake_env
    name = _application_name()
    manager = BaseDuckLakeManager(read_only=True, application_name=name)
    manager.init(settings)
    con = duckdb.connect()
    try:
        manager.attach_catalog(con)
        assert fetch_one(con, COUNT) == (1,)
        _settle()

        states = pg_session_states(name)
        assert states, "no session carries the attach's application_name"
        assert "idle in transaction" not in states
    finally:
        con.close()
        manager.close()


def _cached_catalog_connections(con: Any, catalog: str) -> int:
    """The most catalog connections DuckDB keeps cached for an attached catalog."""
    row = con.execute(
        f"SELECT max_connections FROM postgres_configure_pool(catalog_name='{catalog}')"
    ).fetchall()
    return row[0][0]


def test_attaches_cache_only_the_catalog_connections_they_use(
    lake_env: tuple[Any, BaseDuckLakeManager],
) -> None:
    settings, _ = lake_env
    settings.DUCKDB_THREADS = 2
    manager = BaseDuckLakeManager(read_only=True, pin_snapshot=True)
    pool = DuckLakePool(pool_size=3, pin_snapshot=True)
    manager.init(settings)
    pool.init(settings)
    try:
        # DuckLake reaches its catalog through this internal postgres attach;
        # one query reads it on up to one connection per thread, plus one.
        metadata = "__ducklake_metadata_lake"
        with manager.connection() as con:
            assert _cached_catalog_connections(con, metadata) == 2 + 1
        with pool.connection() as con:
            # The shared base runs the threads of all three cursors.
            assert _cached_catalog_connections(con, metadata) == 2 * 3 + 1
        assert manager._poll_con is not None
        assert _cached_catalog_connections(manager._poll_con, "pincat") == 1
    finally:
        pool.close()
        manager.close()
