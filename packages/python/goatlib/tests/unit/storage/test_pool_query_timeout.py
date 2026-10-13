"""A timed-out pooled query whose thread ignores the interrupt.

DuckDB checks for an interrupt between steps of a query, so a query busy in
a single long step (here a Python UDF that blocks) keeps running after
`_execute_with_timeout` interrupts it and stops waiting. Its connection must
not go back to the pool while that thread still runs on it: a DuckDB
connection is not safe for concurrent use. The pool closes the busy one once
its query has ended; a pinned pool refills the slot from its base at once, an
unpinned one after the close.

Real in-memory DuckDB, no DuckLake catalog.
"""

import queue
import threading
import time
from typing import Any, Callable, Iterator

import duckdb
import pytest
from goatlib.storage.ducklake import DuckLakePool, QueryTimeoutError

BLOCKING_QUERY = "SELECT block_until_released(1)"


@pytest.fixture()
def released() -> Iterator[threading.Event]:
    event = threading.Event()
    yield event
    event.set()  # never leave a query thread blocked after a test


def add_blocking_udf(con: duckdb.DuckDBPyConnection, released: threading.Event) -> None:
    """A function that ignores interrupts until `released` is set."""

    def block_until_released(x: int) -> int:
        released.wait(10)
        return x

    con.create_function(
        "block_until_released", block_until_released, ["INTEGER"], "INTEGER"
    )


def pool_entries(p: DuckLakePool) -> list[tuple[Any, float, int]]:
    items = []
    while True:
        try:
            items.append(p._pool.get_nowait())
        except queue.Empty:
            break
    for it in items:
        p._pool.put(it)
    return items


def wait_until(condition: Callable[[], bool], deadline_s: float = 5.0) -> None:
    deadline = time.monotonic() + deadline_s
    while not condition():
        if time.monotonic() > deadline:
            pytest.fail("condition not reached before the deadline")
        time.sleep(0.02)


def is_closed(con: duckdb.DuckDBPyConnection) -> bool:
    try:
        con.execute("SELECT 1").fetchall()
    except duckdb.ConnectionException:
        return True
    return False


def time_out_blocking_query(p: DuckLakePool) -> tuple[Any, QueryTimeoutError]:
    """Run BLOCKING_QUERY past its timeout; return its cursor and the error."""
    (busy, _, _) = pool_entries(p)[0]
    with pytest.raises(QueryTimeoutError) as excinfo:
        p.execute_with_retry(BLOCKING_QUERY, timeout=0.05)
    return busy, excinfo.value


def running_thread(error: QueryTimeoutError) -> threading.Thread:
    thread = error.query_thread
    assert thread is not None and thread.is_alive(), "the query must still run"
    return thread


@pytest.fixture()
def pinned_pool(released: threading.Event) -> Iterator[DuckLakePool]:
    p = DuckLakePool(pool_size=1, pin_snapshot=True)
    base = duckdb.connect()
    add_blocking_udf(base, released)  # visible to every cursor of the base
    p._register_base(0, base)
    p._pool.put((base.cursor(), time.time(), 0))
    p._initialized = True
    yield p
    released.set()
    p.close()


def test_pinned_busy_cursor_is_replaced_not_reused(
    pinned_pool: DuckLakePool, released: threading.Event
) -> None:
    busy, error = time_out_blocking_query(pinned_pool)

    entries = pool_entries(pinned_pool)
    assert len(entries) == 1
    assert all(e[0] is not busy for e in entries)
    thread = running_thread(error)

    # A fresh cursor of the same base serves the next request at once.
    with pinned_pool.connection() as con:
        assert con is not busy
        assert con.execute("SELECT 42").fetchall() == [(42,)]
    assert thread.is_alive()
    # The busy cursor still counts against its base while its query runs.
    assert pinned_pool._bases[0][1] == 2

    released.set()
    thread.join(5)
    wait_until(lambda: pinned_pool._bases[0][1] == 1)
    assert is_closed(busy)
    assert len(pool_entries(pinned_pool)) == 1


def test_pinned_busy_cursor_keeps_a_superseded_base_open(
    pinned_pool: DuckLakePool,
    released: threading.Event,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_base = pinned_pool._bases[0][0]
    monkeypatch.setattr(
        pinned_pool,
        "_create_base_with_retry",
        lambda snapshot_version=None: duckdb.connect(),
    )
    # Probing the base while the waiter closes it would be concurrent use of
    # one connection: wait for the pool's own close to return instead.
    closed_bases: list[duckdb.DuckDBPyConnection] = []
    close_base = pinned_pool._close_base

    def record_close(base: duckdb.DuckDBPyConnection) -> None:
        close_base(base)
        closed_bases.append(base)

    monkeypatch.setattr(pinned_pool, "_close_base", record_close)
    busy, error = time_out_blocking_query(pinned_pool)
    assert all(e[0] is not busy for e in pool_entries(pinned_pool))
    thread = running_thread(error)

    pinned_pool._apply_snapshot(11)  # a rebuild supersedes the busy cursor's base
    assert 0 in pinned_pool._bases, "the base must outlive its running query"
    entries = pool_entries(pinned_pool)
    assert len(entries) == 1
    assert all(e[2] == pinned_pool._generation for e in entries)

    released.set()
    thread.join(5)
    # The waiter closes the cursor, then the base it held open.
    wait_until(lambda: any(b is old_base for b in closed_bases))
    assert is_closed(old_base)
    assert 0 not in pinned_pool._bases
    assert is_closed(busy)


def test_unpinned_busy_connection_is_replaced_once_closed(
    released: threading.Event, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unpinned connections each carry their own memory budget, so the busy
    one's slot is refilled only after it has closed."""
    p = DuckLakePool(pool_size=2)
    busy = duckdb.connect()
    add_blocking_udf(busy, released)
    other = duckdb.connect()
    p._pool.put((busy, time.time(), 0))  # first out: runs the blocking query
    p._pool.put((other, time.time(), 0))
    p._initialized = True
    created: list[duckdb.DuckDBPyConnection] = []

    def fake_create(**_: Any) -> duckdb.DuckDBPyConnection:
        con = duckdb.connect()
        created.append(con)
        return con

    monkeypatch.setattr(p, "_create_connection_with_retry", fake_create)
    try:
        _, error = time_out_blocking_query(p)

        entries = pool_entries(p)
        assert all(e[0] is not busy for e in entries)
        assert [e[0] for e in entries] == [other]
        thread = running_thread(error)
        with p.connection() as con:
            assert con.execute("SELECT 42").fetchall() == [(42,)]
        assert thread.is_alive()
        assert created == []

        released.set()
        thread.join(5)
        wait_until(lambda: len(pool_entries(p)) == 2)
        assert is_closed(busy)
        assert {id(e[0]) for e in pool_entries(p)} == {id(other), id(created[0])}
    finally:
        released.set()
        p.close()


def test_query_that_stops_within_the_grace_keeps_its_cursor(
    pinned_pool: DuckLakePool, released: threading.Event
) -> None:
    """A query that stops before the pool stops waiting leaves its cursor
    free: the cursor goes back to the pool as after any other query."""
    (cursor, _, _) = pool_entries(pinned_pool)[0]
    timer = threading.Timer(0.3, released.set)
    timer.start()
    try:
        with pytest.raises(QueryTimeoutError):
            pinned_pool.execute_with_retry(BLOCKING_QUERY, timeout=0.05)
    finally:
        timer.cancel()
    assert released.is_set()

    entries = pool_entries(pinned_pool)
    assert len(entries) == 1 and entries[0][0] is cursor
    assert pinned_pool._bases[0][1] == 1
    with pinned_pool.connection() as con:
        assert con.execute("SELECT 42").fetchall() == [(42,)]
