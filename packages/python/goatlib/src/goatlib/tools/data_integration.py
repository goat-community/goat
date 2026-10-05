"""Extract features from our mirrored map data for one area.

Reads the mirrored snapshot in place over S3 -- the parquet is pruned by row
group, so a city-sized area touches a few megabytes of a multi-gigabyte file and
nothing is downloaded.

Tags are matched the way `osm/poi/_base.sql` matches them: a regex over the raw
hstore text first, so only candidate rows pay for the parse, then the parsed map
for an exact comparison. `LIKE '%amenity%'` alone would also match `amenity:parking`.
"""

import json
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Literal, Self

from pydantic import BaseModel, ConfigDict, Field

from goatlib.analysis.schemas.ui import (
    SECTION_INPUT,
    SECTION_OUTPUT,
    SECTION_RESULT,
    layer_selector_field,
    ui_field,
    ui_sections,
)
from goatlib.models.io import DatasetMetadata
from goatlib.tools.base import BaseToolRunner, _get_or_create_event_loop
from goatlib.tools.schemas import ToolInputBase

logger = logging.getLogger(__name__)

#: Where the harvester leaves its snapshots. Configurable because the mirror is
#: not part of this deployment -- it is written by goat-data, and only the two
#: agree on the location.
MIRROR_URI = os.environ.get("OSM_MIRROR_URI", "s3://goat/catalog-test/_osm")
OVERTURE_MIRROR_URI = os.environ.get(
    "OVERTURE_MIRROR_URI", "s3://goat/catalog-test/_overture"
)

#: The GDAL OSM layers the mirror converts, and the geometry each yields.
FEATURE_TYPES: dict[str, str] = {
    "points": "point",
    "lines": "line",
    "multipolygons": "polygon",
}

#: Overture's own types, flattened to one choice each: the theme and type are
#: always picked together, so offering them separately would only allow
#: combinations that do not exist.
OVERTURE_TYPES: dict[str, tuple[str, str]] = {
    "places": ("places/place", "point"),
    "divisions": ("divisions/division_area", "polygon"),
    "roads": ("transportation/segment", "line"),
    "junctions": ("transportation/connector", "point"),
}


@dataclass(frozen=True)
class Source:
    """What differs between the mirrors, in one place.

    Everything else -- coverage, clipping, dedup, the picker -- is written once
    against this rather than branching on the source name.
    """

    mirror: str
    #: Geometry column. GDAL writes `geom`, Overture publishes `geometry`.
    geom: str
    #: Stable feature id, for dropping a feature two extracts both carry.
    id_column: str
    #: Whether attributes live in one hstore string rather than in columns.
    tagged: bool

    def layer_uri(self, extent: str, snapshot: str, type_key: str) -> str:
        layer = type_key if self.tagged else OVERTURE_TYPES[type_key][0]
        return f"{self.mirror}/{extent}/{snapshot}/{layer}/*.parquet"

    def geometry_of(self, type_key: str) -> str:
        return FEATURE_TYPES[type_key] if self.tagged else OVERTURE_TYPES[type_key][1]


#: The columns every Overture type shares. They identify and date a feature
#: rather than describing it, so none is worth offering as a filter.
OVERTURE_HOUSEKEEPING = frozenset(
    {"id", "geometry", "bbox", "theme", "type", "version", "sources"}
)

SOURCES: dict[str, Source] = {
    "osm": Source(MIRROR_URI, "geom", "osm_id", True),
    "overture": Source(OVERTURE_MIRROR_URI, "geometry", "id", False),
}


#: hstore text -> a map, as `osm/poi/_base.sql` does it.
TAGS_SQL = """CAST(TRY_CAST('{' || replace(replace(replace(replace(
    all_tags, '"=>"', '":"'), chr(10), '\\n'), chr(13), '\\r'),
    chr(9), '\\t') || '}' AS JSON) AS MAP(VARCHAR, VARCHAR))"""


def ensure_s3(con: "Any") -> None:
    """Point a connection at our object storage.

    Called rather than assumed: the connections this runs on are made for
    DuckLake, which is read from disk, so nothing has configured S3 on them.
    Idempotent, and quiet when no endpoint is set -- a deployment reading real
    AWS needs no endpoint at all.
    """
    con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;")
    endpoint = (os.environ.get("S3_ENDPOINT_URL") or "").strip()
    key = os.environ.get("S3_ACCESS_KEY_ID") or ""
    secret = os.environ.get("S3_SECRET_ACCESS_KEY") or ""
    if endpoint:
        host = endpoint.split("://", 1)[-1].rstrip("/")
        con.execute(f"SET s3_endpoint = '{host}'")
        con.execute(f"SET s3_use_ssl = {str(endpoint.startswith('https')).lower()}")
        # Path style: a bucket in the host name only works for real AWS, and an
        # endpoint is set precisely when this is not that.
        con.execute("SET s3_url_style = 'path'")
    if key and secret:
        con.execute(f"SET s3_access_key_id = '{key}'")
        con.execute(f"SET s3_secret_access_key = '{secret}'")


def snapshots(con: "Any", source: Source) -> dict[str, str]:
    """The newest complete snapshot of every mirrored extract.

    Globbed on the manifest, which the mirror writes last -- so an extract still
    being converted has none and is skipped rather than half-read.
    """
    newest: dict[str, str] = {}
    rows = con.execute(
        f"SELECT file FROM glob('{source.mirror}/*/*/_manifest.json')"
    ).fetchall()
    for (path,) in rows:
        parts = str(path).rstrip("/").split("/")
        extent, sid = parts[-3], parts[-2]
        if sid > newest.get(extent, ""):
            newest[extent] = sid
    return newest


def covering(
    con: "Any",
    snaps: dict[str, str],
    source: Source,
    type_key: str,
    envelope: tuple,
) -> list[tuple[str, str]]:
    """The extracts that can hold something in this envelope.

    Judged on each file's declared bbox, read from the parquet footer -- no data
    is touched. That bbox is a superset of what the extract really covers
    (Geofabrik keeps ways whose nodes fall well outside the country), so it can
    rule an extract OUT safely but never rule one in: whichever survive are
    queried, and the area itself decides.
    """
    xmin, ymin, xmax, ymax = envelope
    out: list[tuple[str, str]] = []
    for extent, sid in sorted(snaps.items()):
        url = source.layer_uri(extent, sid, type_key)
        try:
            rows = con.execute(
                f"SELECT value FROM parquet_kv_metadata('{url}') WHERE key = 'geo'"
            ).fetchall()
        except Exception as e:
            logger.warning("no metadata for %s/%s: %s", extent, sid, e)
            continue
        for (value,) in rows:
            raw = value.decode() if isinstance(value, bytes) else value
            for column in (json.loads(raw).get("columns") or {}).values():
                bbox = column.get("bbox")
                if (
                    bbox
                    and bbox[0] <= xmax
                    and bbox[2] >= xmin
                    and bbox[1] <= ymax
                    and bbox[3] >= ymin
                ):
                    out.append((extent, sid))
                    break
            else:
                continue
            break
    return out


def area_geom_column(con: "Any", area_table: str) -> str:
    """The reference layer's geometry column.

    Detected, not assumed: the mirror names it `geom` and a GOAT layer names it
    `geometry`, and this reads a GOAT layer.
    """
    described = con.execute(f"DESCRIBE SELECT * FROM {area_table}").fetchall()
    for row in described:
        if "GEOMETRY" in str(row[1]).upper():
            return str(row[0])
    raise ValueError(
        "The reference area layer has no geometry column, so there is no area "
        "to read."
    )


def area_envelope(con: "Any", area_table: str) -> tuple:
    """The reference area's bounding box."""
    geom = area_geom_column(con, area_table)
    bounds = con.execute(
        f"SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM "
        f'(SELECT ST_Extent(ST_Union_Agg("{geom}")) AS e FROM {area_table})'
    ).fetchone()
    if not bounds or bounds[0] is None:
        raise ValueError(
            "The reference area layer holds no geometry, so there is no area to read."
        )
    return tuple(bounds)


def candidates_sql(
    parts: list[tuple[str, str]],
    source: Source,
    type_key: str,
    envelope: tuple,
    prefilter: str,
) -> str:
    """One SELECT per covering extract, unioned.

    An area on a border sits in two extracts at once and each keeps its own copy
    of the features there, so the same feature can arrive twice.
    """
    xmin, ymin, xmax, ymax = envelope
    # A tagged source carries its attributes in one string, so the parsed map is
    # added here; a typed one already has columns and needs nothing.
    projection = (
        f"* EXCLUDE (all_tags), all_tags, {TAGS_SQL} AS tags" if source.tagged else "*"
    )
    selects = [
        f"""SELECT {projection}
            FROM read_parquet('{source.layer_uri(extent, sid, type_key)}')
            WHERE {prefilter}
              AND ST_Intersects("{source.geom}",
                                ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}))"""
        for extent, sid in parts
    ]
    return " UNION ALL ".join(selects)


def _column_values(
    con: "Any",
    source: Source,
    parts: list,
    type_key: str,
    envelope: tuple,
    key: str | None,
    limit: int,
) -> dict:
    """The same answer for a typed source, without any of the machinery.

    No hstore to parse, so no cache either: the keys are the file's own columns,
    read from its footer, and the values are a plain count over one column.
    """
    extent, sid = parts[0]
    url = source.layer_uri(extent, sid, type_key)
    if key is None:
        described = con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{url}')"
        ).fetchall()
        # Only what a user can compare: a struct or a list has no single value
        # to offer. The housekeeping columns go too -- every Overture type
        # carries the same seven, and none describes the feature: `theme` and
        # `type` are constant within a file, `id` is unique, `version` and
        # `sources` are the publisher's own bookkeeping.
        names = [
            str(r[0])
            for r in described
            if str(r[1]).upper()
            in ("VARCHAR", "BIGINT", "INTEGER", "DOUBLE", "BOOLEAN")
            and str(r[0]) not in OVERTURE_HOUSEKEEPING
            and str(r[0]) != source.geom
        ]
        return {
            "key": None,
            "total": len(names),
            "values": [{"value": n, "count": 0} for n in names],
        }

    inner = candidates_sql(parts, source, type_key, envelope, "TRUE")
    rows = con.execute(f"""
        SELECT "{_quote(key)}" AS value, count(*) AS count FROM ({inner})
        WHERE "{_quote(key)}" IS NOT NULL
        GROUP BY value ORDER BY count DESC, value LIMIT {int(limit)}
    """).fetchall()
    return {
        "key": key,
        "total": len(rows),
        "values": [{"value": str(v), "count": n} for v, n in rows],
    }


def _tag_cache_path(
    cache_key: str, feature_type: str, parts: list, envelope: tuple
) -> Path:
    """Where this area's parsed tags are kept between calls.

    Keyed on the snapshots too, so next week's mirror does not answer from last
    week's file. An area edited without moving its bounding box is the case this
    misses; the file is disposable, so deleting it is the remedy.
    """
    import hashlib

    stamp = "|".join(
        [cache_key, feature_type, *(f"{e}/{s}" for e, s in parts)]
        + [f"{v:.5f}" for v in envelope]
    )
    digest = hashlib.sha256(stamp.encode()).hexdigest()[:24]
    # The shared volume where it belongs, falling back to scratch where that is
    # not writable -- a cache is an optimisation, and losing it between restarts
    # costs one slow call, where failing to place it would cost the feature.
    for root in (
        Path(os.environ.get("DATA_DIR", "/app/data")) / "cache" / "osm_tags",
        Path(tempfile.gettempdir()) / "goat_osm_tags",
    ):
        try:
            root.mkdir(parents=True, exist_ok=True)
            return root / f"{digest}.parquet"
        except OSError as e:
            logger.info("tag cache unavailable at %s: %s", root, e)
    raise OSError("no writable location for the tag cache")


def tag_values(
    con: "Any",
    *,
    area_table: str,
    feature_type: str,
    key: str | None = None,
    limit: int = 100,
    cache_key: str | None = None,
    source_name: str = "osm",
) -> dict:
    """Which tag keys, or which values of one key, occur in this area.

    Scoped to the area on purpose: over a whole country this would mean parsing
    every row, while a district is a few thousand and answers at once. It is
    also the only list worth showing -- a key that exists in Hamburg helps
    nobody drawing a box in Munich.
    """
    ensure_s3(con)
    src = SOURCES[source_name]
    envelope = area_envelope(con, area_table)
    parts = covering(con, snapshots(con, src), src, feature_type, envelope)
    if not parts:
        return {"key": key, "total": 0, "values": []}

    if not src.tagged:
        return _column_values(con, src, parts, feature_type, envelope, key, limit)

    # Every feature's tags in the area, parsed once and kept. Building it is the
    # slow part -- the whole area is read and every hstore parsed -- and the
    # form asks repeatedly: the keys, then the values of each key a user tries.
    # Without this each of those reads the same rows from the mirror again.
    cache = None
    if cache_key:
        try:
            cache = _tag_cache_path(cache_key, feature_type, parts, envelope)
        except OSError as e:
            logger.warning("tag cache disabled: %s", e)
    if cache is not None and cache.exists():
        source = f"SELECT tags FROM read_parquet('{cache}')"
    else:
        # The envelope, not the area itself. Testing 445k points against a
        # unioned multipolygon is ~26s of a ~28s call, and buys a list that is
        # the same either way -- a key present just outside the boundary is
        # present inside it too. The extract still clips exactly; this only
        # decides what the dropdowns offer.
        inner = candidates_sql(parts, src, feature_type, envelope, "TRUE")
        source = f"SELECT tags FROM ({inner})"
        if cache is not None:
            tmp = cache.with_suffix(".tmp.parquet")
            con.execute(f"COPY ({source}) TO '{tmp}' (FORMAT PARQUET)")
            os.replace(tmp, cache)
            source = f"SELECT tags FROM read_parquet('{cache}')"

    picked = (
        "unnest(map_keys(tags))"
        if key is None
        else f"tags['{key.replace(chr(39), chr(39) * 2)}']"
    )
    rows = con.execute(f"""
        WITH picked AS (SELECT {picked} AS value FROM ({source}))
        SELECT value, count(*) AS count FROM picked
        WHERE value IS NOT NULL AND value <> ''
        GROUP BY value ORDER BY count DESC, value LIMIT {int(limit)}
    """).fetchall()
    return {
        "key": key,
        "total": len(rows),
        "values": [{"value": v, "count": n} for v, n in rows],
    }


class TagFilter(BaseModel):
    """One `key = value` condition on an OSM tag.

    Both sides are offered from the reference area rather than typed: OSM has no
    fixed schema, so the only honest list is what the chosen area actually holds.
    """

    key: str = Field(
        ...,
        description="OSM tag key, e.g. amenity",
        max_length=255,
        json_schema_extra=ui_field(
            section="input", field_order=1, widget="osm-tag-key"
        ),
    )
    value: str = Field(
        "",
        description="Value to match. Left empty, any feature carrying the key matches.",
        max_length=255,
        json_schema_extra=ui_field(
            section="input", field_order=2, widget="osm-tag-value"
        ),
    )


class DataIntegrationParams(ToolInputBase):
    """Parameters for extracting from the OSM mirror."""

    model_config = ConfigDict(
        json_schema_extra=ui_sections(SECTION_INPUT, SECTION_RESULT, SECTION_OUTPUT)
    )

    source: Literal["osm", "overture"] = Field(
        "osm",
        description="Which mirror to read",
        json_schema_extra=ui_field(section="input", field_order=2),
    )
    feature_type: Literal["points", "lines", "multipolygons"] = Field(
        "points",
        description="Which geometry to extract",
        json_schema_extra=ui_field(
            section="input", field_order=3, visible_when={"source": "osm"}
        ),
    )
    overture_type: Literal["places", "divisions", "roads", "junctions"] = Field(
        "places",
        description="Which kind of feature to extract",
        json_schema_extra=ui_field(
            section="input", field_order=3, visible_when={"source": "overture"}
        ),
    )
    tag_filters: List[TagFilter] = Field(
        default_factory=list,
        description="Tag conditions, combined with AND. None returns every feature in the area.",
        json_schema_extra=ui_field(
            section="input",
            field_order=4,
            repeatable=True,
        ),
    )
    reference_area_layer_id: str = Field(
        ...,
        title="Reference Area",
        description="Polygon layer whose geometry bounds the extract",
        json_schema_extra=layer_selector_field(
            section="input",
            field_order=1,
            geometry_types=["Polygon", "MultiPolygon"],
        ),
    )


def _quote(value: str) -> str:
    return value.replace("'", "''")


def _column_sql(filters: List[TagFilter]) -> tuple[str, str]:
    """The same pair for a typed source: no prefilter, a plain comparison.

    Nothing to pre-filter and nothing to parse -- the attribute is already a
    column, so the only test is the test.
    """
    if not filters:
        return "TRUE", "TRUE"
    exact = [
        f'"{_quote(f.key)}" IS NOT NULL'
        if not f.value
        else f"\"{_quote(f.key)}\" = '{_quote(f.value)}'"
        for f in filters
    ]
    return "TRUE", " AND ".join(exact)


def filter_sql(filters: List[TagFilter], source: Source) -> tuple[str, str]:
    """(cheap prefilter before parsing, exact test after)."""
    return _tag_sql(filters) if source.tagged else _column_sql(filters)


def _tag_sql(filters: List[TagFilter]) -> tuple[str, str]:
    """(cheap prefilter on the raw text, exact test on the parsed map)."""
    if not filters:
        return "TRUE", "TRUE"
    pre, exact = [], []
    for f in filters:
        key = _quote(re.escape(f.key))
        if not f.value:
            pre.append(f"regexp_matches(all_tags, '\"{key}\"=>')")
            exact.append(f"map_contains(tags, '{_quote(f.key)}')")
        else:
            val = _quote(re.escape(f.value))
            pre.append(f'regexp_matches(all_tags, \'"{key}"=>"{val}"\')')
            exact.append(f"tags['{_quote(f.key)}'] = '{_quote(f.value)}'")
    return " AND ".join(pre), " AND ".join(exact)


class DataIntegrationRunner(BaseToolRunner[DataIntegrationParams]):
    """Read the mirror for an area and write one layer."""

    default_output_name = "Extracted Features"
    output_geometry_type = "point"

    def process(
        self: Self, params: DataIntegrationParams, temp_dir: Path
    ) -> tuple[Path, DatasetMetadata]:
        con = self.duckdb_con
        ensure_s3(con)

        src = SOURCES[params.source]
        type_key = params.feature_type if src.tagged else params.overture_type
        self.output_geometry_type = src.geometry_of(type_key)

        area = self.resolve_layer_table_path(params.reference_area_layer_id)
        envelope = area_envelope(con, area)
        area_geom = area_geom_column(con, area)
        parts = covering(con, snapshots(con, src), src, type_key, envelope)
        if not parts:
            raise ValueError(
                "No mirrored extract covers the reference area. Extracts are "
                "prepared per region, and this area is outside every one we hold."
            )

        prefilter, exact = filter_sql(params.tag_filters, src)
        out = temp_dir / "output.parquet"
        # Two spatial tests, not one: the envelope prunes row groups before
        # anything is read, the area itself is what the user asked for. The
        # dedup is for a feature that two bordering extracts both carry.
        con.execute(f"""
            COPY (
                WITH area AS (SELECT ST_Union_Agg("{area_geom}") AS g FROM {area}),
                candidates AS ({candidates_sql(parts, src, type_key, envelope, prefilter)})
                SELECT c.* {"EXCLUDE (tags)" if src.tagged else ""}
                FROM candidates c, area
                WHERE {exact} AND ST_Intersects(c."{src.geom}", area.g)
                QUALIFY row_number() OVER (
                    PARTITION BY c."{src.id_column}" ORDER BY c."{src.id_column}"
                ) = 1
            ) TO '{out}' (FORMAT PARQUET)
        """)
        count = con.execute(f"SELECT count(*) FROM read_parquet('{out}')").fetchone()
        features = int(count[0]) if count else 0
        read = ", ".join(f"{e} {sid}" for e, sid in parts)
        conditions = ", ".join(
            f"{f.key}={f.value}" if f.value else f.key for f in params.tag_filters
        )
        # Recorded in the job rather than on the layer: the output's metadata
        # describes the file, and nothing carries provenance from a tool to the
        # layer it creates. ODbL attribution still has to reach the user, so
        # this is the honest place to say it until that path exists.
        logger.info(
            "extracted %s feature(s) from the OpenStreetMap mirror (%s)%s "
            "— © OpenStreetMap contributors, ODbL-1.0",
            features,
            read,
            f", where {conditions}" if conditions else "",
        )
        provider = "OpenStreetMap" if src.tagged else "Overture Maps"
        self._provenance = {
            "lineage": (
                f"Extracted from the {provider} mirror ({read})"
                + (f", where {conditions}" if conditions else "")
            ),
            "license": "ODbL-1.0",
            "attribution": (
                "© OpenStreetMap contributors"
                if src.tagged
                else "© OpenStreetMap contributors, Overture Maps Foundation"
            ),
            "distributor_name": provider,
            "distribution_url": (
                "https://www.openstreetmap.org"
                if src.tagged
                else "https://overturemaps.org"
            ),
        }
        return out, DatasetMetadata(
            path=str(out),
            source_type="vector",
            format="parquet",
            driver="duckdb",
            crs="EPSG:4326",
            geometry_type=self.output_geometry_type,
            feature_count=features,
        )


async def _record_provenance(
    runner: DataIntegrationRunner, layer_id: str, provenance: dict
) -> None:
    """Write where the data came from onto the layer the tool just made.

    Done here because the runner creates the layer from the output file's
    metadata, which carries no provenance -- and this layer's licence is an
    obligation that has to travel with it, not a nicety.
    """
    assert runner.settings is not None
    pool = await runner.get_postgres_pool()
    await pool.execute(
        f"UPDATE {runner.settings.customer_schema}.layer "
        f"SET dataset_metadata = $1::jsonb WHERE id = $2::uuid",
        json.dumps(provenance),
        layer_id,
    )


def main(params: DataIntegrationParams) -> dict:
    """Windmill entry point."""
    runner = DataIntegrationRunner()
    runner.init_from_env()
    try:
        result = runner.run(params)
        layer_id = result.get("layer_id") if isinstance(result, dict) else None
        provenance = getattr(runner, "_provenance", None)
        if layer_id and provenance:
            try:
                _get_or_create_event_loop().run_until_complete(
                    _record_provenance(runner, str(layer_id), provenance)
                )
            except Exception as e:  # noqa: BLE001 - the layer matters more
                logger.warning("could not record provenance on %s: %s", layer_id, e)
        return result
    finally:
        runner.cleanup()
