"""The per-layer write lock shared by geoapi's feature writes, "Update
dataset" and the workflow's "Append to dataset" node."""

import asyncio
from typing import Any

import pytest
from goatlib.tools.append_rows import (
    LAYER_LOCK_NAMESPACE,
    hold_layer_lock,
    layer_lock_key,
    lock_layer,
)

LAYER = "0A1B2C3D-0000-4000-8000-00000000ABCD"


def test_lock_key_matches_geoapi_spelling() -> None:
    assert LAYER_LOCK_NAMESPACE == "goat.layer_serial:"
    assert layer_lock_key(LAYER) == "goat.layer_serial:0a1b2c3d00004000800000000000abcd"


class _Tx:
    def __init__(self, log: list[str]) -> None:
        self.log = log

    async def __aenter__(self) -> None:
        self.log.append("begin")

    async def __aexit__(self, *exc: Any) -> None:
        self.log.append("rollback" if exc[0] else "commit")


class _Conn:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.log: list[str] = []

    async def execute(self, sql: str, *args: Any) -> None:
        self.calls.append((sql, args))
        self.log.append("lock")

    def transaction(self) -> _Tx:
        return _Tx(self.log)

    async def close(self) -> None:
        self.log.append("close")


def test_lock_layer_uses_xact_lock() -> None:
    conn = _Conn()
    asyncio.run(lock_layer(conn, LAYER))
    assert conn.calls == [
        (
            "SELECT pg_advisory_xact_lock(hashtextextended($1, 0))",
            (layer_lock_key(LAYER),),
        )
    ]


def test_hold_layer_lock_spans_the_block() -> None:
    conn = _Conn()

    async def connect() -> _Conn:
        return conn

    loop = asyncio.new_event_loop()
    try:
        with hold_layer_lock(connect, LAYER, loop):
            conn.log.append("write")
    finally:
        loop.close()
    assert conn.log == ["begin", "lock", "write", "commit", "close"]


def test_hold_layer_lock_releases_on_error() -> None:
    conn = _Conn()

    async def connect() -> _Conn:
        return conn

    loop = asyncio.new_event_loop()
    try:
        with pytest.raises(RuntimeError):
            with hold_layer_lock(connect, LAYER, loop):
                raise RuntimeError("boom")
    finally:
        loop.close()
    assert conn.log == ["begin", "lock", "rollback", "close"]
