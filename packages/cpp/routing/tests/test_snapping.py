"""How points are attached to the street network.

Self-contained: each network is a handful of street segments written to a
temporary directory in the uploaded-street-network layout (no H3 columns), and
each check is a one-pair travel-cost matrix in distance mode, so the expected
cost is plain geometry.

The files are written and read with pyarrow, not Python's duckdb: the routing
extension bundles its own libduckdb, and a process holding both corrupts its
heap on exit.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

try:
    import routing
except Exception as exc:  # pragma: no cover - import guard for local dev
    routing = None
    ROUTING_IMPORT_ERROR = exc
else:
    ROUTING_IMPORT_ERROR = None

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

pytestmark = pytest.mark.skipif(
    routing is None,
    reason=f"routing module is not importable: {ROUTING_IMPORT_ERROR}",
)

R = 6378137.0


def mercator(lon: float, lat: float) -> tuple[float, float]:
    return (
        math.radians(lon) * R,
        math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * R,
    )


def write_network(
    root: Path,
    nodes: dict[int, tuple[float, float]],
    edges: list[tuple[int, int, int]],
) -> Path:
    """Nodes in EPSG:3857, edges as (id, source, target) — written with the
    ground length an uploaded network carries (projected length × cos(lat))."""
    (root / "edges").mkdir(parents=True)
    (root / "nodes").mkdir(parents=True)
    pq.write_table(
        pa.table(
            {
                "id": pa.array(list(nodes), pa.int64()),
                "x_3857": [xy[0] for xy in nodes.values()],
                "y_3857": [xy[1] for xy in nodes.values()],
            }
        ),
        root / "nodes" / "nodes.parquet",
    )
    columns: dict[str, list] = {
        k: []
        for k in (
            "id",
            "source",
            "target",
            "length_m",
            "length_3857",
            "coordinates_3857",
        )
    }
    for edge_id, s, t in edges:
        (sx, sy), (tx, ty) = nodes[s], nodes[t]
        projected = math.hypot(tx - sx, ty - sy)
        columns["id"].append(edge_id)
        columns["source"].append(s)
        columns["target"].append(t)
        columns["length_m"].append(projected / math.cosh((sy + ty) / 2 / R))
        columns["length_3857"].append(projected)
        columns["coordinates_3857"].append([[sx, sy], [tx, ty]])
    n = len(edges)
    pq.write_table(
        pa.table(
            {
                "id": pa.array(columns["id"], pa.int64()),
                "source": pa.array(columns["source"], pa.int64()),
                "target": pa.array(columns["target"], pa.int64()),
                "length_m": columns["length_m"],
                "length_3857": columns["length_3857"],
                "class_": ["residential"] * n,
                "impedance_slope": [0.0] * n,
                "impedance_slope_reverse": [0.0] * n,
                "impedance_surface": pa.array([0.0] * n, pa.float32()),
                "maxspeed_forward": pa.array([30] * n, pa.int16()),
                "maxspeed_backward": pa.array([30] * n, pa.int16()),
                "coordinates_3857": columns["coordinates_3857"],
            }
        ),
        root / "edges" / "edges.parquet",
    )
    return root


def distance(
    network: Path,
    tmp_path: Path,
    origins: list[tuple[float, float]],
    destination: tuple[float, float],
) -> int | None:
    """Walking distance (m) from the first origin to the destination."""
    cfg = routing.MatrixConfig()
    cfg.origins = [routing.Point3857(*o) for o in origins]
    cfg.destinations = [routing.Point3857(*destination)]
    cfg.origin_ids = [str(i) for i in range(len(origins))]
    cfg.destination_ids = ["d"]
    cfg.mode = routing.RoutingMode.Walking
    cfg.cost_type = routing.CostType.Distance
    cfg.max_cost = 5000.0
    cfg.speed_km_h = 5.0
    cfg.edge_dir = str(network / "edges")
    cfg.node_dir = str(network / "nodes")
    cfg.output_path = str(tmp_path / "matrix.parquet")
    routing.compute_travel_cost_matrix(cfg)
    rows = pq.read_table(cfg.output_path).to_pylist()
    costs = [r["travel_cost"] for r in rows if r["origin"] == "0"]
    return costs[0] if costs else None


def test_connector_is_costed_at_its_ground_length(tmp_path: Path) -> None:
    """Coordinates are EPSG:3857, which stretches lengths by 1/cos(latitude):
    at 60°N a projected metre is half a ground metre. Street edges are costed
    from their ground length, so the connector joining a point to its street
    has to be too — measured in projected units it would cost twice its length.
    """
    lat, offset = 60.0, 100.0
    lons = {1: 10.000, 2: 10.002, 3: 10.004}
    nodes = {n: mercator(lon, lat) for n, lon in lons.items()}
    network = write_network(tmp_path / "net", nodes, [(10, 1, 2), (11, 2, 3)])

    def ground(lon_a: float, lon_b: float) -> float:
        return math.radians(abs(lon_b - lon_a)) * R * math.cos(math.radians(lat))

    # The origin stands `offset` m north of the middle of A—B; the destination
    # stands on C. Up to the street, then along it to C.
    mid = (lons[1] + lons[2]) / 2
    origin = mercator(mid, lat + math.degrees(offset / R))
    cost = distance(network, tmp_path, [origin], nodes[3])

    expected = offset + ground(mid, lons[2]) + ground(lons[2], lons[3])
    # The matrix reports whole metres. Costed in projected units, the 100 m
    # connector would add another 100 m at this latitude.
    assert cost is not None and abs(cost - expected) <= 1.0, (cost, expected)


def test_a_destination_does_not_snap_onto_an_origins_connector(
    tmp_path: Path,
) -> None:
    """Origins are attached first, each by a connector straight to its street;
    destinations after. A destination nearer to an origin's connector than to
    any street must still attach to the street: on the connector it would hang
    off the origin's spur and be "reached" in a straight line through blocks.

    At the equator projected and ground metres agree, so the geometry is exact:
    a street y=0 from x=0 to x=200, the origin at (100, 60), the destination at
    (130, 40) — 30 m from the origin's connector, 40 m from the street.
    """
    nodes = {1: (0.0, 0.0), 2: (100.0, 0.0), 3: (200.0, 0.0)}
    network = write_network(tmp_path / "net", nodes, [(10, 1, 2), (11, 2, 3)])

    cost = distance(network, tmp_path, [(100.0, 60.0)], (130.0, 40.0))

    # Down to the street (60), along it (30), up to the destination (40). On the
    # connector it would be 20 down it and 30 across: 50.
    assert cost is not None and abs(cost - 130) <= 1, cost
