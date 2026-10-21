"""The routing tools' own result writers, on a result without rows.

The routing engine is not needed for what is tested here: each writer gets
the table or file it would get after the engine ran, with no rows, and must
write a file whose geometry column is still a GEOMETRY, so the step after it
finds one (`goatlib.io.config.parquet_copy_options`).
"""

from pathlib import Path

import duckdb
import pytest
from goatlib.analysis.accessibility.trip_count import TripCountStationTool
from goatlib.analysis.schemas.catchment_area_v2 import ShapeStyle
from goatlib.io.config import parquet_copy_options
from goatlib.tools.catchment_area_v2 import CatchmentAreaV2ToolRunner
from goatlib.tools.travel_cost_matrix import TravelCostMatrixToolRunner

POINT = "ST_Point(11.5, 48.1)::GEOMETRY('OGC:CRS84')"


def _types(path: Path) -> dict[str, str]:
    con = duckdb.connect()
    try:
        con.execute("INSTALL spatial; LOAD spatial;")
        rows = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()
        count = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()
    finally:
        con.close()
    assert count == (0,)
    return {str(r[0]): str(r[1]) for r in rows}


def _write(path: Path, query: str) -> Path:
    """A file without rows, written as the step before writes its result."""
    con = duckdb.connect()
    try:
        con.execute("INSTALL spatial; LOAD spatial;")
        con.execute(f"COPY ({query}) TO '{path}' {parquet_copy_options()}")
    finally:
        con.close()
    return path


def test_trip_count_with_no_station_in_service(tmp_path: Path) -> None:
    tool = TripCountStationTool()
    try:
        tool.con.execute(f"""
            CREATE TABLE station_mode_counts AS
            SELECT 's1' AS stop_id, 'Halt' AS stop_name, NULL::VARCHAR AS parent_station,
                   0 AS bus, 0 AS tram, 0 AS metro, 0 AS rail, 0 AS other,
                   0 AS total, 0.0 AS frequency, {POINT} AS geom
        """)
        tool.con.execute("CREATE TABLE stations_in_area AS SELECT 's1' AS stop_id")
        out = tmp_path / "trips.parquet"
        tool._export_results(str(out))
    finally:
        tool.cleanup()
    assert _types(out)["geom"].startswith("GEOMETRY")


def test_travel_cost_matrix_destinations_without_rows(tmp_path: Path) -> None:
    destinations = _write(
        tmp_path / "destinations.parquet",
        f"SELECT 1 AS id, {POINT} AS geometry WHERE false",
    )
    matrix = _write(
        tmp_path / "matrix.parquet",
        "SELECT 'a' AS origin, 'b' AS destination, 1 AS travel_cost WHERE false",
    )
    out = tmp_path / "out.parquet"
    TravelCostMatrixToolRunner()._build_destination_points_parquet(
        matrix, destinations, out
    )
    assert _types(out)["geometry"].startswith("GEOMETRY")


@pytest.mark.parametrize("shape_style", [ShapeStyle.combined, ShapeStyle.separated])
def test_catchment_area_bands_without_rows(
    tmp_path: Path, shape_style: ShapeStyle
) -> None:
    """Both ways the engine's origin index leaves the result: dropped for
    combined shapes, turned into an origin for separated ones."""
    engine_result = _write(
        tmp_path / "engine.parquet",
        f"SELECT 0 AS origin_idx, 300 AS travel_cost, {POINT} AS geometry WHERE false",
    )
    runner = CatchmentAreaV2ToolRunner()
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    runner._duckdb_con = con
    runner._starting_point_references = []
    try:
        out = runner._resolve_origins(engine_result, shape_style, tmp_path)
    finally:
        con.close()
        runner._duckdb_con = None
    assert out != engine_result
    assert _types(out)["geometry"].startswith("GEOMETRY")
