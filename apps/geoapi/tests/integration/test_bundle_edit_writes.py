"""The bundle batch write, against a real DuckLake.

``test_bundle_edits.py`` stubs ``_apply`` out, so nothing else executes the SQL
the editor generates: the segment writes, the geometry-derived columns (length
and the GeoParquet bbox struct) and the node pruning that follows a delete.
"""

from contextlib import contextmanager
from typing import Any, Generator

import duckdb
import pytest
from goatlib.storage.ducklake import connect_duckdb

from geoapi.dependencies import LayerInfo

# The edges layer's computed length, exactly as the importer declares it.
FIELD_CONFIG: dict[str, Any] = {
    "length_m": {"is_computed": True, "kind": "length", "depends_on": ["geometry"]},
    "class": {"allowed_values": ["residential", "unknown"], "allow_other": False},
}

BBOX = "STRUCT(xmin DOUBLE, ymin DOUBLE, xmax DOUBLE, ymax DOUBLE)"


class _FakeManager:
    """Replaces ducklake_write_manager: one real connection, no pool."""

    def __init__(self, con: duckdb.DuckDBPyConnection) -> None:
        self._con = con

    @contextmanager
    def connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        yield self._con


@pytest.fixture()
def network(tmp_path: Any) -> Generator[tuple[Any, LayerInfo, LayerInfo], None, None]:
    """A one-street network: 'street' from (0,0) to (0.002,0), and its two
    connectors. Degrees ~ metres/111320 along the equator, where EPSG:3857 is
    the identity scale, so distances are easy to reason about."""
    con = connect_duckdb(":memory:")
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL ducklake; LOAD ducklake;")
    con.execute(
        f"ATTACH 'ducklake:{tmp_path}/meta.ducklake' AS lake "
        f"(DATA_PATH '{tmp_path}/data');"
    )
    con.execute("CREATE SCHEMA lake.test_schema;")
    con.execute(
        f"""
        CREATE TABLE lake.test_schema.edges (
            "id" VARCHAR, "geometry" GEOMETRY,
            source_node VARCHAR, target_node VARCHAR,
            "class" VARCHAR, length_m DOUBLE,
            bbox {BBOX},
            xmin DOUBLE, ymin DOUBLE, xmax DOUBLE, ymax DOUBLE
        )
        """
    )
    con.execute(
        f"""
        CREATE TABLE lake.test_schema.nodes (
            "id" VARCHAR, "geometry" GEOMETRY, is_synthetic BOOLEAN,
            bbox {BBOX},
            xmin DOUBLE, ymin DOUBLE, xmax DOUBLE, ymax DOUBLE
        )
        """
    )
    con.execute(
        """
        INSERT INTO lake.test_schema.edges
        SELECT 'street', g, 'n-west', 'n-east', 'residential',
               ST_Length_Spheroid(g),
               struct_pack(xmin := ST_XMin(g), ymin := ST_YMin(g),
                           xmax := ST_XMax(g), ymax := ST_YMax(g)),
               ST_XMin(g), ST_YMin(g), ST_XMax(g), ST_YMax(g)
        FROM (SELECT ST_GeomFromText('LINESTRING (0 0, 0.002 0)') AS g)
        """
    )
    con.execute(
        """
        INSERT INTO lake.test_schema.nodes
        SELECT id, g, FALSE,
               struct_pack(xmin := ST_X(g), ymin := ST_Y(g),
                           xmax := ST_X(g), ymax := ST_Y(g)),
               ST_X(g), ST_Y(g), ST_X(g), ST_Y(g)
        FROM (VALUES ('n-west', ST_Point(0, 0)), ('n-east', ST_Point(0.002, 0)))
             t(id, g)
        """
    )
    edges = LayerInfo(
        layer_id="abc123de-f456-7890-1234-5678901234ab",
        schema_name="test_schema",
        table_name="edges",
    )
    nodes = LayerInfo(
        layer_id="abc123de-f456-7890-1234-5678901234ac",
        schema_name="test_schema",
        table_name="nodes",
    )
    yield con, edges, nodes
    con.close()


def _batch(**kwargs: Any) -> Any:
    from geoapi.routers.bundle_edits import BundleEditBatch

    return BundleEditBatch(base_revision=0, **kwargs)


def _apply_batch(con: Any, edges: LayerInfo, nodes: LayerInfo, body: Any) -> Any:
    from unittest.mock import patch

    from geoapi.routers.bundle_edits import _apply

    with patch("geoapi.routers.bundle_edits.ducklake_write_manager", _FakeManager(con)):
        return _apply(edges, nodes, body, FIELD_CONFIG)


def test_a_drawn_line_is_written_segment_by_segment(network: Any) -> None:
    """Two lines in one save: the first crosses the street and splits it, the
    second runs through the junction that made, so it is written as two edges.
    Every written row carries the length and the bbox its geometry implies —
    the artifact build inner-joins on them and the tile prefilter reads them."""
    con, edges, nodes = network

    crossing = {
        "type": "LineString",
        "coordinates": [[0.001, 0.0], [0.001, 0.001]],
    }
    through_the_junction = {
        "type": "LineString",
        "coordinates": [[0.0005, -0.0005], [0.001, 0.0], [0.0015, -0.0005]],
    }
    edge_changes, node_changes = _apply_batch(
        con,
        edges,
        nodes,
        _batch(
            create=[
                {"geometry": crossing, "properties": {"class": "residential"}},
                {
                    "geometry": through_the_junction,
                    "properties": {"class": "residential"},
                },
            ]
        ),
    )

    # The crossing is one edge; the line through the junction is broken there
    # into two, so three rows were created plus the street's two halves.
    assert len(edge_changes.created) == 3
    assert len(edge_changes.split) == 1
    assert edge_changes.split[0].original_id == "street"

    rows = con.execute(
        'SELECT "id", length_m, bbox.xmin, xmin, source_node, target_node '
        'FROM lake.test_schema.edges ORDER BY "id"'
    ).fetchall()
    assert len(rows) == 5
    assert "street" not in [r[0] for r in rows]
    for edge_id, length_m, struct_xmin, axis_xmin, source, target in rows:
        assert length_m and length_m > 0, edge_id
        # One definition of the bbox struct, so the two agree.
        assert struct_xmin == pytest.approx(axis_xmin), edge_id
        assert source and target, edge_id

    # One node minted on the street, plus a free end per drawn line: the far
    # end of the crossing and both ends of the line through the junction.
    assert len(node_changes.created) == 4
    # The node minted on the street sits on it, not at the drawn vertex.
    on_street = con.execute(
        "SELECT count(*) FROM lake.test_schema.nodes "
        "WHERE abs(ST_X(geometry) - 0.001) < 1e-9 AND abs(ST_Y(geometry)) < 1e-9"
    ).fetchone()
    assert on_street[0] == 1


def test_a_delete_prunes_only_the_nodes_nothing_holds(network: Any) -> None:
    """The endpoints of a removed edge are candidates; the ones another edge
    still references stay. Both answers come from the same reference query."""
    con, edges, nodes = network

    crossing = {"type": "LineString", "coordinates": [[0.001, 0.0], [0.001, 0.001]]}
    edge_changes, node_changes = _apply_batch(
        con, edges, nodes, _batch(create=[{"geometry": crossing, "properties": {}}])
    )
    drawn = edge_changes.created[0]
    junction, north = con.execute(
        'SELECT source_node, target_node FROM lake.test_schema.edges WHERE "id" = ?',
        [drawn],
    ).fetchone()

    _, removed = _apply_batch(con, edges, nodes, _batch(delete=[drawn]))

    # The far end held nothing else; the junction still holds both halves.
    assert removed.removed == [north]
    surviving = {
        r[0] for r in con.execute('SELECT "id" FROM lake.test_schema.nodes').fetchall()
    }
    assert junction in surviving
    assert north not in surviving
    assert con.execute("SELECT count(*) FROM lake.test_schema.edges").fetchone()[0] == 2


# The edges layer with a serial number and a UUID the user added to it.
GENERATED_CONFIG: dict[str, Any] = {
    **FIELD_CONFIG,
    "nr": {"kind": "serial", "start": 1, "user_added": True},
    "uid": {"kind": "uuid", "user_added": True},
}


def _with_generated_columns(con: Any) -> None:
    """Add both columns the way add_column does: DDL, then the backfill."""
    from goatlib.utils.generated_fields import generated_fields

    con.execute("ALTER TABLE lake.test_schema.edges ADD COLUMN nr BIGINT")
    con.execute("ALTER TABLE lake.test_schema.edges ADD COLUMN uid VARCHAR")
    for field in generated_fields(GENERATED_CONFIG):
        con.execute(field.backfill_sql("lake.test_schema.edges"))


def _apply_generated(con: Any, edges: LayerInfo, nodes: LayerInfo, body: Any) -> Any:
    from unittest.mock import patch

    from geoapi.routers.bundle_edits import _apply

    with patch("geoapi.routers.bundle_edits.ducklake_write_manager", _FakeManager(con)):
        return _apply(edges, nodes, body, GENERATED_CONFIG)


def test_new_and_split_edges_get_their_own_generated_values(network: Any) -> None:
    """Every edge a save writes is a new edge — drawn pieces and both halves of
    a split street alike — so each gets the next number and a fresh UUID in
    the insert itself (an update afterwards would leave a transaction-local
    rowid on the row). A value the client sends is ignored."""
    import uuid

    con, edges, nodes = network
    _with_generated_columns(con)
    assert con.execute("SELECT nr FROM lake.test_schema.edges").fetchall() == [(1,)]

    crossing = {"type": "LineString", "coordinates": [[0.001, 0.0], [0.001, 0.001]]}
    through_the_junction = {
        "type": "LineString",
        "coordinates": [[0.0005, -0.0005], [0.001, 0.0], [0.0015, -0.0005]],
    }
    _apply_generated(
        con,
        edges,
        nodes,
        _batch(
            create=[
                {"geometry": crossing, "properties": {"nr": 99, "uid": "mine"}},
                {"geometry": through_the_junction, "properties": {}},
            ]
        ),
    )

    rows = con.execute(
        "SELECT rowid, nr, uid FROM lake.test_schema.edges ORDER BY nr"
    ).fetchall()
    assert len(rows) == 5
    # The street (1) was replaced by its halves; nothing reuses a number twice.
    assert [nr for _, nr, _ in rows] == [2, 3, 4, 5, 6]
    assert len({uid for _, _, uid in rows}) == 5
    assert all(uuid.UUID(uid).version == 4 for _, _, uid in rows)
    assert all(rowid < 1_000_000 for rowid, _, _ in rows)


def test_an_edge_update_cannot_change_its_generated_values(network: Any) -> None:
    con, edges, nodes = network
    _with_generated_columns(con)
    street = {"type": "LineString", "coordinates": [[0.0, 0.0], [0.002, 0.0001]]}
    uid = con.execute("SELECT uid FROM lake.test_schema.edges").fetchone()[0]

    # Sent back unchanged, as the editor does: saved, values kept.
    _apply_generated(
        con,
        edges,
        nodes,
        _batch(
            update=[
                {
                    "id": "1",
                    "geometry": street,
                    "properties": {"class": "unknown", "nr": 1, "uid": uid},
                }
            ]
        ),
    )
    assert con.execute(
        'SELECT "class", nr, uid FROM lake.test_schema.edges'
    ).fetchall() == [("unknown", 1, uid)]

    with pytest.raises(ValueError, match="assigned automatically"):
        _apply_generated(
            con,
            edges,
            nodes,
            _batch(update=[{"id": "1", "geometry": street, "properties": {"nr": 7}}]),
        )
    assert con.execute("SELECT nr FROM lake.test_schema.edges").fetchall() == [(1,)]


def test_bundle_edges_continue_after_the_high_water_mark(network: Any) -> None:
    """Numbers up to 50 were handed out once (their edges since deleted): the
    batch's new edges and split halves continue at 51, and the batch reports
    the last one back for the lock holder to store."""
    from unittest.mock import patch

    from goatlib.utils.generated_fields import SerialCounters

    from geoapi.routers.bundle_edits import _apply

    con, edges, nodes = network
    _with_generated_columns(con)
    crossing = {"type": "LineString", "coordinates": [[0.001, 0.0], [0.001, 0.001]]}
    counters = SerialCounters(high_water={"nr": 50})
    with patch("geoapi.routers.bundle_edits.ducklake_write_manager", _FakeManager(con)):
        _apply(
            edges,
            nodes,
            _batch(create=[{"geometry": crossing, "properties": {}}]),
            GENERATED_CONFIG,
            counters,
        )
    numbers = sorted(
        r[0] for r in con.execute("SELECT nr FROM lake.test_schema.edges").fetchall()
    )
    # The crossing plus the street's two halves; the street (1) is gone.
    assert numbers == [51, 52, 53]
    assert counters.assigned == {"nr": 53}
