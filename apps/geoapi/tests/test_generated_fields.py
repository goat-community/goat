"""Generated columns (serial, uuid) through every per-feature write path.

Run against a real, file-backed DuckLake rather than a mock, because the
behaviour that matters is SQL behaviour: what ``max`` sees, whether rowids stay
put when a backfill rewrites rows, and whether a batch sees its own inserts.
The write manager is replaced by one connection behind a ``threading.Lock`` —
exactly what ``BaseDuckLakeManager`` gives a pod — so the concurrency tests
exercise the same serialization production relies on inside one process.
Cross-pod serialization is the advisory lock's job; it has its own tests.
"""

from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
from unittest.mock import patch

import duckdb
import pytest
from goatlib.utils.generated_fields import (
    GeneratedField,
    GeneratedValues,
    SerialCounters,
    generated_fields,
)

from geoapi.dependencies import LayerInfo
from geoapi.services.feature_write_service import FeatureWriteService

LAYER_ID = "abc123de-f456-7890-1234-5678901234ab"
POINT = {"type": "Point", "coordinates": [7.1, 50.7]}

SERIAL_CONFIG: dict[str, Any] = {
    "vorhaben_id": {
        "kind": "serial",
        "start": 1,
        "is_computed": False,
        "depends_on": [],
        "display_config": {},
    }
}
UUID_CONFIG: dict[str, Any] = {
    "uid": {
        "kind": "uuid",
        "is_computed": False,
        "depends_on": [],
        "display_config": {},
    }
}


class _LockedManager:
    """One connection behind one lock, like ``BaseDuckLakeManager``."""

    def __init__(self, con: duckdb.DuckDBPyConnection) -> None:
        self._con = con
        self._lock = threading.Lock()

    @contextmanager
    def connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        with self._lock:
            yield self._con


@pytest.fixture()
def lake(tmp_path: Path) -> Generator[duckdb.DuckDBPyConnection, None, None]:
    con = duckdb.connect(":memory:")
    con.execute("INSTALL spatial; LOAD spatial; INSTALL ducklake; LOAD ducklake;")
    con.execute(
        f"ATTACH 'ducklake:{tmp_path}/meta.ducklake' AS lake "
        f"(DATA_PATH '{tmp_path}/data')"
    )
    con.execute("CREATE SCHEMA lake.s")
    con.execute(
        "CREATE TABLE lake.s.t (geometry GEOMETRY, name VARCHAR, "
        "vorhaben_id BIGINT, uid VARCHAR, label VARCHAR)"
    )
    with patch(
        "geoapi.services.feature_write_service.ducklake_write_manager",
        _LockedManager(con),
    ):
        yield con
    con.close()


LAYER = LayerInfo(layer_id=LAYER_ID, schema_name="s", table_name="t")
COLUMNS = ["geometry", "name", "vorhaben_id", "uid", "label"]
SERVICE = FeatureWriteService()


class _CounterTable:
    """Stands in for core's ``layer_serial_counter`` and the advisory lock
    around it: a write reads the marks under the lock, and what it handed out
    is stored back — only ever upwards — before the lock is released."""

    def __init__(self) -> None:
        self.marks: dict[str, int] = {}
        self._lock = threading.Lock()

    @contextmanager
    def write(self) -> Generator[SerialCounters, None, None]:
        with self._lock:
            counters = SerialCounters(high_water=dict(self.marks))
            yield counters
            for name, value in counters.assigned.items():
                self.marks[name] = max(self.marks.get(name, value), value)


def _create(
    field_config: dict[str, Any],
    store: _CounterTable | None = None,
    layer: LayerInfo | None = None,
    **properties: Any,
) -> str:
    def create(counters: SerialCounters | None) -> str:
        return SERVICE.create_feature(
            layer_info=layer or LAYER,
            geometry=POINT,
            properties=properties,
            column_names=COLUMNS,
            geometry_column="geometry",
            field_config=field_config,
            serial_counters=counters,
        )

    if store is None:
        return create(None)
    with store.write() as counters:
        return create(counters)


def _serials(con: duckdb.DuckDBPyConnection) -> list[Any]:
    return [
        r[0]
        for r in con.execute(
            "SELECT vorhaben_id FROM lake.s.t ORDER BY rowid"
        ).fetchall()
    ]


def _value(con: duckdb.DuckDBPyConnection, feature_id: str, column: str) -> Any:
    row = con.execute(
        f'SELECT "{column}" FROM lake.s.t WHERE rowid = ?', [int(feature_id) - 1]
    ).fetchone()
    return row[0] if row else None


# --- next value ---------------------------------------------------------------


def test_an_empty_layer_starts_at_one(lake) -> None:
    _create(SERIAL_CONFIG, name="a")
    _create(SERIAL_CONFIG, name="b")
    assert _serials(lake) == [1, 2]


def test_an_empty_layer_starts_at_the_configured_start(lake) -> None:
    config = {"vorhaben_id": {**SERIAL_CONFIG["vorhaben_id"], "start": 1000}}
    _create(config)
    _create(config)
    assert _serials(lake) == [1000, 1001]


def test_numbering_continues_after_the_highest_existing_value(lake) -> None:
    """Values that predate the column's config (an import, a copy) are kept,
    and new ones continue after the highest — not after the row count."""
    lake.execute("INSERT INTO lake.s.t (name, vorhaben_id) VALUES ('x', 41), ('y', 7)")
    _create(SERIAL_CONFIG)
    assert _serials(lake) == [41, 7, 42]


def test_a_start_above_the_existing_values_wins(lake) -> None:
    lake.execute("INSERT INTO lake.s.t (name, vorhaben_id) VALUES ('x', 3)")
    config = {"vorhaben_id": {**SERIAL_CONFIG["vorhaben_id"], "start": 100}}
    _create(config)
    assert _serials(lake) == [3, 100]


def test_a_delete_leaves_a_gap(lake) -> None:
    ids = [_create(SERIAL_CONFIG) for _ in range(3)]
    SERVICE.delete_feature(LAYER, ids[1])
    _create(SERIAL_CONFIG)
    assert _serials(lake) == [1, 3, 4]


def test_deleting_the_highest_number_never_frees_it(lake) -> None:
    """The high-water mark remembers 3 after its feature is gone, so the next
    feature gets 4 — a number is never handed out twice."""
    store = _CounterTable()
    ids = [_create(SERIAL_CONFIG, store) for _ in range(3)]
    assert store.marks == {"vorhaben_id": 3}
    SERVICE.delete_feature(LAYER, ids[2])
    _create(SERIAL_CONFIG, store)
    assert _serials(lake) == [1, 2, 4]
    # Not even after every feature is gone.
    lake.execute("DELETE FROM lake.s.t")
    _create(SERIAL_CONFIG, store)
    assert _serials(lake) == [5]


def test_without_a_mark_numbering_falls_back_to_max(lake) -> None:
    """No counter row (a copy, or the table not migrated yet): ``max + 1``,
    which would hand out the deleted top number again."""
    ids = [_create(SERIAL_CONFIG) for _ in range(3)]
    SERVICE.delete_feature(LAYER, ids[2])
    _create(SERIAL_CONFIG)
    assert _serials(lake) == [1, 2, 3]


def test_the_mark_and_the_table_maximum_both_count(lake) -> None:
    """Values the mark does not know — imported, or written while the mark
    could not be stored — still push the next number past them."""
    store = _CounterTable()
    store.marks["vorhaben_id"] = 5
    lake.execute("INSERT INTO lake.s.t (name, vorhaben_id) VALUES ('x', 9)")
    _create(SERIAL_CONFIG, store)
    assert _serials(lake) == [9, 10]
    assert store.marks == {"vorhaben_id": 10}


def test_a_value_the_client_sends_on_create_is_ignored(lake) -> None:
    _create(SERIAL_CONFIG)
    feature_id = _create(SERIAL_CONFIG, vorhaben_id=999, name="typed by hand")
    assert _value(lake, feature_id, "vorhaben_id") == 2
    assert _value(lake, feature_id, "name") == "typed by hand"


def test_a_batch_gets_consecutive_numbers(lake) -> None:
    store = _CounterTable()
    _create(SERIAL_CONFIG, store)
    with store.write() as counters:
        ids = SERVICE.create_features_bulk(
            layer_info=LAYER,
            features=[
                {"geometry": POINT, "properties": {"name": str(i)}} for i in range(5)
            ],
            column_names=COLUMNS,
            geometry_column="geometry",
            field_config=SERIAL_CONFIG,
            serial_counters=counters,
        )
    assert [_value(lake, fid, "vorhaben_id") for fid in ids] == [2, 3, 4, 5, 6]
    # The mark moved by the batch's size.
    assert store.marks == {"vorhaben_id": 6}


def test_a_formula_reading_the_serial_is_computed_on_create(lake) -> None:
    lake.execute("ALTER TABLE lake.s.t ADD COLUMN code BIGINT")
    config = {
        **SERIAL_CONFIG,
        "code": {
            "kind": "formula",
            "is_computed": True,
            "formula": '"vorhaben_id" * 10',
            "depends_on": ["vorhaben_id"],
        },
    }
    feature_id = SERVICE.create_feature(
        layer_info=LAYER,
        geometry=POINT,
        properties={},
        column_names=[*COLUMNS, "code"],
        geometry_column="geometry",
        field_config=config,
    )
    assert _value(lake, feature_id, "code") == 10


# --- concurrency ---------------------------------------------------------------


def test_parallel_creates_never_share_a_number(lake) -> None:
    """Many request threads of one pod creating at once — single and batch
    writes mixed — still get distinct numbers with no gaps."""

    def single(_: int) -> None:
        _create(SERIAL_CONFIG)

    def batch(_: int) -> None:
        SERVICE.create_features_bulk(
            layer_info=LAYER,
            features=[{"geometry": POINT, "properties": {}} for _ in range(3)],
            column_names=COLUMNS,
            geometry_column="geometry",
            field_config=SERIAL_CONFIG,
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(single, range(40)))
        list(pool.map(batch, range(10)))

    values = _serials(lake)
    assert len(values) == 70
    assert sorted(values) == list(range(1, 71))


def test_parallel_creates_and_deletes_never_reuse_a_number(lake) -> None:
    """Every writer creates a feature and deletes it again at once, so the
    table's maximum keeps falling back; only the mark stops the next writer
    from handing out the same number again."""
    store = _CounterTable()
    handed_out: list[int] = []
    record = threading.Lock()

    from geoapi.services import feature_write_service as module

    def create_and_delete(_: int) -> None:
        feature_id = _create(SERIAL_CONFIG, store)
        # Through the manager's lock: the connection is shared by the threads.
        with module.ducklake_write_manager.connection():
            value = _value(lake, feature_id, "vorhaben_id")
        with record:
            handed_out.append(value)
        SERVICE.delete_feature(LAYER, feature_id)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(create_and_delete, range(30)))

    assert sorted(handed_out) == list(range(1, 31))
    assert store.marks == {"vorhaben_id": 30}


def test_two_writers_reading_before_either_inserts_would_collide(lake) -> None:
    """Why the write must be serialized at all: ``max + 1`` read by two writers
    before either commits hands out the same number. Inside a pod the write
    manager's lock prevents this; across pods the advisory lock does."""
    fields = generated_fields(SERIAL_CONFIG)
    first = GeneratedValues(lake, "lake.s.t", fields).next_row()
    second = GeneratedValues(lake, "lake.s.t", fields).next_row()
    assert first == second


# --- updates -------------------------------------------------------------------


@pytest.mark.parametrize("sent", [1, 1.0, "1"])
def test_an_update_may_send_the_stored_value_back(lake, sent: Any) -> None:
    """Editors round-trip the whole feature; the unchanged serial is fine."""
    feature_id = _create(SERIAL_CONFIG, name="old")
    assert SERVICE.update_feature_properties(
        layer_info=LAYER,
        feature_id=feature_id,
        properties={"name": "new", "vorhaben_id": sent},
        column_names=COLUMNS,
        field_config=SERIAL_CONFIG,
    )
    assert _value(lake, feature_id, "name") == "new"
    assert _value(lake, feature_id, "vorhaben_id") == 1


@pytest.mark.parametrize("sent", [2, None, "abc"])
def test_patch_cannot_change_a_serial(lake, sent: Any) -> None:
    feature_id = _create(SERIAL_CONFIG)
    with pytest.raises(ValueError, match="assigned automatically"):
        SERVICE.update_feature_properties(
            layer_info=LAYER,
            feature_id=feature_id,
            properties={"vorhaben_id": sent},
            column_names=COLUMNS,
            field_config=SERIAL_CONFIG,
        )
    assert _value(lake, feature_id, "vorhaben_id") == 1


def test_put_cannot_change_a_serial(lake) -> None:
    feature_id = _create(SERIAL_CONFIG)
    with pytest.raises(ValueError, match="assigned automatically"):
        SERVICE.replace_feature(
            layer_info=LAYER,
            feature_id=feature_id,
            geometry=POINT,
            properties={"vorhaben_id": 5, "name": "x"},
            column_names=COLUMNS,
            geometry_column="geometry",
            field_config=SERIAL_CONFIG,
        )
    assert _value(lake, feature_id, "vorhaben_id") == 1


def test_put_keeps_the_serial_when_sent_back_unchanged(lake) -> None:
    feature_id = _create(SERIAL_CONFIG, name="a")
    assert SERVICE.replace_feature(
        layer_info=LAYER,
        feature_id=feature_id,
        geometry=POINT,
        properties={"vorhaben_id": 1, "name": "b"},
        column_names=COLUMNS,
        geometry_column="geometry",
        field_config=SERIAL_CONFIG,
    )
    assert _value(lake, feature_id, "vorhaben_id") == 1
    assert _value(lake, feature_id, "name") == "b"


# --- adding the column to a layer with rows ------------------------------------


def test_adding_a_serial_numbers_existing_rows_in_feature_order(lake) -> None:
    lake.execute("CREATE TABLE lake.s.r (name VARCHAR)")
    for name in "abcde":
        lake.execute("INSERT INTO lake.s.r VALUES (?)", [name])
    lake.execute("DELETE FROM lake.s.r WHERE name = 'b'")
    rows_layer = LayerInfo(layer_id=LAYER_ID, schema_name="s", table_name="r")
    before = lake.execute("SELECT rowid, name FROM lake.s.r ORDER BY rowid").fetchall()

    SERVICE.add_column_with_sql(rows_layer, "nr", "BIGINT")
    counters = SerialCounters()
    SERVICE.backfill_generated_column(
        rows_layer, GeneratedField(name="nr", kind="serial", start=10), counters
    )
    # The last number the backfill handed out becomes the column's mark.
    assert counters.assigned == {"nr": 13}

    after = lake.execute(
        "SELECT rowid, name, nr FROM lake.s.r ORDER BY rowid"
    ).fetchall()
    # Same rows, same rowids (so the same feature ids), numbered in order.
    assert [(r, n) for r, n, _ in after] == before
    assert [nr for _, _, nr in after] == [10, 11, 12, 13]


def test_a_row_written_without_a_value_is_repaired_by_the_next_create(lake) -> None:
    """A feature created between the column's DDL and its field_config entry,
    or by a writer that knows nothing of generated columns, gets a number the
    next time anything is created — before the new feature's own."""
    _create(SERIAL_CONFIG)
    lake.execute("INSERT INTO lake.s.t (name) VALUES ('blank')")
    _create(SERIAL_CONFIG)
    assert _serials(lake) == [1, 2, 3]


def test_a_repaired_row_does_not_reuse_a_deleted_number(lake) -> None:
    store = _CounterTable()
    ids = [_create(SERIAL_CONFIG, store) for _ in range(2)]
    SERVICE.delete_feature(LAYER, ids[1])
    lake.execute("INSERT INTO lake.s.t (name) VALUES ('blank')")
    _create(SERIAL_CONFIG, store)
    assert _serials(lake) == [1, 3, 4]
    assert store.marks == {"vorhaben_id": 4}


# --- uuid ----------------------------------------------------------------------


def test_uuid_is_assigned_on_create_and_batch(lake) -> None:
    one = _create(UUID_CONFIG, uid="client-made")
    many = SERVICE.create_features_bulk(
        layer_info=LAYER,
        features=[{"geometry": POINT, "properties": {}} for _ in range(20)],
        column_names=COLUMNS,
        geometry_column="geometry",
        field_config=UUID_CONFIG,
    )
    values = [_value(lake, fid, "uid") for fid in [one, *many]]
    assert len(set(values)) == 21
    for value in values:
        assert uuid.UUID(value).version == 4
        assert value == str(uuid.UUID(value))  # canonical, lower case


def test_uuid_cannot_be_changed(lake) -> None:
    feature_id = _create(UUID_CONFIG)
    stored = _value(lake, feature_id, "uid")
    # Sent back unchanged (any case): accepted.
    assert SERVICE.update_feature_properties(
        layer_info=LAYER,
        feature_id=feature_id,
        properties={"uid": stored.upper(), "name": "n"},
        column_names=COLUMNS,
        field_config=UUID_CONFIG,
    )
    with pytest.raises(ValueError, match="assigned automatically"):
        SERVICE.update_feature_properties(
            layer_info=LAYER,
            feature_id=feature_id,
            properties={"uid": str(uuid.uuid4())},
            column_names=COLUMNS,
            field_config=UUID_CONFIG,
        )
    assert _value(lake, feature_id, "uid") == stored


def test_adding_a_uuid_column_gives_every_row_its_own(lake) -> None:
    lake.execute("CREATE TABLE lake.s.u (name VARCHAR)")
    lake.execute("INSERT INTO lake.s.u SELECT 'n' || range FROM range(50)")
    rows_layer = LayerInfo(layer_id=LAYER_ID, schema_name="s", table_name="u")
    SERVICE.add_column_with_sql(rows_layer, "uid", "VARCHAR")
    SERVICE.backfill_generated_column(
        rows_layer, GeneratedField(name="uid", kind="uuid")
    )
    values = [r[0] for r in lake.execute("SELECT uid FROM lake.s.u").fetchall()]
    assert len(set(values)) == 50
    assert all(uuid.UUID(v).version == 4 for v in values)


def test_serial_and_uuid_together(lake) -> None:
    config = {**SERIAL_CONFIG, **UUID_CONFIG}
    ids = [_create(config) for _ in range(3)]
    assert [_value(lake, i, "vorhaben_id") for i in ids] == [1, 2, 3]
    assert len({_value(lake, i, "uid") for i in ids}) == 3


# --- copies --------------------------------------------------------------------


def test_a_copy_keeps_its_values_and_continues_from_its_own_maximum(lake) -> None:
    """A filtered copy, an export/import or a template copy materializes the
    rows with their values and carries field_config across; nothing about the
    copy is special: without a mark of its own (the copies that do not carry
    the source's), ``max + 1`` simply continues from what it holds."""
    for name in "abcdef":
        _create(SERIAL_CONFIG, name=name)
    lake.execute(
        "CREATE TABLE lake.s.copy AS SELECT * FROM lake.s.t WHERE name IN ('a', 'c') ORDER BY rowid"
    )
    copy = LayerInfo(layer_id=LAYER_ID, schema_name="s", table_name="copy")
    _create(SERIAL_CONFIG, layer=copy, name="new")
    copied = lake.execute(
        "SELECT name, vorhaben_id FROM lake.s.copy ORDER BY rowid"
    ).fetchall()
    assert copied == [("a", 1), ("c", 3), ("new", 4)]


def test_a_copy_does_not_inherit_the_sources_mark(lake) -> None:
    """The source has handed out 1-6 (its mark is 6); the copy holds 1 and 3
    and has no counter row of its own, so it continues from 3. Its first
    create then gives it a mark of its own."""
    source = _CounterTable()
    for name in "abcdef":
        _create(SERIAL_CONFIG, source, name=name)
    assert source.marks == {"vorhaben_id": 6}
    lake.execute(
        "CREATE TABLE lake.s.copy AS SELECT * FROM lake.s.t WHERE name IN ('a', 'c') ORDER BY rowid"
    )
    copy = LayerInfo(layer_id=LAYER_ID, schema_name="s", table_name="copy")
    copy_marks = _CounterTable()
    _create(SERIAL_CONFIG, copy_marks, layer=copy, name="new")
    copied = lake.execute(
        "SELECT name, vorhaben_id FROM lake.s.copy ORDER BY rowid"
    ).fetchall()
    assert copied == [("a", 1), ("c", 3), ("new", 4)]
    assert copy_marks.marks == {"vorhaben_id": 4}
