"""The draft the assistant writes for a new workflow, and its conversion into
the config the Workflows editor stores (spec §4.1, §4.2).

The model describes a workflow in a small format of its own: steps with short
ids, connections between those ids, settings by name. ``to_config`` turns it
into the editor's config, so the check, the create and the editor read one and
the same thing. It is pure: the caller looks up the project's layers, the
regions' boundaries and the tools' titles and passes them in.

Node and edge ids are derived from the draft's ids and a salt (uuid5): the
same draft and salt give the same config. A tool converts a draft once per
call with a fresh salt, so the create saves the config its check checked, and
two workflows made from one draft share no node id (an export's node id names
its result layer, ``goatlib.tools.workflow_export_target``).
"""

import json
import uuid
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)

from assistant.context import NUTS_ID_PATTERN

STEP_ID_PATTERN = r"^[A-Za-z0-9_-]{1,40}$"
INPUT_PATTERN = r"^[A-Za-z0-9_]{1,64}$"
TOOL_ID_PATTERN = r"^[a-z0-9_]{1,64}$"
VARIABLE_NAME_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
MAX_STEPS = 30
MAX_CONNECTIONS = 60
MAX_CONDITIONS = 10
MAX_IN_VALUES = 50

#: The namespace of the derived ids without a salt. Changing it changes the id
#: of every step a draft converts to.
ID_NAMESPACE = uuid.UUID("5b0f3c1e-2d7a-4e8b-9c41-7a2f6d0e8b13")

#: Layout (spec §4.2): left to right by depth, each depth a column.
DEPTH_SPACING = 360
ROW_SPACING = 200
#: The editor restores a workflow's stored viewport when it opens it and does
#: not fit the view to the steps (``WorkflowCanvas``), so the conversion
#: stores a viewport that shows every step on a canvas of at least this size.
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 500
CANVAS_MARGIN = 40
#: A step's largest drawn size (the node's ``maxWidth``, a tall tool step).
NODE_WIDTH = 360
NODE_HEIGHT = 160
#: The editor's smallest zoom (``WORKFLOW_CANVAS_MIN_ZOOM``).
MIN_ZOOM = 0.1

#: A region boundary larger than this, as JSON, is stored as its bounding box:
#: the filter travels inside the workflow's config and into every run's tool
#: arguments.
MAX_AREA_BYTES = 200_000

#: The draft's operators as the editor's filter expressions, which the runner
#: turns into CQL2 (``workflow_runner.convert_filter_to_cql``).
EXPRESSIONS: dict[str, str] = {
    "=": "is",
    "!=": "is_not",
    "<": "is_less_than",
    "<=": "is_at_most",
    ">": "is_greater_than",
    ">=": "is_at_least",
    "in": "includes",
    "contains": "contains_the_text",
}

Op = Literal["=", "!=", "<", "<=", ">", ">=", "in", "contains"]
Scalar = StrictStr | StrictInt | StrictFloat | StrictBool


class DraftError(ValueError):
    """The draft names a layer or region the caller did not find."""


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Condition(_Model):
    field: str = Field(
        min_length=1,
        max_length=100,
        description="A field of the step's layer, as project_get_fields lists it.",
    )
    op: Op = Field(
        description="'in' takes a list; 'contains' matches text, case-insensitive."
    )
    value: Scalar | list[Scalar] = Field(
        description=(
            "A list for 'in', text for 'contains', else one value of the field's "
            "type (true or false with '=' and '!=')."
        )
    )

    @model_validator(mode="after")
    def _value_fits_op(self) -> "Condition":
        if self.op == "in":
            if not isinstance(self.value, list) or not self.value:
                raise ValueError("'in' takes a non-empty list of values")
            if len(self.value) > MAX_IN_VALUES:
                raise ValueError(f"'in' takes at most {MAX_IN_VALUES} values")
        elif isinstance(self.value, list):
            raise ValueError(f"only 'in' takes a list, not {self.op!r}")
        elif self.op == "contains" and not isinstance(self.value, str):
            raise ValueError("'contains' takes text")
        elif isinstance(self.value, bool) and self.op not in ("=", "!="):
            raise ValueError(f"a yes/no value takes '=' or '!=', not {self.op!r}")
        return self


class StepFilter(_Model):
    area: str | None = Field(
        default=None,
        pattern=NUTS_ID_PATTERN,
        description=(
            "A region (nuts_id from catalog_find_region): keeps the features "
            "inside it, e.g. Munich when the dataset covers all of Germany."
        ),
    )
    where: list[Condition] = Field(
        default_factory=list,
        max_length=MAX_CONDITIONS,
        description="Keeps the features matching every condition.",
    )

    @model_validator(mode="after")
    def _limits_something(self) -> "StepFilter":
        if self.area is None and not self.where:
            raise ValueError("a filter needs an area, conditions in where, or both")
        return self


class DatasetStep(_Model):
    id: str = Field(pattern=STEP_ID_PATTERN, description="Unique in the draft.")
    kind: Literal["dataset"]
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "The step's name, in the language of the user's message; required "
            "when layer is null."
        ),
    )
    layer: int | None = Field(
        ge=1,
        description=(
            "The project layer (layer_project_id from project_get_layers), or "
            "null to leave the step open for the user to choose."
        ),
    )
    filter: StepFilter | None = Field(
        default=None, description="Only with a layer: limits the step's features."
    )

    @model_validator(mode="after")
    def _open_steps_are_named_and_unfiltered(self) -> "DatasetStep":
        if self.layer is None:
            if self.label is None:
                raise ValueError(
                    f"step {self.id!r}: a step left open needs a label naming what is missing"
                )
            if self.filter is not None:
                # Choosing the layer in the editor replaces the step's filter
                # (DatasetNodeSettings), so a filter set before would be lost.
                raise ValueError(
                    f"step {self.id!r}: a step left open takes no filter; choosing its "
                    "layer in the editor replaces it. Leave the filter out."
                )
        return self


class ToolStep(_Model):
    id: str = Field(pattern=STEP_ID_PATTERN, description="Unique in the draft.")
    kind: Literal["tool"]
    tool: str = Field(
        pattern=TOOL_ID_PATTERN, description="A tool id from workflow_tools."
    )
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "The step's name, in the language of the user's message; default: "
            "the tool's title."
        ),
    )
    settings: dict[str, Any] = Field(
        default_factory=dict,
        description="The tool's settings by name, as workflow_describe_tool lists them.",
    )


class ExportStep(_Model):
    id: str = Field(pattern=STEP_ID_PATTERN, description="Unique in the draft.")
    kind: Literal["export"]
    name: str = Field(
        min_length=1,
        max_length=255,
        description=(
            "The name the result is saved as, in the language of the user's message."
        ),
    )
    label: str | None = Field(
        default=None, min_length=1, max_length=100, description="Default: the name."
    )


Step = Annotated[DatasetStep | ToolStep | ExportStep, Field(discriminator="kind")]


class Connection(_Model):
    source: str = Field(alias="from", description="The id of the step it reads from.")
    target: str = Field(alias="to", description="The id of the step it feeds.")
    input: str | None = Field(
        default=None,
        pattern=INPUT_PATTERN,
        description=(
            "The tool's layer input it feeds (layer_inputs of workflow_tools); "
            "none into an export."
        ),
    )


class Variable(_Model):
    name: str = Field(pattern=VARIABLE_NAME_PATTERN, max_length=64)
    type: Literal["string", "number"]
    default_value: StrictStr | StrictInt | StrictFloat | None = Field(
        default=None, alias="defaultValue"
    )
    label: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class Draft(_Model):
    name: str = Field(
        min_length=1,
        max_length=255,
        description="The workflow's name, in the language of the user's message.",
    )
    steps: list[Step] = Field(min_length=1, max_length=MAX_STEPS)
    connections: list[Connection] = Field(
        default_factory=list, max_length=MAX_CONNECTIONS
    )
    variables: list[Variable] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def _graph_fits(self) -> "Draft":
        by_id: dict[str, Step] = {}
        for step in self.steps:
            if step.id in by_id:
                raise ValueError(f"two steps have the id {step.id!r}")
            by_id[step.id] = step
        fed: set[tuple[str, str]] = set()
        for connection in self.connections:
            source = by_id.get(connection.source)
            target = by_id.get(connection.target)
            if source is None or target is None:
                missing = connection.source if source is None else connection.target
                raise ValueError(f"a connection names the unknown step {missing!r}")
            if isinstance(source, ExportStep):
                raise ValueError(
                    f"export {source.id!r} saves a result; nothing reads from it"
                )
            if isinstance(target, DatasetStep):
                raise ValueError(f"dataset {target.id!r} reads from nothing")
            if isinstance(target, ExportStep):
                if connection.input is not None:
                    raise ValueError(
                        f"a connection into export {target.id!r} has no input"
                    )
                handle = "input"
            elif connection.input is None:
                raise ValueError(
                    f"the connection into {target.id!r} needs the input it feeds"
                )
            else:
                handle = connection.input
            if (target.id, handle) in fed:
                raise ValueError(f"two connections feed {target.id!r} {handle!r}")
            fed.add((target.id, handle))
        names = [variable.name for variable in self.variables]
        if len(set(names)) != len(names):
            raise ValueError("two variables have the same name")
        return self


@dataclass(frozen=True)
class ProjectLayer:
    """A layer of the project, as core's layer list gives it."""

    layer_project_id: int
    layer_id: str
    name: str
    type: str | None = None
    geometry_type: str | None = None


@dataclass(frozen=True)
class Region:
    nuts_id: str
    name: str
    #: A GeoJSON geometry: the boundary, or its bounding box (``as_box``).
    geometry: dict[str, Any]
    as_box: bool = False


@dataclass(frozen=True)
class Converted:
    config: dict[str, Any]
    #: Draft step id -> node id.
    node_ids: dict[str, str]
    #: Node id -> draft step id.
    step_of: dict[str, str]
    #: Draft step id -> the step's name in the config (its label).
    labels: dict[str, str]


def _namespace(salt: str) -> uuid.UUID:
    """The namespace a conversion derives its ids in: one per salt."""
    return uuid.uuid5(ID_NAMESPACE, salt) if salt else ID_NAMESPACE


def node_id(step: Step, salt: str = "") -> str:
    return f"{step.kind}-{uuid.uuid5(_namespace(salt), step.id)}"


def _edge_id(connection: Connection, salt: str) -> str:
    key = f"{connection.source}->{connection.target}:{connection.input or ''}"
    return f"edge-{uuid.uuid5(_namespace(salt), key)}"


def _coordinates(value: Any) -> Iterator[tuple[float, float]]:
    if (
        isinstance(value, list)
        and len(value) >= 2
        and all(isinstance(v, int | float) for v in value[:2])
    ):
        yield float(value[0]), float(value[1])
    elif isinstance(value, list):
        for item in value:
            yield from _coordinates(item)


def bbox_polygon(geometry: Mapping[str, Any]) -> dict[str, Any]:
    """The bounding box of a GeoJSON geometry, as a polygon."""
    points = list(_coordinates(geometry.get("coordinates")))
    if not points:
        raise DraftError("the region has no coordinates")
    west = min(x for x, _ in points)
    east = max(x for x, _ in points)
    south = min(y for _, y in points)
    north = max(y for _, y in points)
    ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
    return {"type": "Polygon", "coordinates": [ring]}


def region_from_feature(
    nuts_id: str, feature: Mapping[str, Any], max_bytes: int = MAX_AREA_BYTES
) -> Region:
    """A region from the catalog's ``/stac/nuts/{id}/geometry`` feature: its
    boundary, or the boundary's bounding box when the boundary is larger than
    ``max_bytes`` as JSON."""
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict) or "coordinates" not in geometry:
        raise DraftError(f"region {nuts_id!r} has no boundary")
    properties = feature.get("properties") or {}
    name = str(properties.get("nuts_name") or nuts_id)
    size = len(json.dumps(geometry, separators=(",", ":")))
    if size > max_bytes:
        return Region(nuts_id, name, bbox_polygon(geometry), as_box=True)
    return Region(
        nuts_id,
        name,
        {"type": geometry["type"], "coordinates": geometry["coordinates"]},
    )


def depths(draft: Draft) -> dict[str, int]:
    """Each step's depth: the longest path to it from a step without incoming
    connections. Steps in a loop (the check reports it) are placed after the
    steps that lead into them, in draft order."""
    order = [step.id for step in draft.steps]
    successors: dict[str, list[str]] = {step_id: [] for step_id in order}
    incoming: dict[str, int] = {step_id: 0 for step_id in order}
    for connection in draft.connections:
        successors[connection.source].append(connection.target)
        incoming[connection.target] += 1
    depth = {step_id: 0 for step_id in order}
    ready = [step_id for step_id in order if incoming[step_id] == 0]
    while ready:
        current = ready.pop(0)
        for successor in successors[current]:
            depth[successor] = max(depth[successor], depth[current] + 1)
            incoming[successor] -= 1
            if incoming[successor] == 0:
                ready.append(successor)
    # What is left sits in a loop: after the steps that lead into it.
    for step_id in order:
        if incoming[step_id] > 0:
            for connection in draft.connections:
                if connection.target == step_id:
                    depth[step_id] = max(depth[step_id], depth[connection.source] + 1)
    return depth


def layout(draft: Draft) -> dict[str, dict[str, int]]:
    """Positions by step id: a column per depth, ``DEPTH_SPACING`` apart; the
    steps of a column ``ROW_SPACING`` apart, in draft order, centred on the
    first column's middle."""
    depth = depths(draft)
    columns: dict[int, list[str]] = {}
    for step in draft.steps:
        columns.setdefault(depth[step.id], []).append(step.id)
    positions: dict[str, dict[str, int]] = {}
    for column, step_ids in columns.items():
        for row, step_id in enumerate(step_ids):
            positions[step_id] = {
                "x": column * DEPTH_SPACING,
                "y": row * ROW_SPACING - (len(step_ids) - 1) * ROW_SPACING // 2,
            }
    return positions


def viewport(positions: Mapping[str, Mapping[str, int]]) -> dict[str, float]:
    """A viewport that shows every step on a canvas of ``CANVAS_WIDTH`` by
    ``CANVAS_HEIGHT``, at most at zoom 1."""
    xs = [p["x"] for p in positions.values()]
    ys = [p["y"] for p in positions.values()]
    width = max(xs) + NODE_WIDTH - min(xs)
    height = max(ys) + NODE_HEIGHT - min(ys)
    fit = min(
        1.0,
        (CANVAS_WIDTH - 2 * CANVAS_MARGIN) / width,
        (CANVAS_HEIGHT - 2 * CANVAS_MARGIN) / height,
    )
    # Rounded down, so the steps still fit after rounding.
    zoom = max(MIN_ZOOM, int(fit * 100) / 100)
    return {
        "x": round(CANVAS_MARGIN - min(xs) * zoom, 1),
        "y": round(CANVAS_MARGIN - min(ys) * zoom, 1),
        "zoom": zoom,
    }


def _expression_id(step_id: str, index: int, salt: str) -> str:
    return str(uuid.uuid5(_namespace(salt), f"{step_id}:filter:{index}"))


def dataset_filter(
    step: DatasetStep, regions: Mapping[str, Region], salt: str = ""
) -> dict[str, Any] | None:
    """The step's filter in the editor's own format (``DatasetNodeSettings``):
    an area is a spatial ``s_intersects`` expression on ``geom`` whose value is
    the geometry as JSON text, with the ``properties`` the editor reads back
    (``type``, ``label``); each condition is a logical expression."""
    if step.filter is None:
        return None
    expressions: list[dict[str, Any]] = []
    if step.filter.area is not None:
        region = regions.get(step.filter.area)
        if region is None:
            raise DraftError(f"no boundary for region {step.filter.area!r}")
        geometry = {
            **region.geometry,
            # Always a boundary: the editor shows its label (a bounding box
            # type would read as the map extent there).
            "properties": {
                "type": "boundary",
                "label": f"{region.name} (bounding box)"
                if region.as_box
                else region.name,
            },
        }
        expressions.append(
            {
                "id": _expression_id(step.id, 0, salt),
                "type": "spatial",
                "attribute": "geom",
                "expression": "s_intersects",
                "value": json.dumps(
                    geometry, separators=(",", ":"), ensure_ascii=False
                ),
            }
        )
    for index, condition in enumerate(step.filter.where, start=1):
        expressions.append(
            {
                "id": _expression_id(step.id, index, salt),
                "type": "logical",
                "attribute": condition.field,
                "expression": EXPRESSIONS[condition.op],
                "value": condition.value,
            }
        )
    return {"op": "and", "expressions": expressions}


def _dataset_data(
    step: DatasetStep,
    layers: Mapping[int, ProjectLayer],
    regions: Mapping[str, Region],
    salt: str,
) -> dict[str, Any]:
    if step.layer is None:
        assert step.label is not None  # the draft's own rule
        return {"type": "dataset", "label": step.label}
    layer = layers.get(step.layer)
    if layer is None:
        raise DraftError(
            f"step {step.id!r}: there is no layer {step.layer} in the project; "
            "call project_get_layers for the layer_project_ids"
        )
    data: dict[str, Any] = {
        "type": "dataset",
        "label": step.label or layer.name,
        "projectLayerId": layer.layer_project_id,
        "layerId": layer.layer_id,
        "layerName": layer.name,
        # The layer's own filter in the project is not copied: the draft's
        # filter is the step's whole filter, and the settings panel must not
        # copy the layer's in later.
        "filterInitialized": True,
    }
    if layer.geometry_type:
        data["geometryType"] = layer.geometry_type
    if layer.type in ("feature", "table", "raster"):
        data["layerType"] = layer.type
    step_filter = dataset_filter(step, regions, salt)
    if step_filter is not None:
        data["filter"] = step_filter
    return data


def _data(
    step: Step,
    layers: Mapping[int, ProjectLayer],
    regions: Mapping[str, Region],
    titles: Mapping[str, str],
    salt: str,
) -> dict[str, Any]:
    if isinstance(step, DatasetStep):
        return _dataset_data(step, layers, regions, salt)
    if isinstance(step, ToolStep):
        return {
            "type": "tool",
            "processId": step.tool,
            "label": step.label or titles.get(step.tool, step.tool),
            "config": dict(step.settings),
            "status": "idle",
        }
    return {
        "type": "export",
        "label": step.label or step.name,
        "datasetName": step.name,
        "addToProject": True,
        "overwritePrevious": False,
    }


def _edge(
    connection: Connection, by_id: Mapping[str, Step], salt: str
) -> dict[str, Any]:
    source, target = by_id[connection.source], by_id[connection.target]
    edge: dict[str, Any] = {
        "id": _edge_id(connection, salt),
        "source": node_id(source, salt),
        "target": node_id(target, salt),
    }
    # A dataset's output handle has no id in the editor; a tool's is "output".
    if isinstance(source, ToolStep):
        edge["sourceHandle"] = "output"
    edge["targetHandle"] = (
        "input" if isinstance(target, ExportStep) else connection.input
    )
    return edge


def _variable(index: int, variable: Variable, salt: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": f"variable-{uuid.uuid5(_namespace(salt), 'variable:' + variable.name)}",
        "name": variable.name,
        "type": variable.type,
        "order": index,
    }
    if variable.default_value is not None:
        out["defaultValue"] = variable.default_value
    if variable.label is not None:
        out["label"] = variable.label
    if variable.description is not None:
        out["description"] = variable.description
    return out


def to_config(
    draft: Draft,
    *,
    layers: Mapping[int, ProjectLayer],
    regions: Mapping[str, Region],
    titles: Mapping[str, str],
    salt: str = "",
) -> Converted:
    """The editor's workflow config for ``draft``. ``layers`` by
    layer_project_id, ``regions`` by nuts_id, ``titles`` (the tools' titles in
    the user's language) by tool id; ``salt`` enters every derived id (node,
    edge, filter condition, variable). Raises ``DraftError`` for a layer or a
    region that is not given."""
    by_id: dict[str, Step] = {step.id: step for step in draft.steps}
    positions = layout(draft)
    nodes: list[dict[str, Any]] = []
    for step in draft.steps:
        nodes.append(
            {
                "id": node_id(step, salt),
                "type": step.kind,
                "position": positions[step.id],
                "data": _data(step, layers, regions, titles, salt),
            }
        )
    config = {
        "nodes": nodes,
        "edges": [_edge(connection, by_id, salt) for connection in draft.connections],
        "viewport": viewport(positions),
        "variables": [
            _variable(index, variable, salt)
            for index, variable in enumerate(draft.variables)
        ],
    }
    node_ids = {step.id: node_id(step, salt) for step in draft.steps}
    return Converted(
        config=config,
        node_ids=node_ids,
        step_of={node: step_id for step_id, node in node_ids.items()},
        labels={
            step.id: str(node["data"]["label"])
            for step, node in zip(draft.steps, nodes, strict=True)
        },
    )


def downstream(
    start: Iterable[str], connections: Iterable[tuple[str, str]]
) -> frozenset[str]:
    """``start`` and every step that reads from one of them, directly or
    through other steps; ``connections`` as (from, to) pairs."""
    targets: dict[str, list[str]] = {}
    for source, target in connections:
        targets.setdefault(source, []).append(target)
    found = set(start)
    queue = list(found)
    while queue:
        for target in targets.get(queue.pop(), ()):
            if target not in found:
                found.add(target)
                queue.append(target)
    return frozenset(found)


def open_steps(draft: Draft) -> frozenset[str]:
    """Dataset steps left open (layer null) and every step that reads from one,
    directly or through other steps: their fields cannot be known before the
    user chooses the layer (spec §4.4)."""
    return downstream(
        (
            step.id
            for step in draft.steps
            if isinstance(step, DatasetStep) and step.layer is None
        ),
        ((connection.source, connection.target) for connection in draft.connections),
    )
