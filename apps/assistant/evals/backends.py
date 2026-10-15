"""Fixed backends for the evals: what the tools talk to (decision E16).

The catalog tools reach the real catalog app over its own fixture catalog
(apps/catalog/tests/fixtures/gen_catalog.py, seed 42) plus the named rows
below, through an ASGI transport. The project tools reach canned core,
geoapi and processes answers for one fixture project; the answers are
computed from fixed, filter-aware feature tables, so the oracles that grade
the answers read the same tables.
"""

import contextlib
import importlib.util
import json
import os
import random
import re
import statistics
import sys
from collections import Counter
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx
from fastapi import FastAPI

from assistant.tools.http import ServiceClients
from assistant.tools.testing import Recorder, RecordingTransport, fake_clients
from evals.tasks import Oracle

ROOT = Path(__file__).resolve().parents[3]
GEN_CATALOG = ROOT / "apps" / "catalog" / "tests" / "fixtures" / "gen_catalog.py"

# ---- catalog ------------------------------------------------------------------

#: Named rows the catalog tasks expect: id, topic, region, category, license,
#: language, type, index (the generator's row index: title year 2018 + index % 9).
EVAL_ROWS: tuple[tuple[str, str, str, str, str, str, str, int], ...] = (
    (
        "eval-ladesaeulen-leipzig",
        "Ladesäulen",
        "Leipzig",
        "transportation",
        "dl-de-by-2.0",
        "de",
        "feature",
        1001,
    ),
    (
        "eval-strassenbaeume-koeln",
        "Straßenbäume",
        "Köln",
        "environment",
        "CC0-1.0",
        "de",
        "feature",
        1002,
    ),
    (
        "eval-laermkarte-hamburg",
        "Lärmkarte Straßenverkehr",
        "Hamburg",
        "environment",
        "dl-de-zero-2.0",
        "de",
        "feature",
        1003,
    ),
    (
        "eval-bike-sharing-berlin",
        "Bike sharing stations",
        "Berlin",
        "transportation",
        "ODbL-1.0",
        "en",
        "feature",
        1004,
    ),
    (
        "eval-hochwasser-dresden",
        "Überschwemmungsgebiete",
        "Dresden",
        "environment",
        "dl-de-by-2.0",
        "de",
        "feature",
        1005,
    ),
    (
        "eval-einwohner-muenchen",
        "Einwohner nach Stadtbezirk",
        "München",
        "people",
        "CC-BY-4.0",
        "de",
        "table",
        1006,
    ),
    (
        "eval-solardach-stuttgart",
        "Solarkataster Dachflächen",
        "Stuttgart",
        "environment",
        "CC-BY-4.0",
        "de",
        "feature",
        1007,
    ),
    (
        "eval-ladesaeulen-bayern",
        "Ladesäulen",
        "Bayern",
        "transportation",
        "CC-BY-4.0",
        "de",
        "feature",
        1008,
    ),
    (
        "eval-radverkehr-zaehlstellen-frankfurt",
        "Radverkehr Zählstellen",
        "Frankfurt am Main",
        "transportation",
        "dl-de-by-2.0",
        "de",
        "feature",
        1009,
    ),
    (
        "eval-wohnungsbau-nrw",
        "Wohnungsbaupotenziale",
        "Nordrhein-Westfalen",
        "landuse",
        "other",
        "de",
        "feature",
        1010,
    ),
)


def _generator() -> ModuleType:
    # Not a package: loaded by path, registered first because its dataclasses
    # look their module up in sys.modules (as plan 3's conftest does).
    spec = importlib.util.spec_from_file_location("catalog_fixture_gen", GEN_CATALOG)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["catalog_fixture_gen"] = module
    spec.loader.exec_module(module)
    return module


#: The same playground dataset in four places, its text naming none of them:
#: only a search filtered by region tells the Munich one apart.
#: id, west, south, east, north.
REGION_ROWS: tuple[tuple[str, float, float, float, float], ...] = (
    ("eval-spielplaetze-muenchen", 11.45, 48.12, 11.55, 48.18),
    ("eval-spielplaetze-hamburg", 9.95, 53.52, 10.05, 53.58),
    ("eval-spielplaetze-koeln", 6.90, 50.90, 7.00, 50.96),
    ("eval-spielplaetze-dresden", 13.70, 51.02, 13.80, 51.08),
)
#: The Munich region (district-free city) the playground rows are found by.
MUNICH_REGION = (
    "DE212",
    "München, Kreisfreie Stadt",
    3,
    "DE",
    11.36,
    48.06,
    11.72,
    48.25,
)

#: Where the named rows' places really are (west, south, east, north), so a
#: search filtered by region finds them as it would in the real catalog.
PLACE_BOXES: dict[str, tuple[float, float, float, float]] = {
    "Leipzig": (12.24, 51.24, 12.54, 51.45),
    "Köln": (6.77, 50.83, 7.16, 51.09),
    "Hamburg": (9.73, 53.39, 10.33, 53.74),
    "Berlin": (13.09, 52.34, 13.76, 52.68),
    "Dresden": (13.58, 50.97, 13.97, 51.18),
    "München": (11.36, 48.06, 11.72, 48.25),
    "Stuttgart": (9.04, 48.69, 9.32, 48.87),
    "Frankfurt am Main": (8.47, 50.02, 8.80, 50.23),
    "Bayern": (8.98, 47.27, 13.84, 50.56),
    "Nordrhein-Westfalen": (5.87, 50.32, 9.46, 52.53),
}
#: The cities as regions (NUTS level 3), as catalog_find_region knows them.
CITY_REGIONS: tuple[tuple[str, str, str], ...] = (
    ("DED51", "Leipzig, Kreisfreie Stadt", "Leipzig"),
    ("DEA23", "Köln, Kreisfreie Stadt", "Köln"),
    ("DE600", "Hamburg", "Hamburg"),
    ("DE300", "Berlin", "Berlin"),
    ("DED21", "Dresden, Kreisfreie Stadt", "Dresden"),
    ("DE111", "Stuttgart, Stadtkreis", "Stuttgart"),
    ("DE712", "Frankfurt am Main, Kreisfreie Stadt", "Frankfurt am Main"),
)
#: The generated states and country, in their real extent instead of a random
#: rectangle, so filtering by a state finds what lies in it.
STATE_BOXES: dict[str, tuple[float, float, float, float]] = {
    "DE": (5.87, 47.27, 15.04, 55.06),
    "DE1": (7.51, 47.53, 10.50, 49.79),
    "DE2": PLACE_BOXES["Bayern"],
    "DE3": PLACE_BOXES["Berlin"],
    "DE6": PLACE_BOXES["Hamburg"],
    "DE7": (7.77, 49.39, 10.24, 51.66),
    "DEA": PLACE_BOXES["Nordrhein-Westfalen"],
    "DED": (11.87, 50.17, 15.04, 51.68),
}


def _inside(
    box: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """A footprint in the middle of a place's box."""
    west, south, east, north = box
    dx, dy = (east - west) / 4, (north - south) / 4
    return west + dx, south + dy, east - dx, north - dy


def _box(
    west: float, south: float, east: float, north: float
) -> tuple[str, dict[str, Any]]:
    ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
    wkt = "POLYGON((" + ",".join(f"{x} {y}" for x, y in ring) + "))"
    return wkt, {"type": "Polygon", "coordinates": [ring]}


def eval_rows() -> list[Any]:
    """Each named row as an item plus its one-layer dataset (a Collection)."""
    gen = _generator()
    rows: list[Any] = []
    for (
        row_id,
        topic,
        region,
        category,
        license_id,
        language,
        row_type,
        index,
    ) in EVAL_ROWS:
        item = gen._make_row(
            random.Random(index),
            index,
            topic=topic,
            region=region,
            license_id=license_id,
            category=category,
            language=language,
            row_type=row_type,
        )
        wkt, geojson = _box(*_inside(PLACE_BOXES[region]))
        item = replace(
            item,
            id=row_id,
            parquet_url=f"{gen.PARQUET_ASSET_BASE_URL}/{row_id}.parquet",
            geometry_wkt=wkt,
            geometry_geojson=geojson,
        )
        dataset = gen._dataset_collection_for(item)
        rows.extend([replace(item, collection=dataset.id), dataset])
    for n, (row_id, west, south, east, north) in enumerate(REGION_ROWS):
        wkt, geojson = _box(west, south, east, north)
        item = replace(
            gen._make_row(
                random.Random(2001 + n),
                2001 + n,
                topic="Spielplätze",
                region="Stadtgebiet",
                license_id="dl-de-by-2.0",
                category="places",
                language="de",
                row_type="feature",
            ),
            id=row_id,
            title="Öffentliche Spielplätze",
            description=(
                "Öffentliche Spielplätze im Stadtgebiet mit Lage, Ausstattung "
                "und Altersgruppen."
            ),
            geometry_wkt=wkt,
            geometry_geojson=geojson,
            parquet_url=f"{gen.PARQUET_ASSET_BASE_URL}/{row_id}.parquet",
        )
        dataset = gen._dataset_collection_for(item)
        rows.extend([replace(item, collection=dataset.id), dataset])
    return rows


def write_eval_catalog(path: Path) -> None:
    gen = _generator()
    build_document = gen.build_document

    def with_dataset_metadata(
        row: Any, member_bboxes: list[list[float]] | None = None
    ) -> Any:
        # The generator keeps a collection's themes only under ``summaries`` and
        # no language at all, but the mirror reads a dataset's category and
        # language from the collection's own ``themes`` and ``language`` (as the
        # published catalog has them). Without them every dataset has no theme.
        document = build_document(row, member_bboxes)
        if document.get("type") == "Collection":
            document = {
                **document,
                "themes": document["summaries"]["themes"],
                "language": {"code": row.language},
            }
        return document

    setattr(gen, "build_document", with_dataset_metadata)
    gen.write_catalog(path, extra_rows=eval_rows())
    nuts_id, name, level, country, *box = MUNICH_REGION
    cities = [
        (city_id, city_name, 3, "DE", _box(*PLACE_BOXES[place])[0])
        for city_id, city_name, place in CITY_REGIONS
    ]
    gen.write_nuts(
        path,
        extra_regions=[(nuts_id, name, level, country, _box(*box)[0]), *cities],
        replace_regions={key: _box(*value)[0] for key, value in STATE_BOXES.items()},
    )


@contextlib.contextmanager
def _without_catalog_env() -> Iterator[None]:
    """A developer's .env must not reach the catalog's settings (an aliased
    variable plus a keyword is an extra-input error)."""
    from catalog.config import CatalogSettings

    names = set()
    for settings_field in CatalogSettings.model_fields.values():
        alias = settings_field.validation_alias
        for name in getattr(alias, "choices", [alias]) if alias is not None else []:
            if isinstance(name, str):
                names.add(name)
    saved = {name: os.environ.pop(name) for name in names if name in os.environ}
    try:
        yield
    finally:
        os.environ.update(saved)


def catalog_app(path: Path) -> FastAPI:
    from catalog.app import create_app
    from catalog.config import CatalogSettings
    from catalog.store import CatalogStore

    with _without_catalog_env():
        settings = CatalogSettings(**{"data_dir": path, "AUTH": False})
    app: FastAPI = create_app(settings)
    # What the catalog's lifespan does; an ASGI transport runs no lifespan.
    app.state.store = CatalogStore(settings)
    app.state.preview_reader = None
    app.state.asset_reader = None
    return app


# ---- fixture project ----------------------------------------------------------

PROJECT_ID = "00000000-0000-0000-0000-0000000005e1"
PROJECT_NAME = "Radverkehr Leipzig"
BEZIRKE = (
    "Mitte",
    "Nordost",
    "Ost",
    "Südost",
    "Süd",
    "Südwest",
    "West",
    "Alt-West",
    "Nordwest",
    "Nord",
)


@dataclass(frozen=True)
class FixtureLayer:
    layer_project_id: int
    layer_id: str
    name: str
    geometry: str  # point, line, polygon
    fields: Mapping[str, str]  # name -> JSON type
    features: tuple[dict[str, Any], ...]  # properties plus "_at": (lon, lat)
    locked: bool = False
    group_id: int | None = None


def _at(rng: random.Random) -> tuple[float, float]:
    return (round(rng.uniform(12.25, 12.55), 5), round(rng.uniform(51.25, 51.45), 5))


def _build_layers() -> tuple[FixtureLayer, ...]:
    rng = random.Random(7)
    arts = (
        ["Radweg"] * 32
        + ["Radfahrstreifen"] * 20
        + ["Schutzstreifen"] * 16
        + ["Fahrradstraße"] * 12
    )
    rng.shuffle(arts)
    radwege = tuple(
        {
            "art": art,
            "laenge_m": round(rng.uniform(50, 2500), 1),
            "baujahr": rng.randint(1990, 2024),
            "beleuchtet": rng.random() < 0.6,
            "bezirk": rng.choice(BEZIRKE),
            "_at": _at(rng),
        }
        for art in arts
    )
    bezirke = tuple(
        {
            "name": name,
            "einwohner": rng.randint(20_000, 90_000),
            "flaeche_m2": round(rng.uniform(8e6, 40e6), 1),
            "_at": _at(rng),
        }
        for name in BEZIRKE
    )
    racks_by_district = [
        b
        for b, n in zip(BEZIRKE, (24, 18, 15, 13, 12, 11, 9, 8, 6, 4), strict=True)
        for _ in range(n)
    ]
    rng.shuffle(racks_by_district)
    staender = tuple(
        {
            "stellplaetze": rng.randint(2, 40),
            "ueberdacht": rng.random() < 0.3,
            "bezirk": b,
            "_at": _at(rng),
        }
        for b in racks_by_district
    )
    planung = tuple({"status": "Entwurf", "_at": _at(rng)} for _ in range(5))
    return (
        FixtureLayer(
            21,
            "e1000000-0000-0000-0000-000000000021",
            "Radwege",
            "line",
            {
                "art": "string",
                "laenge_m": "number",
                "baujahr": "integer",
                "beleuchtet": "boolean",
                "bezirk": "string",
            },
            radwege,
            group_id=1,
        ),
        FixtureLayer(
            22,
            "e1000000-0000-0000-0000-000000000022",
            "Bezirke",
            "polygon",
            {"name": "string", "einwohner": "integer", "flaeche_m2": "number"},
            bezirke,
        ),
        FixtureLayer(
            23,
            "e1000000-0000-0000-0000-000000000023",
            "Fahrradständer",
            "point",
            {"stellplaetze": "integer", "ueberdacht": "boolean", "bezirk": "string"},
            staender,
            group_id=1,
        ),
        FixtureLayer(
            24,
            "e1000000-0000-0000-0000-000000000024",
            "Interne Planung",
            "polygon",
            {"status": "string"},
            planung,
            locked=True,
        ),
    )


FIXTURE_LAYERS = _build_layers()
_BY_ID = {layer.layer_id: layer for layer in FIXTURE_LAYERS}


def _layer_named(name: str | None) -> FixtureLayer:
    for layer in FIXTURE_LAYERS:
        if layer.name == name:
            return layer
    raise KeyError(f"no fixture layer {name!r}")


# CQL2-JSON as plan 3's filters produce it (=, <>, <, <=, >, >=, in, like,
# isNull, not, and, or; date-times as {"timestamp": ...}).
def _value(arg: Any, properties: Mapping[str, Any]) -> Any:
    if isinstance(arg, dict) and "property" in arg:
        return properties.get(arg["property"])
    if isinstance(arg, dict) and "timestamp" in arg:
        return arg["timestamp"]
    return arg


def _like(pattern: str) -> str:
    return "".join(
        ".*" if c == "%" else "." if c == "_" else re.escape(c) for c in pattern
    )


def matches(
    expression: Mapping[str, Any] | None, properties: Mapping[str, Any]
) -> bool:
    if expression is None:
        return True
    op = expression["op"]
    args = expression.get("args", [])
    if op == "and":
        return all(matches(arg, properties) for arg in args)
    if op == "or":
        return any(matches(arg, properties) for arg in args)
    if op == "not":
        return not matches(args[0], properties)
    left = _value(args[0], properties)
    if op == "isNull":
        return left is None
    if op == "in":
        return left in [_value(arg, properties) for arg in args[1]]
    right = _value(args[1], properties)
    if left is None or right is None:
        return False
    if op == "like":
        # ILIKE: case-insensitive, as the filter tool's contract says.
        return re.fullmatch(_like(str(right)), str(left), re.IGNORECASE) is not None
    comparisons: dict[str, Callable[[Any, Any], bool]] = {
        "=": lambda a, b: a == b,
        "<>": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }
    try:
        return bool(comparisons[op](left, right))
    except TypeError:
        return False


def _selected(layer: FixtureLayer, raw_filter: Any) -> list[dict[str, Any]]:
    expression = json.loads(raw_filter) if isinstance(raw_filter, str) else raw_filter
    return [feature for feature in layer.features if matches(expression, feature)]


def _geometry(layer: FixtureLayer, at: tuple[float, float]) -> dict[str, Any]:
    lon, lat = at
    if layer.geometry == "point":
        return {"type": "Point", "coordinates": [lon, lat]}
    if layer.geometry == "line":
        return {
            "type": "LineString",
            "coordinates": [[lon, lat], [lon + 0.01, lat + 0.005]],
        }
    ring = [
        [lon, lat],
        [lon + 0.02, lat],
        [lon + 0.02, lat + 0.02],
        [lon, lat + 0.02],
        [lon, lat],
    ]
    return {"type": "Polygon", "coordinates": [ring]}


def _public(feature: Mapping[str, Any], fields: list[str] | None) -> dict[str, Any]:
    return {
        k: v
        for k, v in feature.items()
        if not k.startswith("_") and (fields is None or k in fields)
    }


#: A dataset the user's organization already has: a data question should find
#: it next to the catalog's (``core_find`` before ``catalog_search``).
ORG_DATASET = {
    "type": "layer",
    "id": "00000000-0000-0000-0000-00000000da7a",
    "name": "Ladesäulen Stadtwerke Leipzig",
    "description": "Charging points of the municipal utility, updated monthly.",
    "layer_type": "feature",
    "geometry_type": "point",
    "my_role": "viewer",
    "space_kind": "organization",
    "space_name": "Stadt Leipzig",
    "folder_path": ["Verkehr"],
    "matched_on": ["name"],
    "updated_at": "2026-09-01T00:00:00Z",
}


def _content_search(request: httpx.Request) -> httpx.Response:
    """Core's search over what the user can open, as core matches: part of the
    name, case-insensitive."""
    search = request.url.params.get("search", "").casefold()
    types = request.url.params.get("types", "layer").split(",")
    hit = "layer" in types and search in str(ORG_DATASET["name"]).casefold()
    return httpx.Response(
        200, json={"items": [ORG_DATASET] if hit else [], "total": int(hit)}
    )


def _core_routes() -> dict[tuple[str, str], Any]:
    base = f"/api/v2/project/{PROJECT_ID}"
    layers = [
        {
            "id": layer.layer_project_id,
            "layer_id": layer.layer_id,
            "name": layer.name,
            "type": "feature",
            "feature_layer_geometry_type": layer.geometry,
            "layer_project_group_id": layer.group_id,
            "order": order,
            "locked": layer.locked,
        }
        for order, layer in enumerate(FIXTURE_LAYERS)
    ]
    return {
        ("GET", base): {"id": PROJECT_ID, "name": PROJECT_NAME},
        ("GET", f"{base}/layer"): layers,
        ("GET", f"{base}/group"): [
            {"id": 1, "name": "Verkehr", "parent_id": None, "order": 0}
        ],
        # The project has no workflows and no print layouts.
        ("GET", f"{base}/workflow"): [],
        ("GET", f"{base}/report-layout"): [],
        ("GET", "/api/v2/content/search"): _content_search,
        ("GET", "/api/v2/template"): {"items": [], "total": 0},
        ("GET", f"/api/v2/layer/{ORG_DATASET['id']}"): {
            "id": ORG_DATASET["id"],
            "name": ORG_DATASET["name"],
            "type": "feature",
            "feature_layer_geometry_type": "point",
        },
    }


def _geoapi_routes() -> dict[tuple[str, str], Any]:
    routes: dict[tuple[str, str], Any] = {}
    for layer in FIXTURE_LAYERS:
        queryables = {
            "properties": {
                name: {"name": name, "type": kind}
                for name, kind in layer.fields.items()
            }
        }
        queryables["properties"]["geom"] = {
            "$ref": "https://geojson.org/schema/Geometry.json"
        }
        routes[("GET", f"/collections/{layer.layer_id}/queryables")] = queryables

        def items(
            request: httpx.Request, layer: FixtureLayer = layer
        ) -> httpx.Response:
            params = request.url.params
            selected = _selected(layer, params.get("filter"))
            limit = int(params.get("limit", "10"))
            fields = params["properties"].split(",") if "properties" in params else None
            features = [
                {
                    "type": "Feature",
                    "id": index + 1,
                    "geometry": _geometry(layer, feature["_at"]),
                    "properties": _public(feature, fields),
                }
                for index, feature in enumerate(selected[:limit])
            ]
            return httpx.Response(
                200,
                json={
                    "type": "FeatureCollection",
                    "numberMatched": len(selected),
                    "features": features,
                },
            )

        routes[("GET", f"/collections/{layer.layer_id}/items")] = items
    return routes


def _bbox(layer: FixtureLayer, features: list[dict[str, Any]]) -> list[float]:
    lons = [f["_at"][0] for f in features] + [f["_at"][0] + 0.02 for f in features]
    lats = [f["_at"][1] for f in features] + [f["_at"][1] + 0.02 for f in features]
    return [min(lons), min(lats), max(lons), max(lats)]


def _process(name: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    layer = _BY_ID[str(inputs["collection"])]
    selected = _selected(layer, inputs.get("filter"))
    attribute = inputs.get("attribute")
    values = [
        f[attribute] for f in selected if attribute and f.get(attribute) is not None
    ]
    if name == "feature-count":
        return {"count": len(selected)}
    if name == "unique-values":
        counted = Counter(values).most_common(int(inputs.get("limit", 50)))
        return {
            "attribute": attribute,
            "total": len(set(values)),
            "values": [{"value": value, "count": count} for value, count in counted],
        }
    if name == "class-breaks":
        numbers = sorted(float(v) for v in values)
        if not numbers:
            return {
                "attribute": attribute,
                "method": inputs.get("method"),
                "breaks": [],
                "min": None,
                "max": None,
                "mean": None,
                "std_dev": None,
            }
        # ``breaks`` internal points make ``breaks + 1`` classes (the service's contract).
        n = max(int(inputs.get("breaks", 5)), 2)
        if inputs.get("method") == "equal_interval":
            breaks = [
                numbers[0] + (numbers[-1] - numbers[0]) * k / (n + 1)
                for k in range(1, n + 1)
            ]
        else:
            breaks = [
                numbers[min(len(numbers) - 1, len(numbers) * k // (n + 1))]
                for k in range(1, n + 1)
            ]
        return {
            "attribute": attribute,
            "method": inputs.get("method"),
            "breaks": breaks,
            "min": numbers[0],
            "max": numbers[-1],
            "mean": statistics.fmean(numbers),
            "std_dev": statistics.pstdev(numbers),
        }
    if name == "area-statistics":
        areas = [float(f.get("flaeche_m2", 0.0)) for f in selected]
        stats = {
            "sum": sum(areas),
            "min": min(areas, default=None),
            "max": max(areas, default=None),
        }
        result = stats[str(inputs["operation"])]
        return {
            "result": result,
            "total_area": sum(areas),
            "feature_count": len(selected),
            "unit": "m²",
        }
    if name == "extent":
        return {
            "bbox": _bbox(layer, selected) if selected else None,
            "feature_count": len(selected),
        }
    raise ValueError(name)


def _processes_routes() -> dict[tuple[str, str], Any]:
    def answer(name: str) -> Any:
        def respond(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200, json=_process(name, json.loads(request.content)["inputs"])
            )

        return respond

    return {
        ("POST", f"/processes/{name}/execution"): answer(name)
        for name in (
            "feature-count",
            "unique-values",
            "class-breaks",
            "area-statistics",
            "extent",
        )
    }


class Backends:
    """One eval run's backends; ``clients()`` gives each task fresh recorders."""

    def __init__(self, catalog_dir: Path) -> None:
        self.catalog = catalog_app(catalog_dir)

    def close(self) -> None:
        """Close the catalog's DuckDB connection (the app's lifespan never runs)."""
        self.catalog.state.store.snapshot().con.close()

    def clients(self) -> tuple[ServiceClients, dict[str, list[httpx.Request]]]:
        core, geoapi, processes = (
            Recorder(_core_routes()),
            Recorder(_geoapi_routes()),
            Recorder(_processes_routes()),
        )
        catalog = RecordingTransport(httpx.ASGITransport(app=self.catalog))
        services = fake_clients(
            core=core, geoapi=geoapi, processes=processes, catalog=catalog
        )
        requests = {
            "core": core.requests,
            "geoapi": geoapi.requests,
            "processes": processes.requests,
            "catalog": catalog.requests,
        }
        return services, requests

    async def catalog_count(self, params: Mapping[str, Any]) -> int:
        transport = httpx.ASGITransport(app=self.catalog)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://catalog"
        ) as client:
            response = await client.get(
                "/stac/collections", params={**params, "limit": 1}
            )
            response.raise_for_status()
            return int(response.json()["numberMatched"])

    def project_value(self, oracle: Oracle) -> float | str:
        layer = _layer_named(oracle.layer)
        selected = [f for f in layer.features if matches(oracle.filter, f)]
        if oracle.op == "count":
            return float(len(selected))
        values = [
            f[oracle.field]
            for f in selected
            if oracle.field and f.get(oracle.field) is not None
        ]
        if oracle.op == "top":
            return str(Counter(values).most_common(1)[0][0])
        if oracle.op == "distinct":
            return float(len(set(values)))
        numbers = [float(v) for v in values]
        if oracle.op == "sum":
            return sum(numbers)
        if oracle.op == "min":
            return min(numbers)
        if oracle.op == "max":
            return max(numbers)
        return statistics.fmean(numbers)
