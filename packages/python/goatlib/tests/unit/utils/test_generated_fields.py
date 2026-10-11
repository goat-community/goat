"""The generator behind serial and UUID fields (``goatlib.utils.generated_fields``).

The rules every writer shares: how an entry is read, which settings are valid,
how the next number is chosen, and which updates are refused. The writers
themselves are tested in geoapi against a real DuckLake.
"""

import uuid

import duckdb
import pytest
from goatlib.utils.generated_fields import (
    MAX_SERIAL_VALUE,
    GeneratedField,
    GeneratedValues,
    SerialCounters,
    generated_entry_settings,
    generated_fields,
    needs_write_lock,
    refuse_generated_changes,
    validate_serial_start,
)


@pytest.fixture()
def con():
    connection = duckdb.connect()
    connection.execute("CREATE TABLE t (name VARCHAR, nr BIGINT, uid VARCHAR)")
    yield connection
    connection.close()


class TestSettings:
    @pytest.mark.parametrize(
        ("raw", "expected"), [(None, 1), (0, 0), (5, 5), ("7", 7), (3.0, 3)]
    )
    def test_valid_starts(self, raw, expected):
        assert validate_serial_start(raw) == expected

    @pytest.mark.parametrize("raw", [-1, 1.5, "abc", True, [], MAX_SERIAL_VALUE + 1])
    def test_invalid_starts(self, raw):
        with pytest.raises(ValueError):
            validate_serial_start(raw)

    def test_entry_settings(self):
        assert generated_entry_settings("serial") == {"start": 1}
        assert generated_entry_settings("serial", 10) == {"start": 10}
        assert generated_entry_settings("uuid") == {}
        with pytest.raises(ValueError):
            generated_entry_settings("uuid", 3)
        with pytest.raises(ValueError):
            generated_entry_settings("number")


class TestReadingFieldConfig:
    def test_only_generated_kinds_are_read(self):
        config = {
            "nr": {"kind": "serial", "start": 5},
            "uid": {"kind": "uuid"},
            "name": {"kind": "string"},
            "broken": "not an entry",
        }
        assert generated_fields(config) == [
            GeneratedField(name="nr", kind="serial", start=5),
            GeneratedField(name="uid", kind="uuid"),
        ]

    def test_a_malformed_start_falls_back_instead_of_breaking_writes(self):
        assert generated_fields({"nr": {"kind": "serial", "start": "x"}})[0].start == 1

    def test_only_a_serial_needs_the_write_lock(self):
        assert needs_write_lock(generated_fields({"nr": {"kind": "serial"}}))
        assert not needs_write_lock(generated_fields({"uid": {"kind": "uuid"}}))
        assert not needs_write_lock([])


class TestNextValues:
    def test_empty_table_starts_at_start(self, con):
        values = GeneratedValues(con, "t", [GeneratedField("nr", "serial", 10)])
        assert [values.next_row()["nr"] for _ in range(3)] == [10, 11, 12]

    def test_continues_after_the_maximum_not_the_count(self, con):
        con.execute("INSERT INTO t (name, nr) VALUES ('a', 5), ('b', 2)")
        values = GeneratedValues(con, "t", [GeneratedField("nr", "serial", 1)])
        assert values.next_row() == {"nr": 6}

    def test_uuid_values_are_fresh_v4(self, con):
        values = GeneratedValues(con, "t", [GeneratedField("uid", "uuid")])
        rows = [values.next_row()["uid"] for _ in range(100)]
        assert len(set(rows)) == 100
        assert all(uuid.UUID(v).version == 4 for v in rows)

    def test_blank_rows_are_filled_first(self, con):
        con.execute(
            "INSERT INTO t (name, nr) VALUES ('a', 1), ('b', NULL), ('c', NULL)"
        )
        values = GeneratedValues(
            con, "t", [GeneratedField("nr", "serial", 1), GeneratedField("uid", "uuid")]
        )
        assert con.execute("SELECT nr FROM t ORDER BY rowid").fetchall() == [
            (1,),
            (2,),
            (3,),
        ]
        assert con.execute("SELECT count(DISTINCT uid) FROM t").fetchone()[0] == 3
        assert values.next_row()["nr"] == 4

    def test_running_out_of_numbers_is_refused(self, con):
        con.execute("INSERT INTO t (nr) VALUES (?)", [MAX_SERIAL_VALUE])
        values = GeneratedValues(con, "t", [GeneratedField("nr", "serial", 1)])
        with pytest.raises(ValueError, match="run out"):
            values.next_row()

    def test_no_generated_columns_reads_nothing(self):
        class _Unused:
            def execute(self, *args):
                raise AssertionError("no query expected")

        assert GeneratedValues(_Unused(), "t", []).next_row() == {}


class TestBackfill:
    def test_numbers_rows_in_rowid_order_after_existing_ones(self, con):
        con.execute(
            "INSERT INTO t (name, nr) VALUES ('a', NULL), ('b', 7), ('c', NULL)"
        )
        con.execute(GeneratedField("nr", "serial", 1).backfill_sql("t"))
        assert con.execute("SELECT name, nr FROM t ORDER BY rowid").fetchall() == [
            ("a", 8),
            ("b", 7),
            ("c", 9),
        ]

    def test_a_fresh_column_starts_at_start(self, con):
        con.execute("INSERT INTO t (name) VALUES ('a'), ('b')")
        con.execute(GeneratedField("nr", "serial", 100).backfill_sql("t"))
        assert con.execute("SELECT nr FROM t ORDER BY rowid").fetchall() == [
            (100,),
            (101,),
        ]

    def test_uuid_backfill_gives_each_row_its_own(self, con):
        con.execute("INSERT INTO t (name) SELECT 'x' FROM range(30)")
        con.execute(GeneratedField("uid", "uuid").backfill_sql("t"))
        rows = [r[0] for r in con.execute("SELECT uid FROM t").fetchall()]
        assert len(set(rows)) == 30
        assert all(uuid.UUID(v).version == 4 for v in rows)


class TestRefusingChanges:
    FIELDS = [GeneratedField("nr", "serial"), GeneratedField("uid", "uuid")]
    UID = "0625b5a7-50e1-4cfa-8392-7b0852e0d980"

    @pytest.mark.parametrize(
        "sent", [{"nr": 3}, {"nr": 3.0}, {"nr": "3"}, {"uid": UID.upper()}, {}]
    )
    def test_the_stored_value_sent_back_is_accepted(self, sent):
        refuse_generated_changes(self.FIELDS, {"nr": 3, "uid": self.UID}, sent)

    @pytest.mark.parametrize(
        "sent", [{"nr": 4}, {"nr": None}, {"nr": "x"}, {"uid": "other"}, {"uid": None}]
    )
    def test_a_changed_value_is_refused(self, sent):
        with pytest.raises(ValueError, match="assigned automatically"):
            refuse_generated_changes(self.FIELDS, {"nr": 3, "uid": self.UID}, sent)


class TestHighWaterMark:
    """A serial number is never handed out twice: the next one is past both
    the table's maximum and the highest number ever handed out."""

    def test_the_mark_wins_over_a_lower_table_maximum(self, con):
        con.execute("INSERT INTO t (nr) VALUES (1), (2)")
        counters = SerialCounters(high_water={"nr": 9})
        values = GeneratedValues(con, "t", [GeneratedField("nr", "serial")], counters)
        assert [values.next_row()["nr"] for _ in range(2)] == [10, 11]
        assert counters.assigned == {"nr": 11}

    def test_the_table_maximum_wins_over_a_lower_mark(self, con):
        con.execute("INSERT INTO t (nr) VALUES (20)")
        counters = SerialCounters(high_water={"nr": 9})
        values = GeneratedValues(con, "t", [GeneratedField("nr", "serial")], counters)
        assert values.next_row()["nr"] == 21

    def test_an_empty_table_with_a_mark_does_not_start_over(self, con):
        counters = SerialCounters(high_water={"nr": 41})
        values = GeneratedValues(
            con, "t", [GeneratedField("nr", "serial", 1)], counters
        )
        assert values.next_row()["nr"] == 42

    def test_no_mark_falls_back_to_the_table(self, con):
        con.execute("INSERT INTO t (nr) VALUES (3)")
        counters = SerialCounters()
        values = GeneratedValues(con, "t", [GeneratedField("nr", "serial")], counters)
        assert values.next_row()["nr"] == 4
        assert counters.assigned == {"nr": 4}

    def test_the_table_maximum_is_recorded_even_without_a_new_row(self, con):
        """A copy's own numbers become its mark at the first write."""
        con.execute("INSERT INTO t (nr) VALUES (7)")
        counters = SerialCounters()
        GeneratedValues(con, "t", [GeneratedField("nr", "serial")], counters)
        assert counters.assigned == {"nr": 7}

    def test_a_uuid_column_leaves_the_counters_alone(self, con):
        counters = SerialCounters()
        GeneratedValues(con, "t", [GeneratedField("uid", "uuid")], counters).next_row()
        assert counters.assigned == {}

    def test_backfill_continues_after_the_mark(self, con):
        con.execute("INSERT INTO t (name) VALUES ('a'), ('b')")
        con.execute(GeneratedField("nr", "serial", 1).backfill_sql("t", high_water=30))
        assert con.execute("SELECT nr FROM t ORDER BY rowid").fetchall() == [
            (31,),
            (32,),
        ]

    def test_record_only_moves_up(self):
        counters = SerialCounters()
        counters.record("nr", 5)
        counters.record("nr", 3)
        counters.record("nr", 8)
        assert counters.assigned == {"nr": 8}
