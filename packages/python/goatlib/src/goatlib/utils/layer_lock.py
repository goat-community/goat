"""The per-layer write lock, shared by geoapi's feature writes and the
workflow's "Append to dataset" node.

Dependency-free on purpose: geoapi installs goatlib without its "full" extra.

A Postgres advisory lock keyed by the layer, taken with
``pg_advisory_xact_lock`` inside a transaction, so the server releases it when
the transaction ends, also when the worker dies mid-write.
"""

import asyncio
from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from typing import Any

#: Namespaces the advisory-lock key, so it cannot collide with another feature
#: that hashes a layer id into an advisory lock.
LAYER_LOCK_NAMESPACE = "goat.layer_serial:"


def layer_lock_key(layer_id: str) -> str:
    """The layer id in one spelling, whichever form the caller holds."""
    return LAYER_LOCK_NAMESPACE + layer_id.replace("-", "").lower()


async def lock_layer(conn: Any, layer_id: str) -> None:
    """Take the layer's write lock until the caller's transaction ends."""
    await conn.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended($1, 0))",
        layer_lock_key(layer_id),
    )


@contextmanager
def hold_layer_lock(
    connect: Callable[[], Awaitable[Any]],
    layer_id: str,
    loop: asyncio.AbstractEventLoop,
) -> Iterator[Any]:
    """Hold the layer's write lock around a block of synchronous tool code.

    Yields the dedicated connection whose transaction holds the lock, so the
    block can read and advance the layer's serial marks in that transaction.
    """
    conn = loop.run_until_complete(connect())
    try:
        tx = conn.transaction()
        loop.run_until_complete(tx.__aenter__())
        try:
            loop.run_until_complete(lock_layer(conn, layer_id))
            yield conn
        except BaseException as exc:
            loop.run_until_complete(tx.__aexit__(type(exc), exc, exc.__traceback__))
            raise
        loop.run_until_complete(tx.__aexit__(None, None, None))
    finally:
        loop.run_until_complete(conn.close())
