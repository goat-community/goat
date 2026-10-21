"""The read-only project pack (spec §7.2, §9.1.1, §10).

The read tools take a project ID, defaulting to the project of the page, so other
projects the user can open are readable as sources. The map-view proposal is the
exception: it only targets the project that is open.

Layers are always resolved through core's layer list of that project, with the
user's token: core checks the project and marks layers the user cannot read as
locked. Only layer IDs from that list ever reach geoapi and processes, and never
a locked one. This matters because neither checks per layer today: processes
runs its sync analytics for any caller, and geoapi's read check only logs unless
ENFORCE_READ_AUTHZ is set. So the model never passes a layer UUID, only
(project_id, layer_project_id).
"""

import asyncio
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai.exceptions import ToolFailed

from assistant.context import ProjectMapContext, project_of
from assistant.surfaces import Surface
from assistant.tools.filters import (
    FILTER_EXAMPLES,
    FILTERABLE_KINDS,
    FeatureFilter,
    describe_filter,
    field_kind,
    to_cql2,
    unknown_field,
)
from assistant.tools.http import ServiceError
from assistant.tools.policy import LOW_CARDINALITY_LIMIT, Withheld
from assistant.tools.proposals import (
    MapCamera,
    MapViewPayload,
    Proposal,
    ProposalRow,
    ProposalShown,
    ProposalTarget,
    proposal_row,
    show,
)
from assistant.tools.runtime import InputInvalid, ToolEnv, ToolSpec

#: Every project mode, and pages without a project (Home, content, settings),
#: where the tools need an explicit project_id (Decision T16).
PROJECT_SURFACES: frozenset[Surface] = frozenset(
    {"project.map", "project.workflows", "project.layouts", "project.dashboard", "none"}
)

_NUMERIC = {"integer", "number"}
_RESTRICTED_METHODS = {"quantile", "equal_interval"}
_DATA_LAYER_TYPES = {"feature", "table"}
SAMPLE_MAX = 10
SAMPLE_FIELDS_MAX = 20
_SAMPLE_VALUE_CHARS = 200
#: Values listed per categorical field; also the Restricted cardinality limit.
UNIQUE_VALUES = LOW_CARDINALITY_LIMIT
#: Under Restricted, a filter that matches fewer features than this is not
#: allowed to return the values of what it matches: a filter that isolates one
#: feature would make its minimum, maximum and class breaks that feature's own
#: values. Class breaks are capped so every class holds at least this many
#: features with a value, filtered or not: quantile breaks over as many classes
#: as values are the values themselves. ``k`` break points make ``k + 1``
#: classes.
MIN_RESTRICTED_GROUP = 5
#: A server extent narrower than this (a single point, or features on one
#: meridian or parallel) is widened to it before it becomes a map view, because
#: a zero-sized box cannot be fitted. In degrees, roughly 200 m.
_MIN_EXTENT_DEGREES = 0.004


class ProjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID | None = Field(
        default=None,
        description=(
            "Leave it out for the open project; another project's id reads that one "
            "as a source."
        ),
    )


class LayerInput(ProjectInput):
    layer_project_id: int = Field(
        ge=1,
        description="The layer's ID within the project (layer_project_id from project_get_layers).",
    )


class FilteredLayerInput(LayerInput):
    filter: FeatureFilter | None = Field(
        default=None,
        description=f"Only features matching this filter. {FILTER_EXAMPLES}",
    )


def _project_id(env: ToolEnv, given: UUID | None) -> UUID:
    if given is not None:
        return given
    current = project_of(env.page)
    if current is None:
        raise InputInvalid(
            "No project is open on this page; pass project_id (core_find finds projects by name)."
        )
    return current


async def _core(env: ToolEnv, path: str) -> Any:
    try:
        return await env.call("core", "GET", f"/api/v2/project{path}")
    except ServiceError as exc:
        # Core's authorization answers 401 for "no access" too, not only for an
        # expired sign-in, so the message names both.
        if exc.status in (401, 403, 404):
            raise ToolFailed(
                "The project does not exist, the user cannot open it, or the sign-in expired."
            ) from exc
        raise


@dataclass(frozen=True)
class _Layer:
    project_id: UUID
    layer_project_id: int
    layer_id: str
    name: str
    geometry_type: str | None


async def _readable_layer(env: ToolEnv, args: LayerInput) -> _Layer:
    project_id = _project_id(env, args.project_id)
    for row in await _core(env, f"/{project_id}/layer"):
        if row.get("id") != args.layer_project_id:
            continue
        name = str(row.get("name") or f"layer {args.layer_project_id}")
        if row.get("locked"):
            raise ToolFailed(
                f"{name!r} is in the project, but the user has no access to its data."
            )
        if row.get("type") not in _DATA_LAYER_TYPES:
            raise ToolFailed(
                f"{name!r} is a {row.get('type')} layer; only feature and table layers have data to read."
            )
        return _Layer(
            project_id,
            args.layer_project_id,
            str(row["layer_id"]),
            name,
            row.get("feature_layer_geometry_type"),
        )
    raise InputInvalid(
        f"There is no layer {args.layer_project_id} in project {project_id}. "
        "Call project_get_layers to list the layers."
    )


async def _fields(env: ToolEnv, layer: _Layer) -> dict[str, str]:
    """``{field: kind}`` (``field_kind``); the geometry (a ``$ref``) is left out."""
    doc = await env.call("geoapi", "GET", f"/collections/{layer.layer_id}/queryables")
    return {
        name: field_kind(schema)
        for name, schema in (doc.get("properties") or {}).items()
        if isinstance(schema, dict) and "$ref" not in schema
    }


def _compile(
    feature_filter: FeatureFilter | None, fields: Mapping[str, str]
) -> str | None:
    """The filter checked against the layer's fields, as the CQL2-JSON string
    the services take; None without a filter."""
    return (
        None if feature_filter is None else json.dumps(to_cql2(feature_filter, fields))
    )


#: What a filter may do under Restricted: pick categories, never compare values.
#: "Count where einwohner >= X", asked for X after X, spells out a value that
#: the policy withholds, one feature at a time or the whole layer in order.
_RESTRICTED_FILTER_OPS = frozenset({"=", "!=", "in", "is_null", "is_not_null"})


async def _guard_restricted_filter(
    env: ToolEnv, layer: _Layer, feature_filter: FeatureFilter | None
) -> None:
    """Under Restricted, a filter only selects categories: equality, set and
    null conditions on fields with at most LOW_CARDINALITY_LIMIT distinct
    values over the whole layer (the fields whose values Restricted lists)."""
    if env.data_policy != "restricted" or feature_filter is None:
        return
    for condition in feature_filter.conditions:
        if condition.op not in _RESTRICTED_FILTER_OPS:
            raise InputInvalid(
                f"The data policy (Restricted) allows no {condition.op!r} in a filter: "
                "comparing values would reveal values it withholds. Filter by "
                "categories only (=, !=, in, is_null, is_not_null), or answer without "
                "the filter."
            )
    picks = [c for c in feature_filter.conditions if c.op in ("=", "!=", "in")]
    fields = sorted({c.field for c in picks})
    answers = await asyncio.gather(
        *(
            _analytics(
                env,
                "unique-values",
                {
                    "collection": layer.layer_id,
                    "attribute": field,
                    "order": "descendent",
                    "limit": UNIQUE_VALUES,
                },
            )
            for field in fields
        )
    )
    counts: dict[str, dict[str, int]] = {}
    for field, answer in zip(fields, answers):
        if _distinct_total(answer) > LOW_CARDINALITY_LIMIT:
            raise InputInvalid(
                f"The data policy (Restricted) allows filters on category fields "
                f"only; {field!r} has more than {LOW_CARDINALITY_LIMIT} distinct "
                "values, so filtering by it could single out features."
            )
        counts[field] = {
            str(v["value"]): int(v["count"])
            for v in answer.get("values", [])
            if v.get("value") is not None
        }
    # A category held by fewer than MIN_RESTRICTED_GROUP features singles them
    # out: "name = Mitte" picks one district, "name != Südwest" leaves all but
    # one, and a maximum over the rest is then the second largest value.
    for condition in picks:
        values: list[Any] = (
            list(condition.value)
            if isinstance(condition.value, list)
            else [condition.value]
        )
        for value in values:
            held = counts[condition.field].get(str(value), 0)
            if held < MIN_RESTRICTED_GROUP:
                raise InputInvalid(
                    f"The data policy (Restricted) allows filtering only by values "
                    f"that at least {MIN_RESTRICTED_GROUP} features share; "
                    f"{condition.field} {value!r} is shared by fewer, so the filter "
                    "could single out features."
                )


async def _cql(
    env: ToolEnv, layer: _Layer, feature_filter: FeatureFilter | None
) -> str | None:
    if feature_filter is None:
        return None
    await _guard_restricted_filter(env, layer, feature_filter)
    return _compile(feature_filter, await _fields(env, layer))


def _with_value(
    feature_filter: FeatureFilter | None, fields: Mapping[str, str], field: str
) -> str:
    """The filter ANDed with "``field`` is not null" (without a filter, that
    condition alone), as a CQL2-JSON string. Class breaks, minimum and maximum
    skip rows where the field is null, so the group size that guards them must
    count those rows only: a filter padded with "or the field is null" would
    otherwise look like a large group."""
    present = {
        "op": "not",
        "args": [{"op": "isNull", "args": [{"property": field}]}],
    }
    if feature_filter is None:
        return json.dumps(present)
    return json.dumps({"op": "and", "args": [to_cql2(feature_filter, fields), present]})


def _feature_count(result: Any) -> int:
    """The ``count`` of a feature-count answer. A missing or malformed one is an
    error: the group-size guards must never run on a guess."""
    count = result.get("count") if isinstance(result, dict) else None
    if not isinstance(count, int) or isinstance(count, bool):
        raise ToolFailed("The analytics service answered without a feature count.")
    return count


def _distinct_total(result: Any) -> int:
    """The ``total`` of a unique-values answer. A missing or malformed one is an
    error, never zero: zero would pass for a field with few values."""
    total = result.get("total") if isinstance(result, dict) else None
    if not isinstance(total, int) or isinstance(total, bool):
        raise ToolFailed("The analytics service answered without a distinct count.")
    return total


async def _analytics(env: ToolEnv, process: str, inputs: dict[str, Any]) -> Any:
    body = {
        "inputs": {key: value for key, value in inputs.items() if value is not None}
    }
    return await env.call(
        "processes", "POST", f"/processes/{process}/execution", json_body=body
    )


# -- project.get_layers --------------------------------------------------------


class LayerInfo(BaseModel):
    layer_project_id: int
    name: str
    type: str
    geometry_type: str | None = None
    group: str | None = None
    #: The user has no access to this dataset: listed, but its data cannot be read.
    locked: bool = False
    #: How many features the dataset has, when core knows it without counting
    #: (a catalog dataset's copy records it).
    feature_count: int | None = None
    #: The dataset's bounding box [west, south, east, north] in degrees,
    #: rounded to EXTENT_DECIMALS, when core has one.
    extent: list[float] | None = None
    #: The layer's filter in this project (CQL2-JSON), when it has one.
    filter: dict[str, Any] | None = None
    #: Under Restricted, the filter's text is replaced by this: its literals are
    #: values picked from the dataset.
    has_filter: bool | None = None
    #: The layer selected on the map the user sent this message from; set on
    #: that layer only (None is left out of the result).
    selected: bool | None = None


class GroupInfo(BaseModel):
    id: int
    name: str
    parent_id: int | None = None


class ProjectLayers(BaseModel):
    project_id: UUID
    name: str
    groups: list[GroupInfo]
    layers: list[LayerInfo]

    def restricted(self) -> "ProjectLayers":
        return self.model_copy(
            update={
                "layers": [
                    layer.model_copy(update={"filter": None, "has_filter": True})
                    if layer.filter is not None
                    else layer.model_copy()
                    for layer in self.layers
                ]
            }
        )


#: Decimals a layer's extent keeps: a hundredth of a degree (about a kilometre)
#: tells a city's data from a country's, and keeps the layer list short.
EXTENT_DECIMALS = 2
_WKT_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _recorded_feature_count(row: Mapping[str, Any]) -> int | None:
    """The feature count core sends without counting: the one a catalog
    dataset's copy records (``other_properties.catalog_materialize``, which
    core serves from the dataset). Core keeps none for other layers, and
    counting each layer on every call would read whole tables."""
    other = row.get("other_properties")
    status = other.get("catalog_materialize") if isinstance(other, dict) else None
    count = status.get("feature_count") if isinstance(status, dict) else None
    if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
        return count
    return None


def _extent(row: Mapping[str, Any]) -> list[float] | None:
    """The bounding box of the extent core sends as WKT (a multipolygon in
    WGS84), rounded to EXTENT_DECIMALS; None without one, or for anything
    that is not a box in degrees."""
    wkt = row.get("extent")
    if not isinstance(wkt, str):
        return None
    numbers = [float(n) for n in _WKT_NUMBER.findall(wkt.split(";")[-1])]
    if not numbers or len(numbers) % 2:
        return None
    xs, ys = numbers[0::2], numbers[1::2]
    west, south, east, north = min(xs), min(ys), max(xs), max(ys)
    if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
        return None
    return [round(value, EXTENT_DECIMALS) for value in (west, south, east, north)]


async def _get_layers(env: ToolEnv, args: ProjectInput) -> ProjectLayers:
    project_id = _project_id(env, args.project_id)
    project, rows, groups = await asyncio.gather(
        _core(env, f"/{project_id}"),
        _core(env, f"/{project_id}/layer"),
        _core(env, f"/{project_id}/group"),
    )
    group_names = {group["id"]: group["name"] for group in groups}
    # Only the open project has a selection; a source project read by its ID has none.
    selected = (
        env.page.selected_layer_project_id
        if isinstance(env.page, ProjectMapContext) and env.page.project_id == project_id
        else None
    )
    layers: list[LayerInfo] = []
    # In the project's layer order already (core sorts by layer_order).
    for row in rows:
        locked = bool(row.get("locked"))
        layers.append(
            LayerInfo(
                layer_project_id=row["id"],
                name=row.get("name") or f"layer {row['id']}",
                type=row.get("type") or "unknown",
                geometry_type=row.get("feature_layer_geometry_type"),
                group=group_names.get(row.get("layer_project_group_id")),
                locked=locked,
                # Withheld for a locked layer, as core withholds its other
                # details.
                feature_count=None if locked else _recorded_feature_count(row),
                extent=None if locked else _extent(row),
                filter=(row.get("query") or {}).get("cql"),
                selected=True
                if selected is not None and row["id"] == selected
                else None,
            )
        )
    return ProjectLayers(
        project_id=project_id,
        name=project.get("name") or str(project_id),
        groups=[
            GroupInfo(id=g["id"], name=g["name"], parent_id=g.get("parent_id"))
            for g in groups
        ],
        layers=layers,
    )


GET_LAYERS: ToolSpec[ProjectInput, ProjectLayers] = ToolSpec(
    name="project.get_layers",
    description=(
        "List a project's layers and groups: names, types, geometry types, each "
        "layer's filter, its extent (bounding box) and feature count when known, "
        "which layers the user cannot read (locked) and which one is selected on "
        "the map. Call this first; other project tools take the layer_project_id "
        "it returns."
    ),
    input_model=ProjectInput,
    output_model=ProjectLayers,
    run=_get_layers,
    surfaces=PROJECT_SURFACES,
    returns_data=True,
)


# -- project.get_fields --------------------------------------------------------


class FieldInfo(BaseModel):
    name: str
    #: ``string``, ``number``, ``integer``, ``boolean``, ``date-time`` or another JSON type.
    type: str
    #: Whether filters may use it (``FILTERABLE_KINDS``).
    filterable: bool


class LayerFields(BaseModel):
    layer: str
    fields: list[FieldInfo]
    geometry_type: str | None = None


async def _get_fields(env: ToolEnv, args: LayerInput) -> LayerFields:
    layer = await _readable_layer(env, args)
    fields = await _fields(env, layer)
    return LayerFields(
        layer=layer.name,
        fields=[
            FieldInfo(name=name, type=kind, filterable=kind in FILTERABLE_KINDS)
            for name, kind in fields.items()
        ],
        geometry_type=layer.geometry_type,
    )


GET_FIELDS: ToolSpec[LayerInput, LayerFields] = ToolSpec(
    name="project.get_fields",
    description=(
        "List a layer's fields (attribute names), their types, and which of them "
        "filters can use."
    ),
    input_model=LayerInput,
    output_model=LayerFields,
    run=_get_fields,
    surfaces=PROJECT_SURFACES,
    returns_data=False,
)


# -- project.count_features ----------------------------------------------------


class FeatureCount(BaseModel):
    layer: str
    filter: str
    count: int | None
    #: Set when the count is withheld (Restricted, a filter, a small group).
    note: str | None = None
    #: Whether a filter was applied; not shown to the model.
    filtered: bool = Field(default=False, exclude=True)

    def restricted(self) -> "FeatureCount":
        # Counts are allowed under Restricted (spec §4.7), except a filtered one
        # below the group size: even category filters, combined, can single out
        # a feature, and "none" against "one" says whether it exists. A copy,
        # because the policy treats a reduction that returns the same object as
        # no reduction.
        if (
            self.filtered
            and self.count is not None
            and self.count < MIN_RESTRICTED_GROUP
        ):
            return self.model_copy(
                update={
                    "count": None,
                    "note": (
                        f"The filter matches fewer than {MIN_RESTRICTED_GROUP} "
                        "features; the data policy (Restricted) withholds the exact number."
                    ),
                }
            )
        return self.model_copy()


async def _count(env: ToolEnv, args: FilteredLayerInput) -> FeatureCount:
    layer = await _readable_layer(env, args)
    cql = await _cql(env, layer, args.filter)
    result = await _analytics(
        env, "feature-count", {"collection": layer.layer_id, "filter": cql}
    )
    return FeatureCount(
        layer=layer.name,
        filter=describe_filter(args.filter),
        count=int(result["count"]),
        filtered=args.filter is not None,
    )


COUNT_FEATURES: ToolSpec[FilteredLayerInput, FeatureCount] = ToolSpec(
    name="project.count_features",
    description=(
        "Count a layer's features, optionally only those matching a filter. The "
        "layer's own filter in the project is not applied; pass it as a filter if "
        "the count should match what the map shows."
    ),
    input_model=FilteredLayerInput,
    output_model=FeatureCount,
    run=_count,
    surfaces=PROJECT_SURFACES,
    returns_data=True,
)


# -- project.field_statistics --------------------------------------------------


class StatisticsInput(FilteredLayerInput):
    field: str = Field(
        description="The field to describe, as project_get_fields lists it."
    )
    method: Literal[
        "quantile", "equal_interval", "standard_deviation", "heads_and_tails"
    ] = Field(
        default="quantile", description="Classification method for numeric fields."
    )
    breaks: int = Field(
        default=5,
        ge=2,
        le=10,
        description="Number of class break points (the values form breaks + 1 classes).",
    )


class ValueCount(BaseModel):
    #: Text, whatever the field's type.
    value: str | None
    count: int


class FieldStatistics(BaseModel):
    layer: str
    field: str
    kind: Literal["numeric", "categorical"]
    filter: str
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    std_dev: float | None = None
    method: str | None = None
    breaks: list[float] | None = None
    #: How many features the filter matches with a value in the field; set
    #: only under Restricted with a filter, where it decides whether the
    #: numbers may be shown.
    feature_count: int | None = None
    distinct_count: int | None = None
    values: list[ValueCount] | None = None
    note: str | None = None
    #: Whether the field has few distinct values over the whole layer, not only
    #: over the filtered features. Set under Restricted; never serialized.
    low_cardinality: bool | None = Field(default=None, exclude=True)
    #: The break points allowed under Restricted: ``points + 1`` classes of at
    #: least MIN_RESTRICTED_GROUP features with a value each. Never
    #: serialized. Fewer than two (the fewest the service computes) means no
    #: breaks may be shown.
    points: int | None = Field(default=None, exclude=True)

    def restricted(self) -> "FieldStatistics":
        if self.kind == "numeric":
            notes = [
                "Mean and standard deviation are withheld by the data policy (Restricted)."
            ]
            update: dict[str, Any] = {"mean": None, "std_dev": None}
            if self.method not in _RESTRICTED_METHODS:
                # Breaks from other methods are built on the mean and deviation.
                update["breaks"] = None
            if (
                self.feature_count is not None
                and self.feature_count < MIN_RESTRICTED_GROUP
            ):
                update.update(min=None, max=None, breaks=None)
                notes.append(
                    f"The filter matches fewer than {MIN_RESTRICTED_GROUP} features "
                    "with a value, so minimum, maximum and class breaks are withheld too."
                )
            elif update.get("breaks", self.breaks) is not None and (
                self.points is None or self.points < 2
            ):
                update["breaks"] = None
                notes.append(
                    "Class breaks are withheld too: each class must hold at least "
                    f"{MIN_RESTRICTED_GROUP} features with a value, and there are too "
                    "few for three classes."
                )
            return self.model_copy(update={**update, "note": " ".join(notes)})
        low = (
            self.low_cardinality
            if self.low_cardinality is not None
            else self.distinct_count is not None
            and self.distinct_count <= LOW_CARDINALITY_LIMIT
        )
        if low:
            return self.model_copy()
        return self.model_copy(
            update={
                "values": None,
                "note": (
                    "Values are withheld by the data policy (Restricted): the field has "
                    f"more than {LOW_CARDINALITY_LIMIT} distinct values."
                ),
            }
        )


async def _field_statistics(env: ToolEnv, args: StatisticsInput) -> FieldStatistics:
    layer = await _readable_layer(env, args)
    fields = await _fields(env, layer)
    if args.field not in fields:
        raise InputInvalid(unknown_field(args.field, fields))
    await _guard_restricted_filter(env, layer, args.filter)
    cql = _compile(args.filter, fields)
    described = describe_filter(args.filter)
    restricted = env.data_policy == "restricted"
    if fields[args.field] in _NUMERIC:
        method = args.method
        if restricted and method not in _RESTRICTED_METHODS:
            # Mean-based breaks sit at the mean and multiples of the standard
            # deviation, which Restricted withholds (Decision T20).
            method = "quantile"
        valued: int | None = None
        points = args.breaks
        if restricted:
            # Counted first: the number of break points depends on it.
            valued = _feature_count(
                await _analytics(
                    env,
                    "feature-count",
                    {
                        "collection": layer.layer_id,
                        "filter": _with_value(args.filter, fields, args.field),
                    },
                )
            )
            points = min(args.breaks, valued // MIN_RESTRICTED_GROUP - 1)
        result = await _analytics(
            env,
            "class-breaks",
            {
                "collection": layer.layer_id,
                "attribute": args.field,
                "method": method,
                # Internal break points: ``points + 1`` classes. Fewer than two:
                # still asked for two, for the minimum and maximum; the breaks
                # are withheld (FieldStatistics.restricted).
                "breaks": max(points, 2),
                "filter": cql,
            },
        )
        return FieldStatistics(
            layer=layer.name,
            field=args.field,
            kind="numeric",
            filter=described,
            min=result.get("min"),
            max=result.get("max"),
            mean=result.get("mean"),
            std_dev=result.get("std_dev"),
            method=result.get("method"),
            breaks=result.get("breaks"),
            feature_count=valued if cql is not None else None,
            points=points if restricted else None,
        )
    values_call = _analytics(
        env,
        "unique-values",
        {
            "collection": layer.layer_id,
            "attribute": args.field,
            "order": "descendent",
            "limit": UNIQUE_VALUES,
            "filter": cql,
        },
    )
    low_cardinality: bool | None = None
    if restricted and cql is not None:
        # The filtered distinct count says little about the field: a filter on
        # one person's id leaves a single name. Cardinality is judged on the
        # whole layer.
        result, whole = await asyncio.gather(
            values_call,
            _analytics(
                env,
                "unique-values",
                {
                    "collection": layer.layer_id,
                    "attribute": args.field,
                    "order": "descendent",
                    "limit": 1,
                },
            ),
        )
        low_cardinality = _distinct_total(whole) <= LOW_CARDINALITY_LIMIT
    else:
        result = await values_call
    return FieldStatistics(
        layer=layer.name,
        field=args.field,
        kind="categorical",
        filter=described,
        distinct_count=_distinct_total(result),
        values=[
            ValueCount(
                value=None if v["value"] is None else str(v["value"]),
                count=int(v["count"]),
            )
            for v in result.get("values", [])
        ],
        low_cardinality=low_cardinality,
    )


FIELD_STATISTICS: ToolSpec[StatisticsInput, FieldStatistics] = ToolSpec(
    name="project.field_statistics",
    description=(
        "Describe one field of a layer. Numeric fields: minimum, maximum, mean, "
        "standard deviation and class breaks computed by GOAT (use these breaks for "
        "classes, do not invent your own). Other fields: the number of distinct "
        f"values and the {UNIQUE_VALUES} most frequent ones with their counts. Values "
        "come back as text, whatever the field's type."
    ),
    input_model=StatisticsInput,
    output_model=FieldStatistics,
    run=_field_statistics,
    surfaces=PROJECT_SURFACES,
    returns_data=True,
)


# -- project.area_statistics ---------------------------------------------------


class AreaStatistics(BaseModel):
    layer: str
    filter: str
    feature_count: int
    total_area: float | None = None
    mean_area: float | None = None
    min_area: float | None = None
    max_area: float | None = None
    unit: str = "m²"
    note: str | None = None
    #: Whether a filter was applied; never serialized.
    filtered: bool = Field(default=False, exclude=True)

    def restricted(self) -> "AreaStatistics":
        update: dict[str, Any] = {"total_area": None, "mean_area": None}
        note = "Total and mean area are withheld by the data policy (Restricted)."
        if self.filtered and self.feature_count < MIN_RESTRICTED_GROUP:
            update.update(min_area=None, max_area=None)
            note += (
                f" The filter matches fewer than {MIN_RESTRICTED_GROUP} features, so "
                "smallest and largest area are withheld too."
            )
        return self.model_copy(update={**update, "note": note})


async def _area_statistics(env: ToolEnv, args: FilteredLayerInput) -> AreaStatistics:
    layer = await _readable_layer(env, args)
    if layer.geometry_type != "polygon":
        raise ToolFailed(
            f"Area statistics need a polygon layer; {layer.name!r} has {layer.geometry_type} features."
        )
    # The filter cannot name the geometry (it is not a filterable field), so it
    # cannot be padded with rows that have none: the count the group-size guard
    # reads is the number of features the filter matches.
    cql = await _cql(env, layer, args.filter)
    total, smallest, largest = await asyncio.gather(
        *(
            _analytics(
                env,
                "area-statistics",
                {"collection": layer.layer_id, "operation": operation, "filter": cql},
            )
            for operation in ("sum", "min", "max")
        )
    )
    count = int(total.get("feature_count") or 0)
    area = total.get("total_area")
    return AreaStatistics(
        layer=layer.name,
        filter=describe_filter(args.filter),
        feature_count=count,
        total_area=area,
        mean_area=area / count if area is not None and count else None,
        min_area=smallest.get("result"),
        max_area=largest.get("result"),
        unit=total.get("unit") or "m²",
        filtered=args.filter is not None,
    )


AREA_STATISTICS: ToolSpec[FilteredLayerInput, AreaStatistics] = ToolSpec(
    name="project.area_statistics",
    description="Area of a polygon layer's features: count, total, mean, smallest and largest, in square metres.",
    input_model=FilteredLayerInput,
    output_model=AreaStatistics,
    run=_area_statistics,
    surfaces=PROJECT_SURFACES,
    returns_data=True,
)


# -- project.sample_features ---------------------------------------------------


class SampleInput(FilteredLayerInput):
    fields: list[str] = Field(
        default_factory=list,
        max_length=SAMPLE_FIELDS_MAX,
        description=f"Fields to include (at most {SAMPLE_FIELDS_MAX}); empty for the first {SAMPLE_FIELDS_MAX}.",
    )
    limit: int = Field(default=5, description=f"Features to return (1-{SAMPLE_MAX}).")


class SampleFeature(BaseModel):
    id: Any
    properties: dict[str, Any]


class FeatureSample(BaseModel):
    layer: str
    filter: str
    number_matched: int | None = None
    features: list[SampleFeature] = Field(default_factory=list)

    def restricted(self) -> Withheld:
        return Withheld(
            reason=(
                "Individual features are withheld by the data policy (Restricted). "
                "Use project_count_features or project_field_statistics instead."
            )
        )


def _short(value: Any) -> Any:
    if isinstance(value, str) and len(value) > _SAMPLE_VALUE_CHARS:
        return value[:_SAMPLE_VALUE_CHARS] + "…"
    return value


async def _sample(env: ToolEnv, args: SampleInput) -> FeatureSample:
    layer = await _readable_layer(env, args)
    if env.data_policy == "restricted":
        # Withheld by the policy anyway (FeatureSample.restricted): do not read rows at all.
        return FeatureSample(layer=layer.name, filter=describe_filter(args.filter))
    fields = await _fields(env, layer)
    for name in args.fields:
        if name not in fields:
            raise InputInvalid(unknown_field(name, fields))
    selected = args.fields or list(fields)[:SAMPLE_FIELDS_MAX]
    params: dict[str, object] = {
        "limit": max(1, min(args.limit, SAMPLE_MAX)),
        "properties": selected,
    }
    if args.filter is not None:
        params["filter"] = _compile(args.filter, fields)
        params["filter-lang"] = "cql2-json"
    body = await env.call(
        "geoapi", "GET", f"/collections/{layer.layer_id}/items", params=params
    )
    features = [
        SampleFeature(
            id=feature.get("id"),
            properties={
                key: _short(value)
                for key, value in (feature.get("properties") or {}).items()
            },
        )
        for feature in body.get("features", [])
    ]
    return FeatureSample(
        layer=layer.name,
        filter=describe_filter(args.filter),
        number_matched=body.get("numberMatched"),
        features=features,
    )


SAMPLE_FEATURES: ToolSpec[SampleInput, FeatureSample] = ToolSpec(
    name="project.sample_features",
    description=(
        f"A few features of a layer (at most {SAMPLE_MAX}), attributes only, no "
        "geometry, to see what the data looks like. Not for counting: use "
        "project_count_features."
    ),
    input_model=SampleInput,
    output_model=FeatureSample,
    run=_sample,
    surfaces=PROJECT_SURFACES,
    returns_data=True,
)


# -- map.propose_view ----------------------------------------------------------


class ProposeViewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=80,
        description="A short title for the card, in the user's language.",
    )
    bbox: list[float] | None = Field(
        default=None,
        min_length=4,
        max_length=4,
        description="[west, south, east, north] in WGS84.",
    )
    center: list[float] | None = Field(
        default=None, min_length=2, max_length=2, description="[longitude, latitude]."
    )
    zoom: float | None = Field(
        default=None, ge=0, le=22, description="Zoom level, with center."
    )
    bearing: float = Field(
        default=0, ge=-180, le=180, description="Map rotation in degrees, with center."
    )
    pitch: float = Field(
        default=0, ge=0, le=85, description="Map tilt in degrees, with center."
    )
    fit_layer_project_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Fit the view to this layer's features (GOAT computes the extent). "
            "Give the layer_project_id of a layer of the open project."
        ),
    )
    filter: FeatureFilter | None = Field(
        default=None,
        description=(
            "With fit_layer_project_id: fit only the features matching this filter. "
            f"{FILTER_EXAMPLES}"
        ),
    )


def _check_bbox(bbox: list[float]) -> tuple[float, float, float, float]:
    west, south, east, north = bbox
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise InputInvalid(
            "bbox must be [west, south, east, north] with west < east and south < north in WGS84."
        )
    return west, south, east, north


def _widen(
    low: float, high: float, floor: float, ceiling: float
) -> tuple[float, float]:
    """``low..high`` at least ``_MIN_EXTENT_DEGREES`` wide, kept inside the bounds."""
    if high - low >= _MIN_EXTENT_DEGREES:
        return low, high
    middle = (low + high) / 2
    low, high = middle - _MIN_EXTENT_DEGREES / 2, middle + _MIN_EXTENT_DEGREES / 2
    if low < floor:
        return floor, floor + _MIN_EXTENT_DEGREES
    if high > ceiling:
        return ceiling - _MIN_EXTENT_DEGREES, ceiling
    return low, high


def _extent_bbox(raw: list[float]) -> tuple[float, float, float, float]:
    """A layer's extent as a map view. One feature that is a point, or features
    on one meridian or parallel, give a box with no width or height: it is
    widened (the model's own bbox stays strictly checked)."""
    try:
        west, south, east, north = (float(value) for value in raw)
        if not (west <= east and south <= north):
            raise ValueError
        west, east = _widen(west, east, -180.0, 180.0)
        south, north = _widen(south, north, -90.0, 90.0)
        return _check_bbox([west, south, east, north])
    except (ValueError, InputInvalid) as exc:
        raise ToolFailed("The layer's extent cannot be shown as a map view.") from exc


async def _propose_view(env: ToolEnv, args: ProposeViewInput) -> ProposalShown:
    modes = [
        args.bbox is not None,
        args.center is not None,
        args.fit_layer_project_id is not None,
    ]
    if sum(modes) != 1:
        raise InputInvalid(
            "Pass exactly one of bbox, center with zoom, or fit_layer_project_id."
        )
    if args.filter is not None and args.fit_layer_project_id is None:
        raise InputInvalid("filter goes with fit_layer_project_id.")
    if args.center is None and (args.zoom is not None or args.bearing or args.pitch):
        raise InputInvalid("zoom, bearing and pitch go with center.")
    # Only the project that is open can be moved, so the layer is looked up there.
    project_id = project_of(env.page)
    if project_id is None:
        raise InputInvalid("No project is open on this page.")
    rows: list[ProposalRow] = []
    camera: MapCamera | None = None
    bbox: tuple[float, float, float, float] | None = None
    if args.center is not None:
        if args.zoom is None:
            raise InputInvalid("center needs a zoom.")
        longitude, latitude = args.center
        if not (-180 <= longitude <= 180 and -85.06 <= latitude <= 85.06):
            raise InputInvalid("center must be [longitude, latitude] in WGS84.")
        camera = MapCamera(
            center=(longitude, latitude),
            zoom=args.zoom,
            bearing=args.bearing,
            pitch=args.pitch,
        )
        rows += [
            proposal_row("center", f"{longitude:.5f}, {latitude:.5f}"),
            proposal_row("zoom", f"{args.zoom:g}"),
        ]
    elif args.bbox is not None:
        bbox = _check_bbox(args.bbox)
        rows.append(proposal_row("bbox", ", ".join(f"{value:.5f}" for value in bbox)))
    elif args.fit_layer_project_id is not None:
        layer = await _readable_layer(
            env,
            LayerInput(
                project_id=project_id, layer_project_id=args.fit_layer_project_id
            ),
        )
        cql = await _cql(env, layer, args.filter)
        extent = await _analytics(
            env, "extent", {"collection": layer.layer_id, "filter": cql}
        )
        if not extent.get("bbox"):
            raise ToolFailed("No features match, so there is nothing to show.")
        bbox = _extent_bbox(list(extent["bbox"]))
        rows.append(proposal_row("layer", layer.name))
        if args.filter is not None:
            rows.append(proposal_row("filter", describe_filter(args.filter)))
    project = await _core(env, f"/{project_id}")
    name = project.get("name")
    rows.insert(0, proposal_row("project", name or str(project_id)))
    proposal = Proposal(
        kind="map.view",
        surface="project.map",
        target=ProposalTarget(project_id=project_id, name=name),
        title=args.title,
        rows=rows,
        payload=MapViewPayload(
            project_id=project_id,
            camera=camera,
            bbox=bbox,
            layer_project_id=args.fit_layer_project_id,
        ),
    )
    return await show(env, proposal)


PROPOSE_VIEW: ToolSpec[ProposeViewInput, ProposalShown] = ToolSpec(
    name="map.propose_view",
    description=(
        "Suggest a map view of the open project: a bounding box, a center and zoom, "
        "or the extent of one of its layers' features. Shows a card; the map moves "
        "only if the user applies it."
    ),
    input_model=ProposeViewInput,
    output_model=ProposalShown,
    run=_propose_view,
    surfaces=frozenset({"project.map"}),
    returns_data=False,
    risk="propose",
)

# -- project.get_workflows / project.get_layouts -------------------------------

_TEXT_CHARS = 200


def _clip_text(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    return value if len(value) <= _TEXT_CHARS else value[:_TEXT_CHARS] + "…"


class WorkflowInfo(BaseModel):
    id: str
    name: str
    description: str | None = None
    is_default: bool | None = None
    #: The analysis tools its steps run, e.g. catchment_area, buffer.
    tools: list[str] = Field(default_factory=list)
    #: The names of the datasets it starts from.
    inputs: list[str] = Field(default_factory=list)
    updated_at: str | None = None


class ProjectWorkflows(BaseModel):
    project_id: UUID
    project_name: str
    workflows: list[WorkflowInfo]


def _workflow(row: dict[str, Any]) -> WorkflowInfo:
    nodes = [
        node
        for node in ((row.get("config") or {}).get("nodes") or [])
        if isinstance(node, dict)
    ]
    data = [node.get("data") or {} for node in nodes]
    tools = [str(d["processId"]) for d in data if isinstance(d.get("processId"), str)]
    inputs = [str(d["layerName"]) for d in data if isinstance(d.get("layerName"), str)]
    return WorkflowInfo(
        id=str(row.get("id")),
        name=str(row.get("name") or ""),
        description=_clip_text(row.get("description")),
        is_default=True if row.get("is_default") else None,
        tools=list(dict.fromkeys(tools)),
        inputs=list(dict.fromkeys(inputs)),
        updated_at=row.get("updated_at"),
    )


async def _get_workflows(env: ToolEnv, args: ProjectInput) -> ProjectWorkflows:
    project_id = _project_id(env, args.project_id)
    project, rows = await asyncio.gather(
        _core(env, f"/{project_id}"), _core(env, f"/{project_id}/workflow")
    )
    return ProjectWorkflows(
        project_id=project_id,
        project_name=str(project.get("name") or ""),
        workflows=[_workflow(row) for row in rows or []],
    )


GET_WORKFLOWS: ToolSpec[ProjectInput, ProjectWorkflows] = ToolSpec(
    name="project.get_workflows",
    description=(
        "List a project's workflows (chains of analysis steps in its Workflows "
        "mode): names, descriptions, the analysis tools they run and the datasets "
        "they start from. Pass project_id for a project other than the open one. "
        "Show the ones your answer points to with core_show_items (kind workflow)."
    ),
    input_model=ProjectInput,
    output_model=ProjectWorkflows,
    run=_get_workflows,
    surfaces=PROJECT_SURFACES,
    returns_data=False,
)


class LayoutInfo(BaseModel):
    id: str
    name: str
    description: str | None = None
    is_default: bool | None = None
    #: e.g. "A4 landscape".
    page: str | None = None
    #: What is on the page, e.g. map, legend, text.
    elements: list[str] = Field(default_factory=list)
    updated_at: str | None = None


class ProjectLayouts(BaseModel):
    project_id: UUID
    project_name: str
    layouts: list[LayoutInfo]


def _layout(row: dict[str, Any]) -> LayoutInfo:
    config = row.get("config") or {}
    page = config.get("page") or {}
    size = " ".join(
        str(part) for part in (page.get("size"), page.get("orientation")) if part
    )
    kinds = [
        str(element["type"])
        for element in (config.get("elements") or [])
        if isinstance(element, dict) and isinstance(element.get("type"), str)
    ]
    return LayoutInfo(
        id=str(row.get("id")),
        name=str(row.get("name") or ""),
        description=_clip_text(row.get("description")),
        is_default=True if row.get("is_default") else None,
        page=size or None,
        elements=list(dict.fromkeys(kinds)),
        updated_at=row.get("updated_at"),
    )


async def _get_layouts(env: ToolEnv, args: ProjectInput) -> ProjectLayouts:
    project_id = _project_id(env, args.project_id)
    project, rows = await asyncio.gather(
        _core(env, f"/{project_id}"), _core(env, f"/{project_id}/report-layout")
    )
    return ProjectLayouts(
        project_id=project_id,
        project_name=str(project.get("name") or ""),
        layouts=[_layout(row) for row in rows or []],
    )


GET_LAYOUTS: ToolSpec[ProjectInput, ProjectLayouts] = ToolSpec(
    name="project.get_layouts",
    description=(
        "List a project's print layouts (pages in its Layouts mode): names, page "
        "size and what is on the page. Pass project_id for a project other than "
        "the open one. Show the ones your answer points to with core_show_items "
        "(kind layout)."
    ),
    input_model=ProjectInput,
    output_model=ProjectLayouts,
    run=_get_layouts,
    surfaces=PROJECT_SURFACES,
    returns_data=False,
)

PROJECT_TOOLS: tuple[ToolSpec[Any, Any], ...] = (
    GET_LAYERS,
    GET_FIELDS,
    COUNT_FEATURES,
    FIELD_STATISTICS,
    AREA_STATISTICS,
    SAMPLE_FEATURES,
    PROPOSE_VIEW,
    GET_WORKFLOWS,
    GET_LAYOUTS,
)
