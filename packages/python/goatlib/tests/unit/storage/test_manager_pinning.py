"""BaseDuckLakeManager pinning logic with stubbed connection creation."""

import time
from typing import Any

import pytest
from goatlib.storage.ducklake import BaseDuckLakeManager


class FakeCon:
    def __init__(self, snapshot: int | None) -> None:
        self.snapshot = snapshot
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def execute(self, *_: Any) -> "FakeCon":
        return self

    def fetchone(self) -> tuple[int]:
        return (1,)

    def fetchall(self) -> list[tuple[int]]:
        return [(1,)]


@pytest.fixture()
def manager(monkeypatch: pytest.MonkeyPatch) -> BaseDuckLakeManager:
    m = BaseDuckLakeManager(read_only=True, pin_snapshot=True)

    def fake_build(snapshot_version: int | None = None) -> FakeCon:
        return FakeCon(snapshot_version)

    monkeypatch.setattr(m, "_build_connection", fake_build)
    monkeypatch.setattr(m, "_warm_connection", lambda con: None)
    monkeypatch.setattr(m, "_fetch_latest_snapshot_id", lambda: 10)
    m._connection = fake_build(9)  # type: ignore[assignment]
    return m


def test_apply_snapshot_swaps_connection(manager: BaseDuckLakeManager) -> None:
    old = manager._connection
    manager._apply_snapshot(10)
    assert manager._connection is not old
    assert manager._connection.snapshot == 10  # type: ignore[union-attr]
    assert old.closed  # type: ignore[union-attr]


def test_pinned_manager_skips_inline_stale_recycle(
    manager: BaseDuckLakeManager,
) -> None:
    manager._created_at = 1.0  # ancient: stale by any margin
    before = manager._connection
    with manager.connection() as con:
        assert con is before  # no inline recycle when pinned


def test_pinned_maintain_recycles_aged_connection(
    manager: BaseDuckLakeManager,
) -> None:
    from goatlib.storage.snapshot_pin import SnapshotPin

    manager._pin = SnapshotPin(
        manager._fetch_latest_snapshot_id,
        manager._apply_snapshot,
    )
    manager._pin._current = 9

    manager._created_at = 1.0  # aged out
    old = manager._connection
    manager._recycle_aged()
    assert manager._connection is not old
    assert manager._connection.snapshot == 9  # type: ignore[union-attr]
    assert old.closed  # type: ignore[union-attr]
    assert manager._created_at > time.time() - 5

    # Young connection: no-op (fresh _created_at from the swap above).
    current = manager._connection
    manager._recycle_aged()
    assert manager._connection is current


def test_recycle_aged_warm_failure_keeps_old_connection(
    manager: BaseDuckLakeManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager._created_at = 1.0  # aged out
    old = manager._connection

    built: list[FakeCon] = []

    def fake_build(snapshot_version: int | None = None) -> FakeCon:
        con = FakeCon(snapshot_version)
        built.append(con)
        return con

    def failing_warm(con: FakeCon) -> None:
        raise RuntimeError("warm failed")

    monkeypatch.setattr(manager, "_build_connection", fake_build)
    monkeypatch.setattr(manager, "_warm_connection", failing_warm)

    with pytest.raises(RuntimeError, match="warm failed"):
        manager._recycle_aged()
    assert manager._connection is old  # old connection keeps serving
    assert not old.closed  # type: ignore[union-attr]
    assert built[0].closed  # fresh connection not leaked


def test_recycle_aged_discards_late_replacement(
    manager: BaseDuckLakeManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A force_refresh rebuild that lands mid-maintain-build must win."""
    manager._created_at = 1.0  # aged out
    old = manager._connection

    built: list[FakeCon] = []

    def build_and_race(snapshot_version: int | None = None) -> FakeCon:
        con = FakeCon(snapshot_version)
        built.append(con)
        # Simulate _apply_snapshot swapping in a newer pin mid-build.
        manager._connection = FakeCon(10)  # type: ignore[assignment]
        return con

    monkeypatch.setattr(manager, "_build_connection", build_and_race)
    manager._recycle_aged()
    assert manager._connection.snapshot == 10  # type: ignore[union-attr]
    assert not manager._connection.closed  # type: ignore[union-attr]
    assert old is not manager._connection
    assert built[0].closed  # late replacement discarded, not leaked


def test_force_pin_refresh_unpinned_returns_false() -> None:
    m = BaseDuckLakeManager(read_only=True)
    assert m.force_pin_refresh() is False


def test_fetch_latest_snapshot_id_installs_postgres_before_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A fresh poll connection must INSTALL postgres before LOAD postgres —
    on a clean container this is the first DuckDB call of the process and
    must not rely on autoinstall-on-LOAD."""
    m = BaseDuckLakeManager(read_only=True, pin_snapshot=True)
    m._catalog_schema = "ducklake"
    m._postgres_uri = "postgresql://u:p@localhost/db"

    executed: list[str] = []

    class FakePollConn:
        def execute(self, sql: str, *_: Any) -> "FakePollConn":
            executed.append(sql)
            return self

        def fetchall(self) -> list[tuple[int]]:
            return [(5,)]

        def close(self) -> None:
            pass

    import goatlib.storage.ducklake as ducklake_module

    monkeypatch.setattr(ducklake_module.duckdb, "connect", lambda: FakePollConn())

    assert m._fetch_latest_snapshot_id() == 5
    assert executed[0] == "INSTALL postgres"
    assert executed[1] == "LOAD postgres"


def test_execute_with_retry_pin_miss_refresh(
    manager: BaseDuckLakeManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    from goatlib.storage.snapshot_pin import SnapshotPin

    manager._pin = SnapshotPin(
        manager._fetch_latest_snapshot_id,
        manager._apply_snapshot,
        min_refresh_gap=0.0,
    )
    manager._pin._current = 9

    calls = {"n": 0}

    def fake_execute(query: str, params: Any = None) -> list[tuple[int]]:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("Catalog Error: Table with name t_x does not exist!")
        return [(42,)]

    monkeypatch.setattr(manager, "execute", fake_execute)
    assert manager.execute_with_retry("SELECT 1") == [(42,)]
    assert calls["n"] == 2
    assert manager._pin.current == 10


class TestDirectPgUri:
    """DuckLake attaches prefer DUCKLAKE_POSTGRES_DATABASE_URI (direct PG,
    bypassing the transaction pooler); absent -> app-wide URI unchanged."""

    class _Base:
        POSTGRES_DATABASE_URI = "postgresql://u:p@pooler:5432/goat"
        DUCKLAKE_CATALOG_SCHEMA = "ducklake"
        DUCKLAKE_DATA_DIR = "/tmp/lake"
        DUCKLAKE_S3_ENDPOINT = None
        DUCKLAKE_S3_BUCKET = None
        DUCKLAKE_S3_ACCESS_KEY = None
        DUCKLAKE_S3_SECRET_KEY = None

    def test_manager_prefers_ducklake_uri(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class S(self._Base):
            DUCKLAKE_POSTGRES_DATABASE_URI = "postgresql://u:p@primary:5432/goat"

        m = BaseDuckLakeManager(read_only=True)
        monkeypatch.setattr(m, "_create_connection", lambda *a, **k: None)
        m.init(S())
        assert m._postgres_uri == "postgresql://u:p@primary:5432/goat"

    def test_manager_falls_back_without_ducklake_uri(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        m = BaseDuckLakeManager(read_only=True)
        monkeypatch.setattr(m, "_create_connection", lambda *a, **k: None)
        m.init(self._Base())
        assert m._postgres_uri == "postgresql://u:p@pooler:5432/goat"

    def test_pool_prefers_ducklake_uri(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from goatlib.storage.ducklake import DuckLakePool

        class S(self._Base):
            DUCKLAKE_POSTGRES_DATABASE_URI = "postgresql://u:p@primary:5432/goat"

        p = DuckLakePool(pool_size=1)
        monkeypatch.setattr(
            p,
            "_create_connection_with_retry",
            lambda *a, **k: type("C", (), {"close": lambda self: None})(),
        )
        p.init(S())
        assert p._postgres_uri == "postgresql://u:p@primary:5432/goat"
