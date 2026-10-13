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
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Literal, Self
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field

from goatlib.analysis.schemas.ui import (
    SECTION_INPUT,
    SECTION_OUTPUT,
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
MIRROR_URI = os.environ.get("OSM_MIRROR_URI", "s3://goat/mirror/osm")
OVERTURE_MIRROR_URI = os.environ.get("OVERTURE_MIRROR_URI", "s3://goat/mirror/overture")

#: Above this the extract fails rather than writing a layer cut at an arbitrary row.
MAX_FEATURES = 1_000_000

#: Features read to suggest keys and values: the fetch limit, so any area small
#: enough to fetch whole gets exact counts. Reading every feature of a large map
#: view took over a minute.
SUGGESTION_ROWS = MAX_FEATURES
#: A first, fast read whose list shows while the full one is counted.
QUICK_ROWS = 100_000
#: The same for a key too rare to show up in that sample.
RARE_KEY_ROWS = 20_000

#: A cached tag list unused this long is deleted, and the check runs at most
#: this often -- the files are disposable, and without it they pile up forever.
TAG_CACHE_MAX_IDLE_SECONDS = 60 * 60
_tag_cache_swept = 0.0
_tag_cache_sweep_lock = threading.Lock()

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
    "buildings": ("buildings/building", "polygon"),
    "land_use": ("base/land_use", "polygon"),
    "land": ("base/land", "polygon"),
    "water_areas": ("base/water", "polygon"),
    "waterways": ("base/water", "line"),
    "infrastructure_points": ("base/infrastructure", "point"),
    "infrastructure_lines": ("base/infrastructure", "line"),
    "infrastructure_areas": ("base/infrastructure", "polygon"),
}

#: The licence follows the data: OSM is ODbL, Overture's licence is per theme.
#: Places come from Meta, Microsoft and others under CDLA; every other theme
#: offered here is built on OSM and stays ODbL.
OSM_LICENCE = ("ODbL-1.0", "© OpenStreetMap contributors")
OVERTURE_LICENCES: dict[str, tuple[str, str]] = {
    "places": ("CDLA-Permissive-2.0", "© Overture Maps Foundation"),
}
OVERTURE_OSM_LICENCE = (
    "ODbL-1.0",
    "© OpenStreetMap contributors, Overture Maps Foundation",
)

#: The Overture themes whose types mix geometries (water has lakes and rivers).
MIXED_THEMES = frozenset({"base"})

#: A GOAT layer holds one geometry type, and a base type mixes them (water has
#: lakes and rivers), so each option keeps the rows of its own.
GEOMETRY_TYPES: dict[str, tuple[str, ...]] = {
    "point": ("POINT", "MULTIPOINT"),
    "line": ("LINESTRING", "MULTILINESTRING"),
    "polygon": ("POLYGON", "MULTIPOLYGON"),
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

    def unit_of(self, type_key: str) -> str | None:
        """The pointer unit holding a type: any continent for OSM, one theme for Overture."""
        return None if self.tagged else OVERTURE_TYPES[type_key][0].split("/")[0]

    def layer_of(self, type_key: str) -> str:
        return type_key if self.tagged else OVERTURE_TYPES[type_key][0].split("/")[1]

    def geometry_filter(self, type_key: str) -> str:
        """SQL keeping only this option's geometry type.

        Only where a type mixes them: OSM layers and most Overture types hold one
        already, and the test reads the geometry column, the largest in the file.
        """
        if self.tagged or self.unit_of(type_key) not in MIXED_THEMES:
            return "TRUE"
        kinds = ", ".join(f"'{k}'" for k in GEOMETRY_TYPES[self.geometry_of(type_key)])
        return f'ST_GeometryType("{self.geom}")::VARCHAR IN ({kinds})'

    def licence_of(self, type_key: str) -> tuple[str, str]:
        """The SPDX licence and the attribution notice it obliges."""
        if self.tagged:
            return OSM_LICENCE
        return OVERTURE_LICENCES.get(self.unit_of(type_key) or "", OVERTURE_OSM_LICENCE)

    def field_sql(self, type_key: str, field: str) -> str:
        """A filterable Overture attribute as SQL text, or a refusal for any other."""
        fields = OVERTURE_FIELDS.get(OVERTURE_TYPES[type_key][0], {})
        if field not in fields:
            raise ValueError(
                f"'{field}' is not an attribute you can filter this type on."
            )
        return f"CAST({fields[field]} AS VARCHAR)"

    def geometry_of(self, type_key: str) -> str:
        return FEATURE_TYPES[type_key] if self.tagged else OVERTURE_TYPES[type_key][1]


#: The attributes worth filtering on, per Overture type, and where each lives.
#: Chosen rather than read off the schema: the useful ones are often nested
#: (a place's category, a brand's name), and the plain columns include free
#: text, ids and decimal scores no filter needs.
OVERTURE_FIELDS: dict[str, dict[str, str]] = {
    "places/place": {
        "category": '"taxonomy"."primary"',
        "basic_category": '"basic_category"',
        "brand": '"brand"."names"."primary"',
        "operating_status": '"operating_status"',
    },
    "buildings/building": {
        "class": '"class"',
        "subtype": '"subtype"',
        "roof_shape": '"roof_shape"',
        "roof_material": '"roof_material"',
        "facade_material": '"facade_material"',
        "is_underground": '"is_underground"',
    },
    "divisions/division_area": {
        "subtype": '"subtype"',
        "class": '"class"',
        "country": '"country"',
    },
    "base/land_use": {
        "subtype": '"subtype"',
        "class": '"class"',
        "surface": '"surface"',
    },
    "base/land": {
        "subtype": '"subtype"',
        "class": '"class"',
        "surface": '"surface"',
    },
    "base/water": {
        "subtype": '"subtype"',
        "class": '"class"',
        "is_intermittent": '"is_intermittent"',
        "is_salt": '"is_salt"',
    },
    "base/infrastructure": {
        "subtype": '"subtype"',
        "class": '"class"',
        "surface": '"surface"',
    },
}

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
    # The mirror may sit in another store than GOAT's own; a secret scoped to its
    # bucket leaves every other s3:// read on the settings above.
    m_endpoint = (os.environ.get("MIRROR_S3_ENDPOINT_URL") or "").strip()
    m_bucket = (os.environ.get("MIRROR_S3_BUCKET") or "").strip()
    if m_endpoint and m_bucket:
        u = urlparse(m_endpoint)
        con.execute(f"""CREATE OR REPLACE SECRET goat_mirror (
            TYPE s3, KEY_ID '{_quote(os.environ.get("MIRROR_S3_ACCESS_KEY_ID", ""))}',
            SECRET '{_quote(os.environ.get("MIRROR_S3_SECRET_ACCESS_KEY", ""))}',
            ENDPOINT '{_quote(u.netloc)}', USE_SSL {str(u.scheme == "https").lower()},
            URL_STYLE 'path', REGION '{_quote(os.environ.get("MIRROR_S3_REGION") or "us-east-1")}',
            SCOPE 's3://{_quote(m_bucket)}')""")


def pointer(con: "Any", source: Source) -> dict:
    """Which version of each unit is current: one small object the mirror writes last."""
    try:
        row = con.execute(
            f"SELECT content FROM read_text('{source.mirror}/_current.json')"
        ).fetchone()
    except Exception as e:  # noqa: BLE001 - no pointer is no data, not an error
        logger.warning("no mirror pointer at %s: %s", source.mirror, e)
        return {}
    return (json.loads(row[0]) if row else {}).get("units", {})


def covering(
    con: "Any", units: dict, source: Source, type_key: str, envelope: tuple
) -> tuple[list[str], list[tuple[str, str]]]:
    """The data files that can hold something in this envelope, and the unit versions read.

    Decided from each version's index, which holds every file's actual bounds, so
    no data file or footer is opened to decide."""
    xmin, ymin, xmax, ymax = envelope
    wanted = source.unit_of(type_key)
    bases: dict[str, tuple[str, str]] = {}
    for unit, state in sorted(units.items()):
        b = state.get("bbox")
        if (wanted is not None and unit != wanted) or (
            b and (b[0] > xmax or b[2] < xmin or b[1] > ymax or b[3] < ymin)
        ):
            continue
        base = f"{source.mirror}/{unit}/{state['version']}"
        bases[f"{base}/_index.parquet"] = (unit, state["version"])
    if not bases:
        return [], []
    # One read over every index: they are remote, and one round trip per
    # country made a large area cost ten seconds before any data was touched.
    listed = ", ".join(f"'{_quote(i)}'" for i in bases)
    rows = con.execute(
        f"SELECT filename, path FROM read_parquet([{listed}], filename = true, union_by_name = true) "
        "WHERE layer = ? AND xmin <= ? AND xmax >= ? AND ymin <= ? AND ymax >= ? "
        "ORDER BY filename, path",
        [source.layer_of(type_key), xmax, xmin, ymax, ymin],
    ).fetchall()
    files = [f"{index.removesuffix('/_index.parquet')}/{p}" for index, p in rows]
    read = [bases[i] for i in bases if any(index == i for index, _ in rows)]
    return files, read


def area_geom_column(con: "Any", area_table: str) -> str:
    """The reference layer's geometry column.

    Detected, not assumed: the mirror names it `geom` and a GOAT layer names it
    `geometry`, and this reads a GOAT layer.
    """
    described = con.execute(f"DESCRIBE SELECT * FROM {area_table}").fetchall()
    for row in described:
        if "GEOMETRY" in str(row[1]).upper():
            return str(row[0])
    raise ValueError("The area has no geometry column, so there is no area to read.")


def area_envelope(con: "Any", area_table: str) -> tuple:
    """The reference area's bounding box."""
    geom = area_geom_column(con, area_table)
    bounds = con.execute(
        f"SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM "
        f'(SELECT ST_Extent(ST_Union_Agg("{geom}")) AS e FROM {area_table})'
    ).fetchone()
    if not bounds or bounds[0] is None:
        raise ValueError("The area holds no geometry, so there is no area to read.")
    return tuple(bounds)


def area_table(con: "Any", area: dict) -> str:
    """The area as a one-row table, so it is read like a layer."""
    con.execute(
        "CREATE OR REPLACE TEMP TABLE fetch_area AS SELECT ST_GeomFromGeoJSON(?) AS geom",
        [json.dumps(area)],
    )
    row = con.execute(
        "SELECT ST_GeometryType(geom)::VARCHAR FROM fetch_area"
    ).fetchone()
    if not row or row[0] not in ("POLYGON", "MULTIPOLYGON"):
        raise ValueError("The area has to be a polygon.")
    return "fetch_area"


def checked_where(con: "Any", files: list[str], source: Source, where: str) -> str:
    """A user's own condition, held to what goatlib allows in an expression."""
    from goatlib.utils.expressions.validator import ExpressionValidator

    columns = [
        str(r[0])
        for r in con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{_quote(files[0])}')"
        ).fetchall()
    ]
    if source.tagged:
        columns.append("tags")
    result = ExpressionValidator(columns, source.geom).validate(where)
    if not result.valid:
        raise ValueError(
            "The SQL condition is not allowed: "
            + "; ".join(e.message for e in result.errors)
        )
    return f"({where})"


def _joined(items: str) -> str:
    """A list's distinct non-empty values, in first-seen order, as one text.

    Not list_distinct, which does not keep order. NULL when nothing is left, so
    an empty list reads as missing rather than as an empty string.
    """
    return (
        f"NULLIF(array_to_string(list_filter({items}, (x, i) -> x IS NOT NULL "
        f"AND x <> '' AND list_position({items}, x) = i), '; '), '')"
    )


def overture_plain_columns(columns: dict[str, str], alias: str = "c") -> list[str]:
    """Overture's name and source attribution as plain columns, from the nested ones.

    The tile writer drops struct and list columns, so without these the map
    shows nothing for them. ``sources`` also carries each record's licence --
    buildings mix OpenStreetMap (ODbL, attribution required) with Microsoft,
    Google and others -- so the attribution has to be readable on the map too.
    Built only from what the file has: a type without them gets none.
    """
    out = []
    if "primary" in columns.get("names", ""):
        out.append(f'{alias}."names"."primary" AS name')
    sources = columns.get("sources", "")

    def field(name: str) -> str:
        return f"list_transform({alias}.sources, s -> s.{name})"

    if "dataset" in sources:
        out.append(f"{_joined(field('dataset'))} AS source")
    if "license" in sources:
        out.append(f"{_joined(field('license'))} AS source_license")
    if "record_id" in sources:
        out.append(
            f"NULLIF(array_to_string({field('record_id')}, '; '), '') AS source_id"
        )
    if "update_time" in sources:
        out.append(f"list_max({field('update_time')}) AS source_updated")
    return out


def candidates_sql(
    files: list[str], source: Source, envelope: tuple, prefilter: str
) -> str:
    """One read over every covering file. Features at a continent seam can arrive
    twice; the caller de-duplicates by id."""
    xmin, ymin, xmax, ymax = envelope
    # Inside a CASE, so only rows the prefilter admits are parsed: written as a
    # plain projection, DuckDB merged it with the exact test into one filter and
    # parsed every row first -- 0.59s instead of 0.05s for Munich's points.
    parsed = (
        TAGS_SQL
        if prefilter == "TRUE"
        else f"CASE WHEN {prefilter} THEN {TAGS_SQL} END"
    )
    projection = (
        f"* EXCLUDE (all_tags), all_tags, {parsed} AS tags" if source.tagged else "*"
    )
    listed = ", ".join(f"'{_quote(f)}'" for f in files)
    return f"""SELECT {projection}
        FROM read_parquet([{listed}], union_by_name = true, filename = true)
        WHERE bbox.xmin <= {xmax} AND bbox.xmax >= {xmin}
          AND bbox.ymin <= {ymax} AND bbox.ymax >= {ymin}
          AND {prefilter}
          AND ST_Intersects("{source.geom}", ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}))"""


def _column_values(
    con: "Any",
    source: Source,
    files: list[str],
    type_key: str,
    envelope: tuple,
    key: str | None,
    limit: int,
) -> dict:
    """The same answer for a typed source, without any of the machinery.

    No hstore to parse, so no cache either: the keys are the file's own columns,
    read from its footer, and the values are a plain count over one column.
    """
    # By each feature's bbox only, as for OSM: the exact test reads the geometry
    # column and changes nothing a dropdown shows.
    xmin, ymin, xmax, ymax = envelope
    listed = ", ".join(f"'{_quote(f)}'" for f in files)
    capped = f"""SELECT * FROM read_parquet([{listed}], union_by_name = true)
        WHERE bbox.xmin <= {xmax} AND bbox.xmax >= {xmin}
          AND bbox.ymin <= {ymax} AND bbox.ymax >= {ymin}
          AND {source.geometry_filter(type_key)}
        LIMIT {SUGGESTION_ROWS}"""
    if key is None:
        fields = OVERTURE_FIELDS.get(OVERTURE_TYPES[type_key][0], {})
        counted = ", ".join(f"count({sql})" for sql in fields.values())
        row = con.execute(f"SELECT count(*), {counted} FROM ({capped})").fetchone()
        return {
            "key": None,
            "total": len(fields),
            "sampled": bool(row) and row[0] >= SUGGESTION_ROWS,
            "values": [
                {"value": name, "count": int(n)}
                for name, n in zip(fields, row[1:] if row else [])
                if n
            ],
        }

    column = source.field_sql(type_key, key)
    rows = con.execute(f"""
        SELECT {column} AS value, count(*) AS count, sum(count(*)) OVER () AS seen
        FROM ({capped}) WHERE {column} IS NOT NULL
        GROUP BY value ORDER BY count DESC, value LIMIT {int(limit)}
    """).fetchall()
    return {
        "key": key,
        "total": len(rows),
        "sampled": bool(rows) and rows[0][2] >= SUGGESTION_ROWS,
        "values": [{"value": str(v), "count": n} for v, n, _ in rows],
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
        ["raw", cache_key, feature_type, *(f"{e}/{s}" for e, s in parts)]
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
            _sweep_tag_cache(root)
            return root / f"{digest}.parquet"
        except OSError as e:
            logger.info("tag cache unavailable at %s: %s", root, e)
    raise OSError("no writable location for the tag cache")


def _version_date(version: str) -> str:
    """A mirror version as a date a person reads: '20261011' -> '11 Oct 2026'."""
    try:
        day = datetime.strptime(version, "%Y%m%d")
    except ValueError:
        return version
    return f"{day.day} {day:%b %Y}"


def lineage_text(
    source: Source,
    type_key: str,
    parts: list[tuple[str, str]],
    filters: List["TagFilter"],
    match_mode: str = "all",
    where: str | None = None,
) -> str:
    """Where the layer's data came from, in a sentence for the metadata panel."""
    if source.tagged:
        places = [unit.replace("-", " ").title() for unit, _ in parts]
        named = (
            f"{', '.join(places[:-1])} and {places[-1]}"
            if len(places) > 1
            else "".join(places)
        )
        latest = max((version for _, version in parts), default="")
        text = f"OpenStreetMap data for {named}, as of {_version_date(latest)}."
    else:
        release = parts[0][1] if parts else ""
        text = f"Overture Maps {type_key.replace('_', ' ')}, release {release}."
    if where:
        return f"{text} Only features matching: {where}"
    if filters:
        conditions = [
            f"{f.key} is {' or '.join(f.values)}" if f.values else f"{f.key} is set"
            for f in filters
        ]
        joiner = " and " if match_mode == "all" else " or "
        text += f" Only features where {joiner.join(conditions)}."
    return text


def _sweep_tag_cache(root: Path) -> None:
    """Delete cached tag lists nobody has read for an hour, at most once an hour.

    Run from a request rather than a timer. A file is touched on every read, so
    only lists out of use go -- an old mirror version's, an area left behind.
    """
    global _tag_cache_swept
    now = time.time()
    if now - _tag_cache_swept < TAG_CACHE_MAX_IDLE_SECONDS:
        return
    with _tag_cache_sweep_lock:
        if now - _tag_cache_swept < TAG_CACHE_MAX_IDLE_SECONDS:
            return
        _tag_cache_swept = now
        for path in root.glob("*.parquet"):
            try:
                if now - path.stat().st_mtime > TAG_CACHE_MAX_IDLE_SECONDS:
                    path.unlink(missing_ok=True)
            except OSError:
                pass


def _raw_tags_sql(files: list[str], envelope: tuple, prefilter: str) -> str:
    """Every feature's unparsed tags in the envelope, for suggestions only."""
    xmin, ymin, xmax, ymax = envelope
    listed = ", ".join(f"'{_quote(f)}'" for f in files)
    return f"""SELECT all_tags FROM read_parquet([{listed}], union_by_name = true)
        WHERE bbox.xmin <= {xmax} AND bbox.xmax >= {xmin}
          AND bbox.ymin <= {ymax} AND bbox.ymax >= {ymin} AND {prefilter}"""


def _count_tags(
    con: "Any", source: str, key: str | None, limit: int
) -> tuple[list, int]:
    """The commonest keys or values, and how many were counted before the limit.

    Read from the raw hstore text with a regex: parsing every feature's tags
    into a map was most of a ten-second first call, and a list needs no map.
    """
    picked = (
        """unnest(regexp_extract_all(all_tags, '"([^"]+)"=>', 1))"""
        if key is None
        else f"""regexp_extract(all_tags, '"{_quote(re.escape(key))}"=>"((?:[^"\\\\]|\\\\.)*)"', 1)"""
    )
    # A colon marks a sub-attribute by OSM convention -- `addr:street`,
    # `contact:phone`, `crossing:markings` describe a feature rather than say
    # what it is, and they crowd out the keys worth querying: in Munich the six
    # commonest keys are all `addr:*`. Only when listing the keys; a value list
    # is already about one key the user chose.
    noise = "" if key else " AND value NOT LIKE '%:%'"
    rows = con.execute(f"""
        WITH picked AS (SELECT {picked} AS value FROM ({source}))
        SELECT value, count(*) AS count, sum(count(*)) OVER () AS seen FROM picked
        WHERE value IS NOT NULL AND value <> ''{noise}
        GROUP BY value ORDER BY count DESC, value LIMIT {int(limit)}
    """).fetchall()
    return [(v, n) for v, n, _ in rows], int(rows[0][2]) if rows else 0


def mirror_values(
    con: "Any",
    *,
    area: dict,
    feature_type: str,
    key: str | None = None,
    limit: int = 100,
    source_name: str = "osm",
    quick: bool = False,
) -> dict:
    """Which attributes, or which values of one attribute, the mirror holds here.

    OSM tags or Overture columns alike: the source decides how they are read.

    Scoped to the area on purpose: over a whole country this would mean parsing
    every row, while a district is a few thousand and answers at once. It is
    also the only list worth showing -- a key that exists in Hamburg helps
    nobody drawing a box in Munich.
    """
    import hashlib

    ensure_s3(con)
    src = SOURCES[source_name]
    envelope = area_envelope(con, area_table(con, area))
    files, parts = covering(con, pointer(con, src), src, feature_type, envelope)
    if not files:
        return {"key": key, "total": 0, "values": []}

    if not src.tagged:
        return _column_values(con, src, files, feature_type, envelope, key, limit)

    # Every feature's tags in the area, parsed once and kept. Building it is the
    # slow part -- the whole area is read and every hstore parsed -- and the
    # form asks repeatedly: the keys, then the values of each key a user tries.
    # Without this each of those reads the same rows from the mirror again.
    cache = None
    cache_key = hashlib.sha256(json.dumps(area, sort_keys=True).encode()).hexdigest()
    try:
        cache = _tag_cache_path(cache_key, feature_type, parts, envelope)
    except OSError as e:
        logger.warning("tag cache disabled: %s", e)
    if quick and not (cache is not None and cache.exists()):
        con.execute(
            "CREATE OR REPLACE TEMP TABLE quick_tags AS "
            f"{_raw_tags_sql(files, envelope, 'TRUE')} LIMIT {QUICK_ROWS}"
        )
        complete = (
            con.execute("SELECT count(*) FROM quick_tags").fetchone()[0] < QUICK_ROWS
        )
        # Fewer than the cap means the area was read whole: that is the full
        # answer, so it is kept as the cache and the caller needs no second read.
        # A capped one is never cached -- a partial read must not stand in for
        # the full list.
        if complete and cache is not None:
            tmp = cache.with_suffix(".tmp.parquet")
            con.execute(f"COPY quick_tags TO '{tmp}' (FORMAT PARQUET)")
            os.replace(tmp, cache)
        rows, _ = _count_tags(con, "SELECT all_tags FROM quick_tags", key, limit)
        con.execute("DROP TABLE quick_tags")
        return {
            "key": key,
            "total": len(rows),
            "sampled": not complete,
            "complete": complete,
            "values": [{"value": v, "count": n} for v, n in rows],
        }
    if cache is not None and cache.exists():
        try:
            cache.touch()
        except OSError:
            pass
        source = f"SELECT all_tags FROM read_parquet('{cache}')"
    else:
        # The envelope by each feature's bbox, not the area itself and not even
        # ST_Intersects: a key present just outside the boundary is present
        # inside it too. The extract still clips exactly; this only decides
        # what the dropdowns offer.
        source = f"{_raw_tags_sql(files, envelope, 'TRUE')} LIMIT {SUGGESTION_ROWS}"
        if cache is not None:
            tmp = cache.with_suffix(".tmp.parquet")
            con.execute(f"COPY ({source}) TO '{tmp}' (FORMAT PARQUET)")
            os.replace(tmp, cache)
            source = f"SELECT all_tags FROM read_parquet('{cache}')"

    # A capped read makes counts of a sample, not of the area; the caller is
    # told, so it never shows a sample's number as a total.
    sampled = (
        con.execute(f"SELECT count(*) FROM ({source})").fetchone()[0] >= SUGGESTION_ROWS
    )
    rows, _ = _count_tags(con, source, key, limit)
    if key is not None and not rows:
        # A key too rare for the sample: read only features carrying it.
        quoted_key = _quote(re.escape(key))
        prefilter = f"regexp_matches(all_tags, '\"{quoted_key}\"=>')"
        rows, seen = _count_tags(
            con,
            f"{_raw_tags_sql(files, envelope, prefilter)} LIMIT {RARE_KEY_ROWS}",
            key,
            limit,
        )
        sampled = seen >= RARE_KEY_ROWS
    return {
        "key": key,
        "total": len(rows),
        "sampled": sampled,
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
        json_schema_extra=ui_field(section="input", field_order=1),
    )
    values: List[str] = Field(
        default_factory=list,
        description=(
            "Values to match, any of them. None selected matches every feature "
            "carrying the key."
        ),
        json_schema_extra=ui_field(section="input", field_order=2),
    )


class DataIntegrationParams(ToolInputBase):
    """What to extract, from where, and for which area.

    Shown as the panel's own description, so it says what the tool needs rather
    than what it is.
    """

    model_config = ConfigDict(
        json_schema_extra=ui_sections(SECTION_INPUT, SECTION_OUTPUT)
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
    overture_type: Literal[
        "places",
        "divisions",
        "buildings",
        "land_use",
        "land",
        "water_areas",
        "waterways",
        "infrastructure_points",
        "infrastructure_lines",
        "infrastructure_areas",
    ] = Field(
        "places",
        description="Which kind of feature to extract",
        json_schema_extra=ui_field(
            section="input",
            field_order=3,
            visible_when={"source": "overture"},
            enum_labels={k: f"enums.overture_type.{k}" for k in OVERTURE_TYPES},
        ),
    )
    match_mode: Literal["all", "any"] = Field(
        "all",
        description=(
            "Whether a feature must satisfy every condition or just one of them"
        ),
        json_schema_extra=ui_field(
            section="input",
            field_order=4,
            enum_labels={
                "all": "Match all filters",
                "any": "Match at least one filter",
            },
        ),
    )
    tag_filters: List[TagFilter] = Field(
        default_factory=list,
        description="Tag conditions, combined with AND. None returns every feature in the area.",
        json_schema_extra=ui_field(
            section="input",
            field_order=5,
            repeatable=True,
        ),
    )
    area: dict = Field(
        ...,
        description=(
            "GeoJSON polygon bounding the extract: a map view, a region, a "
            "buffered point or a drawn shape"
        ),
        json_schema_extra=ui_field(section="input", field_order=1, hidden=True),
    )
    where: str | None = Field(
        None,
        max_length=4000,
        description=(
            "SQL condition used instead of the tag filters, e.g. "
            "tags['amenity'] = 'school'"
        ),
        json_schema_extra=ui_field(section="input", field_order=6),
    )


def _quote(value: str) -> str:
    return value.replace("'", "''")


def _column_sql(
    filters: List[TagFilter], joiner: str, source: Source, type_key: str
) -> tuple[str, str]:
    """The same pair for a typed source: no prefilter, a plain comparison.

    Nothing to pre-filter and nothing to parse -- the attribute is already a
    column, so the only test is the test.
    """
    if not filters:
        return "TRUE", "TRUE"
    exact = []
    for f in filters:
        column = source.field_sql(type_key, f.key)
        if not f.values:
            exact.append(f"{column} IS NOT NULL")
        else:
            listed = ", ".join(f"'{_quote(v)}'" for v in f.values)
            # Not `IN`: over S3 a one-value IN becomes `=`, which DuckDB pushes
            # into the Parquet reader, and the reader then fetches each row
            # group's other columns separately -- 718 requests instead of 178
            # for Munich, five seconds instead of one. A function stays out.
            exact.append(f"list_contains([{listed}], {column})")
    return "TRUE", joiner.join(exact)


def filter_sql(
    filters: List[TagFilter],
    source: Source,
    match_mode: str = "all",
    type_key: str = "places",
) -> tuple[str, str]:
    """(cheap prefilter before parsing, exact test after)."""
    joiner = " AND " if match_mode == "all" else " OR "
    if source.tagged:
        return _tag_sql(filters, joiner)
    return _column_sql(filters, joiner, source, type_key)


def _tag_sql(filters: List[TagFilter], joiner: str = " AND ") -> tuple[str, str]:
    """(cheap prefilter on the raw text, exact test on the parsed map)."""
    if not filters:
        return "TRUE", "TRUE"
    pre, exact = [], []
    for f in filters:
        key = _quote(re.escape(f.key))
        quoted = f"'{_quote(f.key)}'"
        if not f.values:
            pre.append(f"regexp_matches(all_tags, '\"{key}\"=>')")
            exact.append(f"map_contains(tags, {quoted})")
            continue
        # Several values on one key is "any of them": a feature has one value
        # per key, so AND-ing them could never match anything.
        alts = "|".join(re.escape(v) for v in f.values)
        pre.append(f'regexp_matches(all_tags, \'"{key}"=>"({_quote(alts)})"\')')
        listed = ", ".join(f"'{_quote(v)}'" for v in f.values)
        exact.append(f"tags[{quoted}] IN ({listed})")
    return joiner.join(pre), joiner.join(exact)


class DataIntegrationRunner(BaseToolRunner[DataIntegrationParams]):
    """Read the mirror for an area and write one layer."""

    default_output_name = "Extracted Features"
    output_geometry_type = "point"

    def get_feature_layer_type(self: Self, params: DataIntegrationParams) -> str:
        """A dataset brought in from a source, like an import -- not a tool's result."""
        return "standard"

    def process(
        self: Self, params: DataIntegrationParams, temp_dir: Path
    ) -> tuple[Path, DatasetMetadata]:
        con = self.duckdb_con
        ensure_s3(con)

        src = SOURCES[params.source]
        type_key = params.feature_type if src.tagged else params.overture_type
        self.output_geometry_type = src.geometry_of(type_key)

        area = area_table(con, params.area)
        envelope = area_envelope(con, area)
        area_geom = area_geom_column(con, area)
        files, parts = covering(con, pointer(con, src), src, type_key, envelope)
        if not files:
            raise ValueError("The mirror holds no data for this area.")

        if params.where:
            prefilter, exact = "TRUE", checked_where(con, files, src, params.where)
        else:
            prefilter, exact = filter_sql(
                params.tag_filters, src, params.match_mode, type_key
            )
        prefilter = f"({prefilter}) AND {src.geometry_filter(type_key)}"
        out = temp_dir / "output.parquet"
        staged = temp_dir / "staged.parquet"
        columns = {
            str(r[0]): str(r[1])
            for r in con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{_quote(files[0])}')"
            ).fetchall()
        }
        # GDAL fills osm_id only for relations on the polygon layer; a polygon
        # from a way has its id in osm_way_id and osm_id NULL. Keyed on osm_id
        # alone, every way-polygon fell into one group and one row was kept.
        identity = (
            'c."osm_id", c."osm_way_id"'
            if src.tagged and "osm_way_id" in columns
            else f'c."{src.id_column}"'
        )
        if src.tagged:
            selected = "c.* EXCLUDE (tags, bbox, filename)"
        else:
            plain = overture_plain_columns(columns)
            # Right after the id, so they are the first thing a popup shows; the
            # nested originals stay for a download's full records.
            selected = ", ".join(
                [
                    f'c."{src.id_column}"',
                    *plain,
                    f'c.* EXCLUDE ("{src.id_column}", bbox, filename)',
                ]
            )
        # Two spatial tests, not one: the envelope prunes row groups before
        # anything is read, the area itself is what the user asked for. The
        # dedup is for a feature at a continent seam, which both continents carry.
        con.execute(f"""
            COPY (
                WITH area AS (SELECT ST_Union_Agg("{area_geom}") AS g FROM {area}),
                candidates AS ({candidates_sql(files, src, envelope, prefilter)})
                SELECT {selected}, c.filename AS _mirror_file
                FROM candidates c, area
                WHERE {exact} AND ST_Intersects(c."{src.geom}", area.g)
                QUALIFY row_number() OVER (PARTITION BY {identity} ORDER BY {identity}) = 1
                LIMIT {MAX_FEATURES + 1}
            ) TO '{staged}' (FORMAT PARQUET)
        """)
        # Which files supplied rows, so the lineage names only those: a unit's
        # bbox can cover the area without the unit holding anything in it
        # (France's, Corsica to the Belgian border, covers Frankfurt).
        supplied = {
            str(r[0])
            for r in con.execute(
                f"SELECT DISTINCT _mirror_file FROM read_parquet('{staged}')"
            ).fetchall()
        }
        parts = [
            (unit, version)
            for unit, version in parts
            if any(f.startswith(f"{src.mirror}/{unit}/{version}/") for f in supplied)
        ]
        con.execute(
            f"COPY (SELECT * EXCLUDE (_mirror_file) FROM read_parquet('{staged}')) "
            f"TO '{out}' (FORMAT PARQUET)"
        )
        staged.unlink(missing_ok=True)
        count = con.execute(f"SELECT count(*) FROM read_parquet('{out}')").fetchone()
        features = int(count[0]) if count else 0
        if features > MAX_FEATURES:
            raise ValueError(
                f"The area holds more than {MAX_FEATURES:,} matching features. "
                "Pick a smaller area or add filters."
            )
        read = ", ".join(f"{e} {sid}" for e, sid in parts)
        conditions = params.where or ", ".join(
            f"{f.key}={','.join(f.values)}" if f.values else f.key
            for f in params.tag_filters
        )
        provider = "OpenStreetMap" if src.tagged else "Overture Maps"
        licence, attribution = src.licence_of(type_key)
        logger.info(
            "extracted %s feature(s) from the %s mirror (%s)%s — %s, %s",
            features,
            provider,
            read,
            f", where {conditions}" if conditions else "",
            attribution,
            licence,
        )
        # The catalog record's own keys, so the dataset card reads both the same.
        self._provenance = {
            "license": licence,
            "attribution": attribution,
            "processing:lineage": lineage_text(
                src,
                type_key,
                parts,
                params.tag_filters,
                params.match_mode,
                params.where,
            ),
            "publisher": provider,
            "source_url": (
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

    Under ``other_properties.provenance``: a layer has no metadata column of its
    own (only a bundle does), and ``catalog_item`` means a link to a catalog
    record, which a copy drops -- this has to survive a copy.
    """
    assert runner.settings is not None
    pool = await runner.get_postgres_pool()
    schema = runner.settings.customer_schema
    # The project link this job just made keeps its own copy of the layer's
    # other_properties, taken before this ran, so the licence goes into that
    # copy too -- only this layer's links, which exist for seconds at this point.
    for table, column in (("layer", "id"), ("layer_project", "layer_id")):
        await pool.execute(
            f"UPDATE {schema}.{table} "
            "SET other_properties = COALESCE(other_properties, '{}'::jsonb) "
            f"|| jsonb_build_object('provenance', $1::jsonb) WHERE {column} = $2::uuid",
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
