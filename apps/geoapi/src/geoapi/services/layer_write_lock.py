"""The per-layer write lock and the serial high-water marks it guards.

A serial number is one past the larger of the highest number in the layer and
the highest number ever handed out (its high-water mark), so two creates that
read those at the same time hand out the same number. Within one pod the
DuckLake write manager's ``threading.Lock`` already runs writes one after the
other; across pods nothing did — DuckLake lets two transactions append to the
same table without a conflict, so both commits succeed.

The lock is a Postgres advisory lock keyed by the layer, taken with
``pg_advisory_xact_lock`` inside a transaction on one pooled connection:

- Postgres is the one thing every geoapi pod already shares, and the lock costs
  no table, row or migration of its own.
- The transaction-scoped form is released by the server when the transaction
  ends, including when the pod dies mid-write, so a crash cannot leave a layer
  locked. It also works through a transaction pooler, where a session-level
  lock could be released on a connection another client then gets.
- It is held until the DuckLake write has committed, so the next writer's
  ``max`` already sees this writer's rows.

The high-water marks live in core's ``customer.layer_serial_counter`` (one row
per layer and serial column) and are read and advanced in that same
transaction: read after the lock is taken, written back — only ever upwards —
after the rows are in. If the DuckLake write fails, nothing is written back;
if the write-back fails after DuckLake committed, the rows themselves still
carry the numbers, so ``max`` covers them until the next write moves the mark.
A table rather than ``field_config``, because a counter that moves on every
create should not rewrite the column definitions each time, and because the
foreign key drops it with its layer.

Every feature create and update takes the lock and reads the layer's
``field_config`` under it (``locked_layer_write``), because an existing column
can be turned into a serial at any time and a write must not slip a typed-in
number past that conversion. The bundle editor and the add-column backfill
decide up front (``layer_write_lock``): a bundle member's columns cannot be
converted, and a column being added has no writer yet. A UUID needs no
coordination of its own. Without a Postgres pool (tests, a bare dev run) there
is a single process, its write manager's lock is the whole guarantee, and there
is no mark: numbers continue from ``max``.
"""

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, AsyncIterator, Iterable
from uuid import UUID

import asyncpg
from goatlib.utils.generated_fields import (
    SerialCounters,
    generated_fields,
    needs_write_lock,
)
from goatlib.utils.layer_lock import LAYER_LOCK_NAMESPACE, layer_lock_key

from geoapi.services.computed_columns import fetch_field_config
from geoapi.services.layer_service import layer_service

logger = logging.getLogger(__name__)

#: The lock key's namespace and spelling live in goatlib, so "Update dataset"
#: and the workflow's "Append to dataset" node take the very same lock.
LOCK_NAMESPACE = LAYER_LOCK_NAMESPACE
_lock_key = layer_lock_key

COUNTER_TABLE = "customer.layer_serial_counter"


async def _lock(conn: Any, layer_id: str) -> None:
    await conn.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended($1, 0))", _lock_key(layer_id)
    )


async def _read_marks(conn: Any, layer_id: str, names: list[str]) -> dict[str, int]:
    """The stored marks of these columns; none for a column that has no row."""
    try:
        async with conn.transaction():
            rows = await conn.fetch(
                f"SELECT field_name, last_value FROM {COUNTER_TABLE} "
                "WHERE layer_id = $1::uuid AND field_name = ANY($2::text[])",
                layer_id,
                names,
            )
    except asyncpg.UndefinedTableError:
        # Core's migration has not run yet: numbers continue from max.
        logger.warning("%s is missing; serial numbers fall back to max", COUNTER_TABLE)
        return {}
    return {row["field_name"]: int(row["last_value"]) for row in rows}


async def _advance_marks(conn: Any, layer_id: str, assigned: dict[str, int]) -> None:
    """Store the highest numbers handed out; a mark never moves down."""
    try:
        async with conn.transaction():
            await conn.executemany(
                f"INSERT INTO {COUNTER_TABLE} AS c "
                "(layer_id, field_name, last_value, updated_at) "
                "VALUES ($1::uuid, $2, $3, now()) "
                "ON CONFLICT (layer_id, field_name) DO UPDATE SET "
                "last_value = greatest(c.last_value, excluded.last_value), "
                "updated_at = now()",
                [(layer_id, name, value) for name, value in assigned.items()],
            )
    except asyncpg.UndefinedTableError:
        logger.warning(
            "%s is missing; serial high-water mark not stored", COUNTER_TABLE
        )


async def _forget_marks(conn: Any, layer_id: str, names: Iterable[str]) -> None:
    names = list(names)
    if not names:
        return
    try:
        async with conn.transaction():
            await conn.execute(
                f"DELETE FROM {COUNTER_TABLE} "
                "WHERE layer_id = $1::uuid AND field_name = ANY($2::text[])",
                layer_id,
                names,
            )
    except asyncpg.UndefinedTableError:
        pass


@asynccontextmanager
async def layer_write_lock(
    layer_id: str,
    field_config: dict[str, Any] | None,
    *,
    reset: Iterable[str] = (),
    pool: Any = None,
) -> AsyncIterator[SerialCounters]:
    """Hold the layer's write lock while the body writes, if it needs one.

    Yields the serial counters: their ``high_water`` is what the table held,
    and whatever the body records in ``assigned`` is stored back before the
    lock is released. ``reset`` forgets the marks of those columns first — a
    column that has just been added starts over, whatever a dropped column of
    the same name once handed out. ``pool`` defaults to the service's own.
    """
    counters = SerialCounters()
    pool = pool if pool is not None else layer_service._pool
    fields = generated_fields(field_config)
    if pool is None or not needs_write_lock(fields):
        yield counters
        return
    serials = [f.name for f in fields if f.kind == "serial"]
    async with pool.acquire() as conn:
        async with conn.transaction():
            await _lock(conn, layer_id)
            await _forget_marks(conn, layer_id, reset)
            counters.high_water = await _read_marks(conn, layer_id, serials)
            yield counters
            if counters.assigned:
                await _advance_marks(conn, layer_id, counters.assigned)


@dataclass
class LayerWrite:
    """What a feature write needs to know, read while it holds the lock.

    ``field_config`` is read on the lock's own connection after the lock is
    taken, so it is the definition the write is serialized against: a column
    turned into a serial a moment ago is already a serial here. ``conn`` is
    that connection (``None`` without a pool), for anything the write has to
    store before the lock is released — on the same connection, because a
    second one from the pool could wait on writers that hold the others while
    they wait for this lock.
    """

    field_config: dict[str, Any]
    counters: SerialCounters = dataclass_field(default_factory=SerialCounters)
    conn: Any = None


@asynccontextmanager
async def locked_layer_write(
    layer_id: str,
    *,
    reset: Iterable[str] = (),
    pool: Any = None,
) -> AsyncIterator[LayerWrite]:
    """Hold the layer's write lock for any feature write, and read under it.

    Unlike ``layer_write_lock`` this always takes the lock, whatever the layer
    declares, and reads ``field_config`` only once it holds it. That closes the
    one gap a lock decided up front leaves: an existing column can be turned
    into a serial (``update_column``), and a create or update that had read the
    old definition before the conversion would otherwise write a typed-in —
    possibly duplicate — number after the conversion checked the column. With
    both sides under one lock, a write either finished before the conversion
    looked, or sees the serial.

    The cost is one advisory lock per create or update; writes to one layer
    were already serialized within a pod.
    """
    pool = pool if pool is not None else layer_service._pool
    if pool is None:
        yield LayerWrite(field_config={})
        return
    async with pool.acquire() as conn:
        async with conn.transaction():
            await _lock(conn, layer_id)
            await _forget_marks(conn, layer_id, reset)
            field_config = await fetch_field_config(conn, UUID(layer_id))
            write = LayerWrite(field_config=field_config, conn=conn)
            serials = [
                f.name for f in generated_fields(field_config) if f.kind == "serial"
            ]
            if serials:
                write.counters.high_water = await _read_marks(conn, layer_id, serials)
            yield write
            if write.counters.assigned:
                await _advance_marks(conn, layer_id, write.counters.assigned)


async def forget_serial_counter(layer_id: str, name: str) -> None:
    """Drop a column's mark: the column is gone, or is about to start over."""
    pool = layer_service._pool
    if pool is None:
        return
    async with pool.acquire() as conn:
        async with conn.transaction():
            await _lock(conn, layer_id)
            await _forget_marks(conn, layer_id, [name])


async def rename_serial_counter(layer_id: str, old: str, new: str) -> None:
    """Move a column's mark to its new name.

    A rename is the same column, so it keeps its numbering; a column later
    added under the old name has no mark and starts over.
    """
    pool = layer_service._pool
    if pool is None:
        return
    async with pool.acquire() as conn:
        async with conn.transaction():
            await _lock(conn, layer_id)
            await _forget_marks(conn, layer_id, [new])
            try:
                async with conn.transaction():
                    await conn.execute(
                        f"UPDATE {COUNTER_TABLE} SET field_name = $3, updated_at = now() "
                        "WHERE layer_id = $1::uuid AND field_name = $2",
                        layer_id,
                        old,
                        new,
                    )
            except asyncpg.UndefinedTableError:
                pass
