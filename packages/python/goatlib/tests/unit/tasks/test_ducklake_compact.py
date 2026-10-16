"""Unit tests for the DuckLake compaction task.

The DuckDB connection is mocked — these tests verify only that the right
SQL is issued (candidate selection, merge_adjacent_files calls, optional
cleanup_old_files), and that the return shape correctly reports compacted
vs unchanged vs failed tables.
"""

from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from goatlib.tasks.ducklake_compact import (
    DuckLakeCompactParams,
    DuckLakeCompactTask,
    main,
)

# ────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────


class _FakeConn:
    """Minimal DuckDB connection mock.

    Returns canned data for the candidate-selection SELECT and for
    each merge_adjacent_files call. The merge call returns rows of
    (schema_name, table_name, files_processed, files_created) per the
    DuckLake API.
    """

    def __init__(
        self,
        candidates: list[tuple[str, str, int, int, int]],
        merge_results: dict[tuple[str, str], tuple[int, int]] | None = None,
        cleanup_deleted_paths: list[str] | None = None,
        merge_should_raise: set[tuple[str, str]] | None = None,
    ) -> None:
        self.calls: list[str] = []
        self._candidates = candidates
        # (files_processed, files_created) per (schema, table). Default
        # (0, 0) → "unchanged" (table reported by candidate filter but
        # nothing was actually merged on this run).
        self._merge_results = merge_results or {}
        self._cleanup = cleanup_deleted_paths or []
        self._merge_should_raise = merge_should_raise or set()
        # Remember which schema/table the most recent merge call was for,
        # so fetchall() can look up its canned result.
        self._last_merge: tuple[str, str] | None = None

    def execute(self, sql: str, *_: Any) -> "_FakeConn":
        self.calls.append(sql.strip())
        if "ducklake_merge_adjacent_files" in sql:
            # Parse positional table + named schema => '<schema>' from SQL.
            table = self._extract_first_string_literal(sql)
            schema = self._extract_named_arg(sql, "schema")
            self._last_merge = (schema, table) if schema and table else None
            for s, t in self._merge_should_raise:
                if self._last_merge == (s, t):
                    raise RuntimeError("simulated merge failure")
        return self

    @staticmethod
    def _extract_first_string_literal(sql: str) -> str | None:
        # Picks the second quoted literal because the first is 'lake'
        # (the catalog name).
        parts = sql.split("'")
        return parts[3] if len(parts) >= 4 else None

    @staticmethod
    def _extract_named_arg(sql: str, name: str) -> str | None:
        # Find name => '<value>'
        marker = f"{name} => '"
        i = sql.find(marker)
        if i < 0:
            return None
        rest = sql[i + len(marker) :]
        end = rest.find("'")
        return rest[:end] if end >= 0 else None

    def fetchall(self) -> list[tuple[Any, ...]]:
        last = self.calls[-1]
        if "FROM pg.ducklake.ducklake_data_file df" in last and "GROUP BY 1, 2" in last:
            return list(self._candidates)
        if "ducklake_merge_adjacent_files" in last:
            if self._last_merge is None:
                return []
            schema, table = self._last_merge
            fp, fc = self._merge_results.get((schema, table), (0, 0))
            if fp == 0 and fc == 0:
                return []
            return [(schema, table, fp, fc)]
        if "ducklake_cleanup_old_files" in last:
            return [(p,) for p in self._cleanup]
        return []

    def fetchone(self) -> tuple[Any, ...]:
        return (0,)


@contextmanager
def _fake_connection_cm(con: _FakeConn) -> Any:
    yield con


def _make_task(con: _FakeConn) -> DuckLakeCompactTask:
    task = DuckLakeCompactTask()
    task.settings = MagicMock()
    task.settings.ducklake_postgres_uri = "host=fake dbname=fake user=fake"
    fake_manager = MagicMock()
    fake_manager.connection.return_value = _fake_connection_cm(con)
    task._manager = fake_manager
    return task


def _has(calls: list[str], needle: str) -> bool:
    return any(needle in c for c in calls)


# ────────────────────────────────────────────────────────────────────────
# Params
# ────────────────────────────────────────────────────────────────────────


class TestParams:
    def test_defaults(self) -> None:
        p = DuckLakeCompactParams()
        assert p.min_files_per_table == 3
        assert p.target_file_size_mib == 256
        assert p.min_file_size_kib == 0
        assert p.max_compacted_files is None
        assert p.cleanup_after is True
        assert p.max_tables is None
        assert p.dry_run is False

    def test_min_files_at_least_2(self) -> None:
        with pytest.raises(ValueError):
            DuckLakeCompactParams(min_files_per_table=1)

    def test_target_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            DuckLakeCompactParams(target_file_size_mib=0)

    def test_floor_can_be_zero(self) -> None:
        # 0 = no noise floor; valid default.
        assert DuckLakeCompactParams(min_file_size_kib=0).min_file_size_kib == 0


# ────────────────────────────────────────────────────────────────────────
# Dry-run
# ────────────────────────────────────────────────────────────────────────


class TestDryRun:
    def test_lists_candidates_no_merge(self) -> None:
        con = _FakeConn(
            candidates=[
                ("user_a", "t_a", 5, 4, 10_000),
                ("user_b", "t_b", 8, 7, 20_000),
            ]
        )
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams(dry_run=True))

        # No merge or cleanup calls in dry run
        assert not _has(con.calls, "SELECT * FROM ducklake_merge_adjacent_files")
        assert not _has(con.calls, "ducklake_cleanup_old_files")

        assert out["dry_run"] is True
        assert len(out["candidates"]) == 2
        assert out["candidates"][0]["schema"] == "user_a"
        assert out["candidates"][0]["current_files"] == 5
        assert out["candidates"][0]["small_files"] == 4

    def test_max_tables_caps_dry_run(self) -> None:
        con = _FakeConn(candidates=[("u", f"t_{i}", 4, 3, 5_000) for i in range(10)])
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams(dry_run=True, max_tables=3))
        assert len(out["candidates"]) == 3


# ────────────────────────────────────────────────────────────────────────
# Real run
# ────────────────────────────────────────────────────────────────────────


class TestRealRun:
    def test_no_candidates_means_nothing_to_do(self) -> None:
        con = _FakeConn(candidates=[])
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams())
        assert not _has(con.calls, "SELECT * FROM ducklake_merge_adjacent_files")
        # cleanup_after defaults true and still runs (cheap no-op if
        # nothing is scheduled for deletion)
        assert _has(con.calls, "ducklake_cleanup_old_files")
        assert out["candidates"] == 0
        assert out["tables_compacted"] == 0

    def test_calls_merge_per_table_with_correct_api(self) -> None:
        con = _FakeConn(
            candidates=[("user_a", "t_a", 5, 4, 10_000)],
            merge_results={("user_a", "t_a"): (5, 1)},
        )
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams(target_file_size_mib=32))
        # Correct DuckLake API per docs: positional table, schema as
        # named kwarg, max_file_size as named kwarg. min_file_size is
        # NOT passed when the noise-floor default of 0 is in effect.
        assert _has(
            con.calls,
            "SELECT * FROM ducklake_merge_adjacent_files('lake', 't_a', "
            "schema => 'user_a', "
            f"max_file_size => {32 * 1024 * 1024})",
        )
        assert out["tables_compacted"] == 1
        assert out["tables_unchanged"] == 0
        assert out["files_processed"] == 5
        assert out["files_created"] == 1

    def test_min_file_size_only_passed_when_non_zero(self) -> None:
        con = _FakeConn(
            candidates=[("u", "t", 4, 3, 100)],
            merge_results={("u", "t"): (4, 1)},
        )
        task = _make_task(con)
        task.run(DuckLakeCompactParams(min_file_size_kib=8))
        assert _has(con.calls, f"min_file_size => {8 * 1024}")

    def test_max_compacted_files_passed_when_set(self) -> None:
        con = _FakeConn(
            candidates=[("u", "t", 4, 3, 100)],
            merge_results={("u", "t"): (4, 1)},
        )
        task = _make_task(con)
        task.run(DuckLakeCompactParams(max_compacted_files=10))
        assert _has(con.calls, "max_compacted_files => 10")

    def test_unchanged_table_reported_separately(self) -> None:
        # merge_adjacent_files returns no rows: nothing actually merged
        # on this run (decided by DuckLake's internal grouping rules).
        # Must not be counted as "compacted."
        con = _FakeConn(
            candidates=[("u", "t_static", 3, 1, 100)],
            merge_results={},
        )
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams())
        assert out["tables_compacted"] == 0
        assert out["tables_unchanged"] == 1

    def test_failure_per_table_doesnt_abort_run(self) -> None:
        con = _FakeConn(
            candidates=[
                ("u", "t_ok", 4, 3, 1000),
                ("u", "t_bad", 5, 4, 2000),
                ("u", "t_ok2", 6, 5, 3000),
            ],
            merge_results={
                ("u", "t_ok"): (4, 1),
                ("u", "t_ok2"): (6, 1),
            },
            merge_should_raise={("u", "t_bad")},
        )
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams())
        assert out["tables_compacted"] == 2
        assert len(out["failures"]) == 1
        assert out["failures"][0]["table"] == "lake.u.t_bad"
        assert "simulated" in out["failures"][0]["error"]

    def test_cleanup_after_false_skips_reclaim(self) -> None:
        con = _FakeConn(
            candidates=[("u", "t", 4, 3, 100)],
            merge_results={("u", "t"): (4, 1)},
            cleanup_deleted_paths=["/x/y.parquet"],
        )
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams(cleanup_after=False))
        assert not _has(con.calls, "ducklake_cleanup_old_files")
        assert out["files_reclaimed"] == 0

    def test_cleanup_after_true_reports_reclaim(self) -> None:
        con = _FakeConn(
            candidates=[("u", "t", 4, 3, 100)],
            merge_results={("u", "t"): (4, 1)},
            cleanup_deleted_paths=[
                "/x/old1.parquet",
                "/x/old2.parquet",
                "/x/old3.parquet",
            ],
        )
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams())
        assert _has(con.calls, "CALL ducklake_cleanup_old_files")
        assert out["files_reclaimed"] == 3

    def test_max_tables_caps_real_run(self) -> None:
        candidates = [("u", f"t_{i}", 4, 3, 1000) for i in range(5)]
        results = {("u", f"t_{i}"): (4, 1) for i in range(5)}
        con = _FakeConn(candidates=candidates, merge_results=results)
        task = _make_task(con)
        out = task.run(DuckLakeCompactParams(max_tables=2))
        merge_calls = [
            c for c in con.calls if "SELECT * FROM ducklake_merge_adjacent_files" in c
        ]
        assert len(merge_calls) == 2
        assert out["candidates"] == 2
        assert out["tables_compacted"] == 2


# ────────────────────────────────────────────────────────────────────────
# Threading params into SQL
# ────────────────────────────────────────────────────────────────────────


class TestParamThreading:
    def test_thresholds_in_candidate_query(self) -> None:
        con = _FakeConn(candidates=[])
        task = _make_task(con)
        task.run(
            DuckLakeCompactParams(
                min_files_per_table=7,
                target_file_size_mib=128,
                dry_run=True,
            )
        )
        candidate_sql = next(
            c for c in con.calls if "FROM pg.ducklake.ducklake_data_file" in c
        )
        # min_files_per_table is templated into HAVING
        assert ">= 7" in candidate_sql
        # target size becomes the "small file" threshold for the filter
        assert str(128 * 1024 * 1024) in candidate_sql


# ────────────────────────────────────────────────────────────────────────
# main() wrapper
# ────────────────────────────────────────────────────────────────────────


class TestMain:
    def test_main_inits_runs_and_closes(self) -> None:
        with patch("goatlib.tasks.ducklake_compact.DuckLakeCompactTask") as mock_cls:
            instance = mock_cls.return_value
            instance.run.return_value = {"dry_run": True}
            result = main(DuckLakeCompactParams(dry_run=True))
            instance.init_from_env.assert_called_once()
            instance.run.assert_called_once()
            instance.close.assert_called_once()
            assert result == {"dry_run": True}

    def test_main_closes_on_exception(self) -> None:
        with patch("goatlib.tasks.ducklake_compact.DuckLakeCompactTask") as mock_cls:
            instance = mock_cls.return_value
            instance.run.side_effect = RuntimeError("boom")
            with pytest.raises(RuntimeError):
                main(DuckLakeCompactParams())
            instance.close.assert_called_once()
