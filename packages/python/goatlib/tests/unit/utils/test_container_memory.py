"""DuckDB budgets follow the container's memory limit.

A connection without a memory_limit takes 80% of the container for itself,
so several of them can pass the limit and get the container killed before
DuckDB spills. Shares of the container's limit keep them under it.
"""

from pathlib import Path

import pytest
from goatlib.utils import container_memory
from goatlib.utils.container_memory import (
    container_memory_limit,
    duckdb_memory_limit,
    set_memory_share,
)

GIB = 1024**3


def _cgroup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *values: str) -> None:
    files = []
    for i, value in enumerate(values):
        path = tmp_path / f"limit{i}"
        path.write_text(value + "\n")
        files.append(path)
    files.append(tmp_path / "missing")
    monkeypatch.setattr(container_memory, "CGROUP_MEMORY_LIMIT_FILES", tuple(files))


@pytest.mark.unit
def test_a_cgroup_v2_limit_is_read(monkeypatch, tmp_path) -> None:
    _cgroup(monkeypatch, tmp_path, str(4 * GIB))
    assert container_memory_limit() == 4 * GIB
    assert duckdb_memory_limit(0.5) == "2048MiB"


@pytest.mark.unit
@pytest.mark.parametrize("value", ["max", str(9223372036854771712)])
def test_no_limit_falls_back_to_the_default(monkeypatch, tmp_path, value) -> None:
    _cgroup(monkeypatch, tmp_path, value)
    assert container_memory_limit() is None
    assert duckdb_memory_limit(0.5, "4GB") == "4GB"
    assert duckdb_memory_limit(0.25) is None


@pytest.mark.unit
def test_without_cgroup_files_there_is_no_limit(monkeypatch, tmp_path) -> None:
    _cgroup(monkeypatch, tmp_path)
    assert container_memory_limit() is None


@pytest.mark.unit
def test_an_analysis_takes_half_the_container(monkeypatch, tmp_path) -> None:
    from goatlib.analysis.core.base import AnalysisTool

    _cgroup(monkeypatch, tmp_path, str(4 * GIB))
    tool = AnalysisTool(db_path=tmp_path / "analysis.duckdb")
    try:
        (limit,) = tool.con.execute("SELECT current_setting('memory_limit')").fetchone()
    finally:
        tool.con.close()

    assert limit == "2.0 GiB"


class _RecordingConnection:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def execute(self, sql: str) -> None:
        self.executed.append(sql)


@pytest.mark.unit
def test_a_share_is_set_only_with_a_limit_or_a_default(monkeypatch, tmp_path) -> None:
    _cgroup(monkeypatch, tmp_path, str(2 * GIB))
    con = _RecordingConnection()
    set_memory_share(con, 0.25)
    assert con.executed == ["SET memory_limit='512MiB'"]

    _cgroup(monkeypatch, tmp_path, "max")
    con = _RecordingConnection()
    set_memory_share(con, 0.25)
    assert con.executed == []
    set_memory_share(con, 0.5, "4GB")
    assert con.executed == ["SET memory_limit='4GB'"]
