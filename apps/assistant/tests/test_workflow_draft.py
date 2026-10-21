"""The draft and its conversion into the editor's config (spec §4.1, §4.2).

The shared fixture is read by the web's test as well, which runs the editor's
own rule (isDrawableWorkflowConfig) on every converted config."""

import json
import uuid
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from assistant.workflows.draft import (
    CANVAS_HEIGHT,
    CANVAS_MARGIN,
    CANVAS_WIDTH,
    EXPRESSIONS,
    ID_NAMESPACE,
    MIN_ZOOM,
    NODE_HEIGHT,
    NODE_WIDTH,
    Condition,
    Draft,
    DraftError,
    ProjectLayer,
    Region,
    node_id,
    open_steps,
    region_from_feature,
    to_config,
)

FIXTURE = Path(__file__).parent / "fixtures" / "workflow_drafts.json"
SHARED: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
LAYERS = {row["layer_project_id"]: ProjectLayer(**row) for row in SHARED["layers"]}
TITLES: dict[str, str] = SHARED["titles"]
MUNICH = Region(
    "DE212",
    "München, Kreisfreie Stadt",
    {
        "type": "Polygon",
        "coordinates": [
            [
                [11.36, 48.06],
                [11.72, 48.06],
                [11.72, 48.25],
                [11.36, 48.25],
                [11.36, 48.06],
            ]
        ],
    },
)


def _draft(
    steps: list[dict[str, Any]], connections: list[dict[str, Any]] | None = None
) -> Draft:
    return Draft.model_validate(
        {"name": "Test", "steps": steps, "connections": connections or []}
    )


def _convert(draft: Draft, regions: dict[str, Region] | None = None) -> dict[str, Any]:
    return to_config(draft, layers=LAYERS, regions=regions or {}, titles=TITLES).config


def _shops(**changes: Any) -> dict[str, Any]:
    return {"id": "shops", "kind": "dataset", "layer": 34, **changes}


def _ring() -> dict[str, Any]:
    return {
        "id": "ring",
        "kind": "tool",
        "tool": "buffer",
        "settings": {"distances": [500]},
    }


@pytest.mark.parametrize("case", SHARED["cases"], ids=lambda case: case["note"][:40])
def test_the_shared_fixture_is_what_the_conversion_gives(case: dict[str, Any]) -> None:
    regions = {row["nuts_id"]: Region(**row) for row in case["regions"]}
    draft = Draft.model_validate(case["draft"])
    assert _convert(draft, regions) == case["config"]


def test_the_same_draft_gives_the_same_ids() -> None:
    draft = _draft(
        [_shops(), _ring()],
        [{"from": "shops", "to": "ring", "input": "input_layer_id"}],
    )
    first, second = _convert(draft), _convert(draft)
    assert first == second
    assert [node["id"] for node in first["nodes"]] == [
        f"dataset-{uuid.uuid5(ID_NAMESPACE, 'shops')}",
        f"tool-{uuid.uuid5(ID_NAMESPACE, 'ring')}",
    ]
    assert first["edges"][0]["id"].startswith("edge-")
    converted = to_config(draft, layers=LAYERS, regions={}, titles=TITLES)
    assert converted.node_ids == {
        "shops": first["nodes"][0]["id"],
        "ring": first["nodes"][1]["id"],
    }
    assert converted.step_of == {
        node: step for step, node in converted.node_ids.items()
    }
    assert converted.labels == {"shops": "Supermärkte", "ring": "Buffer"}


def _derived_ids(config: dict[str, Any]) -> list[str]:
    """Every id the conversion derives: steps, connections, filter
    conditions and variables."""
    ids = [node["id"] for node in config["nodes"]]
    ids += [edge["id"] for edge in config["edges"]]
    ids += [
        expression["id"]
        for node in config["nodes"]
        for expression in (node["data"].get("filter") or {}).get("expressions", [])
    ]
    ids += [variable["id"] for variable in config["variables"]]
    return ids


def test_a_salt_enters_every_derived_id() -> None:
    """Export node ids must be unique per workflow (goatlib's export target
    finds a result layer by them), so each salt gives ids of its own; the
    default salt keeps the ids of the shared fixture."""
    draft = Draft.model_validate(
        {
            "name": "Rings",
            "steps": [
                _shops(
                    filter={"where": [{"field": "kette", "op": "=", "value": "Edeka"}]}
                ),
                _ring(),
                {"id": "save", "kind": "export", "name": "Rings"},
            ],
            "connections": [
                {"from": "shops", "to": "ring", "input": "input_layer_id"},
                {"from": "ring", "to": "save"},
            ],
            "variables": [{"name": "minutes", "type": "number", "defaultValue": 15}],
        }
    )

    def convert(salt: str) -> Any:
        return to_config(draft, layers=LAYERS, regions={}, titles=TITLES, salt=salt)

    plain, first, second = convert(""), convert("a1"), convert("b2")
    assert plain.config == _convert(draft)
    assert len(_derived_ids(first.config)) == 7
    assert not set(_derived_ids(first.config)) & set(_derived_ids(second.config))
    assert not set(_derived_ids(first.config)) & set(_derived_ids(plain.config))
    assert convert("a1") == first
    assert first.node_ids == {step.id: node_id(step, "a1") for step in draft.steps}
    assert [node["id"] for node in first.config["nodes"]] == list(
        first.node_ids.values()
    )
    assert first.config["edges"][0]["source"] == first.node_ids["shops"]
    assert first.step_of == {node: step for step, node in first.node_ids.items()}


def test_edges_carry_the_editor_handles() -> None:
    draft = _draft(
        [_shops(), _ring(), {"id": "save", "kind": "export", "name": "Rings"}],
        [
            {"from": "shops", "to": "ring", "input": "input_layer_id"},
            {"from": "ring", "to": "save"},
        ],
    )
    into_tool, into_export = _convert(draft)["edges"]
    assert "sourceHandle" not in into_tool
    assert into_tool["targetHandle"] == "input_layer_id"
    assert (into_export["sourceHandle"], into_export["targetHandle"]) == (
        "output",
        "input",
    )


def test_a_dataset_step_takes_the_layer_from_the_project_list() -> None:
    [node] = _convert(_draft([_shops(label="Shops")]))["nodes"]
    assert node["type"] == "dataset"
    assert node["data"] == {
        "type": "dataset",
        "label": "Shops",
        "projectLayerId": 34,
        "layerId": "e2000000-0000-0000-0000-000000000034",
        "layerName": "Supermärkte",
        "filterInitialized": True,
        "geometryType": "point",
        "layerType": "feature",
    }


def test_an_open_step_gets_only_its_label() -> None:
    [node] = _convert(
        _draft(
            [{"id": "toilets", "kind": "dataset", "label": "Toilets", "layer": None}]
        )
    )["nodes"]
    assert node["data"] == {"type": "dataset", "label": "Toilets"}


def test_a_tool_step_is_named_by_its_label_else_the_tools_title_else_its_id() -> None:
    steps = [
        {"id": "a", "kind": "tool", "tool": "buffer", "label": "500 m rings"},
        {"id": "b", "kind": "tool", "tool": "buffer"},
        {"id": "c", "kind": "tool", "tool": "no_such_tool"},
    ]
    nodes = _convert(_draft(steps))["nodes"]
    assert [node["data"]["label"] for node in nodes] == [
        "500 m rings",
        "Buffer",
        "no_such_tool",
    ]
    assert nodes[0]["data"] == {
        "type": "tool",
        "processId": "buffer",
        "label": "500 m rings",
        "config": {},
        "status": "idle",
    }


def test_an_export_step_saves_into_the_project() -> None:
    [node] = _convert(_draft([{"id": "save", "kind": "export", "name": "Rings"}]))[
        "nodes"
    ]
    assert node["data"] == {
        "type": "export",
        "label": "Rings",
        "datasetName": "Rings",
        "addToProject": True,
        "overwritePrevious": False,
    }


def test_steps_go_left_to_right_by_depth_and_each_column_is_centred() -> None:
    draft = _draft(
        [
            _shops(),
            {"id": "people", "kind": "dataset", "layer": 33},
            {"id": "schools", "kind": "dataset", "layer": 31},
            _ring(),
            {"id": "count", "kind": "tool", "tool": "aggregate_polygon"},
            {"id": "save", "kind": "export", "name": "Counts"},
        ],
        [
            {"from": "shops", "to": "ring", "input": "input_layer_id"},
            {"from": "ring", "to": "count", "input": "area_layer_id"},
            {"from": "people", "to": "count", "input": "source_layer_id"},
            {"from": "count", "to": "save"},
        ],
    )
    positions = {node["id"]: node["position"] for node in _convert(draft)["nodes"]}
    at = {step.id: positions[node_id(step)] for step in draft.steps}
    assert at == {
        "shops": {"x": 0, "y": -200},
        "people": {"x": 0, "y": 0},
        "schools": {"x": 0, "y": 200},
        "ring": {"x": 360, "y": 0},
        "count": {"x": 720, "y": 0},
        "save": {"x": 1080, "y": 0},
    }


def test_a_loop_is_laid_out_after_the_steps_leading_into_it() -> None:
    draft = _draft(
        [_shops(), _ring(), {"id": "cut", "kind": "tool", "tool": "clip"}],
        [
            {"from": "shops", "to": "ring", "input": "input_layer_id"},
            {"from": "ring", "to": "cut", "input": "input_layer_id"},
            {"from": "cut", "to": "ring", "input": "overlay_layer_id"},
        ],
    )
    xs = [node["position"]["x"] for node in _convert(draft)["nodes"]]
    assert xs == [0, 360, 720]


def test_the_viewport_shows_every_step() -> None:
    one = _convert(_draft([_shops()]))
    assert one["viewport"] == {"x": CANVAS_MARGIN, "y": CANVAS_MARGIN, "zoom": 1.0}
    chain = [_shops()] + [
        {"id": f"t{n}", "kind": "tool", "tool": "buffer"} for n in range(12)
    ]
    connections = [{"from": "shops", "to": "t0", "input": "input_layer_id"}] + [
        {"from": f"t{n}", "to": f"t{n + 1}", "input": "input_layer_id"}
        for n in range(11)
    ]
    config = _convert(_draft(chain, connections))
    view = config["viewport"]
    assert MIN_ZOOM <= view["zoom"] < 1
    for node in config["nodes"]:
        x = node["position"]["x"] * view["zoom"] + view["x"]
        y = node["position"]["y"] * view["zoom"] + view["y"]
        assert x >= 0 and x + NODE_WIDTH * view["zoom"] <= CANVAS_WIDTH
        assert y >= 0 and y + NODE_HEIGHT * view["zoom"] <= CANVAS_HEIGHT


@pytest.mark.parametrize(
    ("op", "value"),
    [
        ("=", "Edeka"),
        ("!=", "Lidl"),
        ("<", 3),
        ("<=", 3.5),
        (">", 10),
        (">=", 0),
        ("in", ["Edeka", "Rewe"]),
        ("contains", "markt"),
    ],
)
def test_conditions_use_the_editors_expressions(op: str, value: Any) -> None:
    step = _shops(filter={"where": [{"field": "kette", "op": op, "value": value}]})
    [node] = _convert(_draft([step]))["nodes"]
    [expression] = node["data"]["filter"]["expressions"]
    assert node["data"]["filter"]["op"] == "and"
    assert expression == {
        "id": str(uuid.uuid5(ID_NAMESPACE, "shops:filter:1")),
        "type": "logical",
        "attribute": "kette",
        "expression": EXPRESSIONS[op],
        "value": value,
    }


def test_an_area_is_a_spatial_expression_with_the_regions_boundary() -> None:
    step = _shops(filter={"area": "DE212"})
    [node] = _convert(_draft([step]), {"DE212": MUNICH})["nodes"]
    [expression] = node["data"]["filter"]["expressions"]
    assert (expression["type"], expression["attribute"], expression["expression"]) == (
        "spatial",
        "geom",
        "s_intersects",
    )
    assert json.loads(expression["value"]) == {
        **MUNICH.geometry,
        "properties": {"type": "boundary", "label": "München, Kreisfreie Stadt"},
    }
    with pytest.raises(DraftError, match="no boundary for region 'DE212'"):
        _convert(_draft([step]))


def test_a_large_boundary_becomes_its_bounding_box() -> None:
    """Review Focus 5: a state's boundary is not stored in the workflow."""
    ring = [[round(11 + n / 1000, 3), round(48 + (n % 7) / 100, 2)] for n in range(400)]
    ring.append([11.0, 48.0])
    feature = {
        "type": "Feature",
        "properties": {"nuts_id": "DE2", "nuts_name": "Bayern"},
        "geometry": {"type": "Polygon", "coordinates": [ring]},
    }
    small = region_from_feature("DE2", feature)
    assert (small.name, small.as_box) == ("Bayern", False)
    assert small.geometry == feature["geometry"]
    boxed = region_from_feature("DE2", feature, max_bytes=1000)
    assert boxed.as_box
    assert boxed.geometry == {
        "type": "Polygon",
        "coordinates": [
            [[11.0, 48.0], [11.399, 48.0], [11.399, 48.06], [11.0, 48.06], [11.0, 48.0]]
        ],
    }
    with pytest.raises(DraftError, match="has no boundary"):
        region_from_feature("DE2", {"type": "Feature", "geometry": None})


def test_an_open_step_takes_no_filter() -> None:
    """Review Focus 2: choosing the layer in the editor would replace it."""
    with pytest.raises(ValidationError, match="a step left open takes no filter"):
        _draft(
            [
                {
                    "id": "toilets",
                    "kind": "dataset",
                    "label": "Toilets",
                    "layer": None,
                    "filter": {"area": "DE212"},
                }
            ]
        )


def test_an_open_step_is_named_for_what_is_missing() -> None:
    with pytest.raises(ValidationError, match="needs a label"):
        _draft([{"id": "toilets", "kind": "dataset", "layer": None}])
    with pytest.raises(ValidationError, match="Field required"):
        _draft([{"id": "toilets", "kind": "dataset", "label": "Toilets"}])


@pytest.mark.parametrize(
    ("steps", "connections", "message"),
    [
        ([_shops(), _shops()], [], "two steps have the id 'shops'"),
        (
            [_shops()],
            [{"from": "shops", "to": "ring", "input": "x"}],
            "unknown step 'ring'",
        ),
        (
            [{"id": "save", "kind": "export", "name": "S"}, _ring()],
            [{"from": "save", "to": "ring", "input": "input_layer_id"}],
            "nothing reads from it",
        ),
        ([_ring(), _shops()], [{"from": "ring", "to": "shops"}], "reads from nothing"),
        (
            [_ring(), {"id": "save", "kind": "export", "name": "S"}],
            [{"from": "ring", "to": "save", "input": "input"}],
            "has no input",
        ),
        (
            [_shops(), _ring()],
            [{"from": "shops", "to": "ring"}],
            "needs the input it feeds",
        ),
        (
            [_shops(), {"id": "people", "kind": "dataset", "layer": 33}, _ring()],
            [
                {"from": "shops", "to": "ring", "input": "input_layer_id"},
                {"from": "people", "to": "ring", "input": "input_layer_id"},
            ],
            "two connections feed 'ring' 'input_layer_id'",
        ),
    ],
)
def test_the_draft_graph_follows_the_editors_rules(
    steps: list[dict[str, Any]], connections: list[dict[str, Any]], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        _draft(steps, connections)


@pytest.mark.parametrize(
    ("condition", "message"),
    [
        ({"field": "a", "op": "in", "value": "x"}, "non-empty list"),
        ({"field": "a", "op": "=", "value": ["x"]}, "only 'in' takes a list"),
        ({"field": "a", "op": "contains", "value": 3}, "'contains' takes text"),
        ({"field": "a", "op": ">", "value": True}, "yes/no value"),
    ],
)
def test_a_condition_value_fits_its_operator(
    condition: dict[str, Any], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        Condition.model_validate(condition)
    assert (
        Condition.model_validate({"field": "a", "op": "=", "value": True}).value is True
    )


def test_an_unknown_layer_is_a_draft_error() -> None:
    with pytest.raises(DraftError, match="no layer 99 in the project"):
        _convert(_draft([_shops(layer=99)]))


def test_open_steps_follow_the_connections() -> None:
    draft = _draft(
        [
            {"id": "toilets", "kind": "dataset", "label": "Toilets", "layer": None},
            _shops(),
            {"id": "walk", "kind": "tool", "tool": "catchment_area_v2"},
            {"id": "count", "kind": "tool", "tool": "aggregate_points"},
            {"id": "other", "kind": "tool", "tool": "buffer"},
            {"id": "save", "kind": "export", "name": "S"},
        ],
        [
            {"from": "toilets", "to": "walk", "input": "starting_points"},
            {"from": "walk", "to": "count", "input": "area_layer_id"},
            {"from": "shops", "to": "count", "input": "source_layer_id"},
            {"from": "shops", "to": "other", "input": "input_layer_id"},
            {"from": "count", "to": "save"},
        ],
    )
    assert open_steps(draft) == {"toilets", "walk", "count", "save"}


def test_variables_get_the_editors_shape() -> None:
    draft = Draft.model_validate(
        {
            "name": "V",
            "steps": [_shops()],
            "variables": [
                {"name": "minutes", "type": "number", "defaultValue": 15},
                {
                    "name": "mode",
                    "type": "string",
                    "label": "Mode",
                    "description": "How people travel",
                },
            ],
        }
    )
    assert _convert(draft)["variables"] == [
        {
            "id": f"variable-{uuid.uuid5(ID_NAMESPACE, 'variable:minutes')}",
            "name": "minutes",
            "type": "number",
            "order": 0,
            "defaultValue": 15,
        },
        {
            "id": f"variable-{uuid.uuid5(ID_NAMESPACE, 'variable:mode')}",
            "name": "mode",
            "type": "string",
            "order": 1,
            "label": "Mode",
            "description": "How people travel",
        },
    ]
    with pytest.raises(ValidationError, match="two variables"):
        Draft.model_validate(
            {
                "name": "V",
                "steps": [_shops()],
                "variables": [{"name": "a", "type": "string"}] * 2,
            }
        )


@pytest.mark.parametrize("step_id", ["", "has space", "x" * 41, "ümlaut"])
def test_a_step_id_is_short_and_plain(step_id: str) -> None:
    with pytest.raises(ValidationError):
        _draft([_shops(id=step_id)])
