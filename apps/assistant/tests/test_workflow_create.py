"""workflow_check_draft and workflow_create (spec §4.3, §4.4, §9): the draft
is converted with the project's layers, checked by processes, mapped back to
the draft's ids, and created only when nothing but open steps remain."""

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
import pytest
from pydantic_ai.exceptions import ToolFailed

from assistant.context import parse_context
from assistant.db import Database
from assistant.repo import Repository
from assistant.tools.runtime import InputInvalid, execute
from assistant.tools.testing import Answer, Recorder, fake_clients, tool_env
from assistant.tools.workflow_tools import clear_description_cache
from assistant.tools.workflows import (
    CHECK_DRAFT,
    CHECK_UNAVAILABLE,
    CREATE,
    NOT_CHECKED,
    NOT_READABLE,
    VIEWER_WORKFLOWS,
    WorkflowCreated,
)

#: The toolbox (``GET /processes``) and the process descriptions
#: (``GET /processes/{id}``) captured from processes.
FIXTURE = Path(__file__).parent / "fixtures" / "process_descriptions.json"
PROCESSES: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
DESCRIPTIONS: dict[str, dict[str, Any]] = PROCESSES["descriptions"]
PROJECT = "00000000-0000-0000-0000-0000000005e4"
PAGE = parse_context({"surface": "project.workflows", "project_id": PROJECT})
WORKFLOW_ID = "0b6f0000-0000-0000-0000-00000000f10f"
LAYERS = [
    {
        "id": 31,
        "layer_id": "e2000000-0000-0000-0000-000000000031",
        "name": "Schulen",
        "type": "feature",
        "feature_layer_geometry_type": "point",
    },
    {
        "id": 33,
        "layer_id": "e2000000-0000-0000-0000-000000000033",
        "name": "Einwohner Raster",
        "type": "feature",
        "feature_layer_geometry_type": "polygon",
    },
    {
        "id": 36,
        "layer_id": "e2000000-0000-0000-0000-000000000036",
        "name": "Intern",
        "type": "feature",
        "locked": True,
    },
]
DRAFT: dict[str, Any] = {
    "name": "Schools: 15-minute walk",
    "steps": [
        {
            "id": "schools",
            "kind": "dataset",
            "label": "Schools",
            "layer": 31,
            "filter": {
                "area": "DE212",
                "where": [{"field": "schulart", "op": "=", "value": "Grundschule"}],
            },
        },
        {"id": "residents", "kind": "dataset", "layer": 33},
        {
            "id": "walk",
            "kind": "tool",
            "tool": "catchment_area_v2",
            "label": "15 minutes on foot",
            "settings": {"routing_mode": "walking", "max_cost": 15, "steps": 1},
        },
        {
            "id": "count",
            "kind": "tool",
            "tool": "aggregate_polygon",
            "settings": {
                "area_type": "polygon",
                "column_statistics": [{"operation": "sum", "field": "einwohner"}],
            },
        },
        {"id": "save", "kind": "export", "name": "Residents within 15 minutes"},
    ],
    "connections": [
        {"from": "schools", "to": "walk", "input": "starting_points"},
        {"from": "walk", "to": "count", "input": "area_layer_id"},
        {"from": "residents", "to": "count", "input": "source_layer_id"},
        {"from": "count", "to": "save"},
    ],
}
OPEN_DRAFT: dict[str, Any] = {
    "name": "Toilets: 5-minute walk",
    "steps": [
        {"id": "toilets", "kind": "dataset", "label": "Public toilets", "layer": None},
        {
            "id": "walk",
            "kind": "tool",
            "tool": "catchment_area_v2",
            "settings": {"routing_mode": "walking", "max_cost": 5},
        },
        {"id": "save", "kind": "export", "name": "Toilets within 5 minutes"},
    ],
    "connections": [
        {"from": "toilets", "to": "walk", "input": "starting_points"},
        {"from": "walk", "to": "save"},
    ],
}
MUNICH = {
    "type": "Feature",
    "properties": {
        "nuts_id": "DE212",
        "nuts_name": "München, Kreisfreie Stadt",
        "level": 3,
        "country": "DE",
    },
    "geometry": {
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
}


@pytest.fixture(autouse=True)
def _fresh_cache() -> Iterator[None]:
    clear_description_cache()
    yield
    clear_description_cache()


def _issue(
    code: str,
    step: str | None,
    message: str,
    level: str = "error",
    draft: dict[str, Any] = DRAFT,
    field: str | None = None,
) -> dict[str, Any]:
    """A row of processes' check about ``step`` of ``draft``. Each call
    converts with ids of its own, so the row holds the step's position in the
    draft, and the fake check names the node at that position of the config
    it checks (the steps come in draft order)."""
    positions = [item["id"] for item in draft["steps"]]
    return {
        "code": code,
        "level": level,
        "node_ids": [positions.index(step)] if step else [],
        "field": field,
        "message": message,
        "params": {},
        "source": "check",
    }


def _answer(issues: list[dict[str, Any]]) -> Any:
    """Processes' check answering ``issues`` with the node ids of the
    config it was sent."""

    def respond(request: httpx.Request) -> httpx.Response:
        nodes = json.loads(request.content)["nodes"]
        rows = [
            {**row, "node_ids": [nodes[index]["id"] for index in row["node_ids"]]}
            for row in issues
        ]
        return httpx.Response(200, json={"issues": rows})

    return respond


def _toolbox(
    *, extra: list[dict[str, Any]] | None = None, without: frozenset[str] = frozenset()
) -> Any:
    """``GET /processes`` for this user: the captured toolbox in the asked
    language, without the tools in ``without`` (processes leaves a beta tool
    out for a user outside the beta), with the rows of ``extra`` added."""

    def respond(request: httpx.Request) -> httpx.Response:
        language = "de" if request.headers.get("accept-language") == "de" else "en"
        rows = [row for row in PROCESSES["list"][language] if row["id"] not in without]
        return httpx.Response(
            200, json={"processes": [*rows, *(extra or [])], "links": []}
        )

    return respond


def _services(
    *,
    issues: list[dict[str, Any]] | None = None,
    check: Any = None,
    created: Any = None,
    queryables: Any = None,
    region: Any = MUNICH,
    descriptions: Mapping[str, Answer] | None = None,
    toolbox: Answer | None = None,
) -> tuple[Recorder, Recorder, Recorder, Recorder]:
    """Fake services; processes lists the captured toolbox (or ``toolbox``)
    and describes the captured tools, or the tools of ``descriptions`` (tool
    id -> its answer) on top of them."""
    core = Recorder(
        {
            ("GET", f"/api/v2/project/{PROJECT}/layer"): LAYERS,
            ("POST", f"/api/v2/project/{PROJECT}/workflow"): created
            if created is not None
            else (
                lambda request: httpx.Response(
                    201,
                    json={
                        **json.loads(request.content),
                        "id": WORKFLOW_ID,
                        "project_id": PROJECT,
                    },
                )
            ),
        }
    )
    described = {**DESCRIPTIONS, **(descriptions or {})}
    processes = Recorder(
        {
            ("GET", "/processes"): toolbox if toolbox is not None else _toolbox(),
            **{
                ("GET", f"/processes/{tool}"): answer
                for tool, answer in described.items()
            },
            ("POST", "/workflows/check"): check
            if check is not None
            else _answer(issues or []),
        }
    )
    geoapi = Recorder(
        {
            (
                "GET",
                "/collections/e2000000-0000-0000-0000-000000000031/queryables",
            ): queryables
            if queryables is not None
            else {
                "properties": {
                    "name": {"type": "string"},
                    "schulart": {"type": "string"},
                    "geom": {"$ref": "geometry"},
                }
            },
        }
    )
    catalog = Recorder({("GET", "/stac/nuts/DE212/geometry"): region})
    return core, processes, geoapi, catalog


def _env(
    core: Recorder, processes: Recorder, geoapi: Recorder, catalog: Recorder
) -> Any:
    return tool_env(
        fake_clients(core=core, processes=processes, geoapi=geoapi, catalog=catalog),
        page=PAGE,
    )


async def test_check_converts_the_draft_and_maps_the_issues_back() -> None:
    core, processes, geoapi, catalog = _services(
        issues=[
            _issue(
                "setting_required",
                "count",
                "Aggregate Polygons: Area Type is required.",
            )
        ]
    )
    result = await execute(
        CHECK_DRAFT, _env(core, processes, geoapi, catalog), {"draft": DRAFT}
    )
    assert result == {
        "checked": True,
        "issues": [
            {
                "code": "setting_required",
                "level": "error",
                "steps": ["count"],
                "message": "Aggregate Polygons: Area Type is required.",
            }
        ],
        "blocking": 1,
        "open": 0,
    }
    [check] = [r for r in processes.requests if r.url.path == "/workflows/check"]
    body = json.loads(check.content)
    assert body["project_id"] == PROJECT
    assert [n["id"].split("-")[0] for n in body["nodes"]] == [
        s["kind"] for s in DRAFT["steps"]
    ]
    assert len({n["id"] for n in body["nodes"]}) == len(DRAFT["steps"])
    assert check.headers["accept-language"] == "en"
    assert core.paths() == [f"/api/v2/project/{PROJECT}/layer"]


async def test_check_adds_a_filter_field_the_layer_lacks() -> None:
    draft = json.loads(json.dumps(DRAFT))
    draft["steps"][0]["filter"]["where"][0]["field"] = "type"
    services = _services()
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
    [issue] = result["issues"]
    assert issue == {
        "code": "filter_field_not_in_layer",
        "level": "error",
        "steps": ["schools"],
        "field": "type",
        "message": "Schools: the filter's field 'type' is not in the layer. Its fields: name, schulart.",
    }


async def test_a_check_that_cannot_run_says_so() -> None:
    services = _services(check=httpx.Response(503, json={"detail": "busy"}))
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": DRAFT})
    assert result == {
        "checked": False,
        "issues": [],
        "blocking": 0,
        "open": 0,
        "note": NOT_CHECKED,
    }


async def test_create_saves_the_config_the_check_checked() -> None:
    core, processes, geoapi, catalog = _services()
    env = _env(core, processes, geoapi, catalog)
    result = await execute(CREATE, env, {"draft": DRAFT}, tool_call_id="c1")
    checked = json.loads(
        next(r for r in processes.requests if r.url.path == "/workflows/check").content
    )
    posted = json.loads(next(r for r in core.requests if r.method == "POST").content)
    assert posted["name"] == "Schools: 15-minute walk"
    assert (posted["is_default"], posted["description"]) == (False, None)
    assert posted["config"]["nodes"] == checked["nodes"]
    assert posted["config"]["edges"] == checked["edges"]
    assert result == {
        "workflow": {
            "id": WORKFLOW_ID,
            "name": "Schools: 15-minute walk",
            "project_id": PROJECT,
        },
        "open_issues": [],
        "groups": [
            {
                "items": [
                    {
                        "kind": "workflow",
                        "id": WORKFLOW_ID,
                        "project_id": PROJECT,
                        "name": "Schools: 15-minute walk",
                    }
                ]
            }
        ],
    }


def _checked_ids(processes: Recorder) -> list[list[str]]:
    return [
        [node["id"] for node in json.loads(request.content)["nodes"]]
        for request in processes.requests
        if request.url.path == "/workflows/check"
    ]


async def test_each_conversion_gets_ids_of_its_own() -> None:
    """Export node ids are unique per workflow, so a draft created twice
    must not share them: every call converts the draft once, with new ids,
    and the create saves the ids its own check checked."""
    core, processes, geoapi, catalog = _services()
    env = _env(core, processes, geoapi, catalog)
    await execute(CHECK_DRAFT, env, {"draft": DRAFT})
    await execute(CHECK_DRAFT, env, {"draft": DRAFT})
    await execute(CREATE, env, {"draft": DRAFT}, tool_call_id="c1")
    first, second, created = _checked_ids(processes)
    assert not set(first) & set(second)
    assert not set(created) & (set(first) | set(second))
    posted = json.loads(next(r for r in core.requests if r.method == "POST").content)
    assert [node["id"] for node in posted["config"]["nodes"]] == created


async def test_create_refuses_while_a_blocking_issue_remains() -> None:
    core, processes, geoapi, catalog = _services(
        issues=[
            _issue(
                "setting_required",
                "count",
                "Aggregate Polygons: Area Type is required.",
            )
        ]
    )
    with pytest.raises(ToolFailed) as caught:
        await execute(CREATE, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert "Not created: 1 issue(s) must be fixed first." in caught.value.message
    assert "Aggregate Polygons: Area Type is required." in caught.value.message
    assert [r.method for r in core.requests] == ["GET"]


async def test_create_accepts_open_steps_and_names_what_is_open() -> None:
    core, processes, geoapi, catalog = _services(
        issues=[
            _issue(
                "layer_not_chosen",
                "toilets",
                "Public toilets: no layer is chosen.",
                draft=OPEN_DRAFT,
            ),
            _issue(
                "step_not_connected", "save", "x", level="warning", draft=OPEN_DRAFT
            ),
        ]
    )
    result = await execute(
        CREATE, _env(core, processes, geoapi, catalog), {"draft": OPEN_DRAFT}
    )
    assert result["open_issues"] == [
        {
            "step": "Public toilets",
            "code": "layer_not_chosen",
            "message": "Public toilets: no layer is chosen.",
        }
    ]


async def test_create_refuses_when_the_check_cannot_run() -> None:
    core, processes, geoapi, catalog = _services(check=httpx.Response(500, json={}))
    with pytest.raises(ToolFailed, match="could not be checked right now"):
        await execute(CREATE, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert CHECK_UNAVAILABLE.startswith("Not created")
    assert [r.method for r in core.requests] == ["GET"]


@pytest.mark.parametrize("status", [401, 403])
async def test_a_viewer_is_told_and_nothing_is_retried(status: int) -> None:
    services = _services(
        created=httpx.Response(status, json={"detail": "Unauthorized"})
    )
    with pytest.raises(ToolFailed) as caught:
        await execute(CREATE, _env(*services), {"draft": DRAFT})
    assert caught.value.message == VIEWER_WORKFLOWS
    assert [r.method for r in services[0].requests] == ["GET", "POST"]


async def test_a_layer_not_in_the_project_or_locked_goes_back_to_the_model() -> None:
    for layer, message in (
        (99, "no layer 99 in the project"),
        (36, "'Intern' is in the project, but the user has no access"),
    ):
        draft = json.loads(json.dumps(DRAFT))
        draft["steps"][1]["layer"] = layer
        services = _services()
        with pytest.raises(InputInvalid, match=message):
            await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
        assert all(
            "e2000000-0000-0000-0000-000000000036" not in r.content.decode()
            for r in services[1].requests
        )


async def test_a_region_comes_from_the_catalog_and_a_box_is_noted() -> None:
    """Review Focus 5: a boundary too large to store is its bounding box, and the result says so."""
    huge = {
        **MUNICH,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[11.36 + n / 100000, 48.06] for n in range(30000)]
                + [[11.36, 48.25], [11.36, 48.06]]
            ],
        },
    }
    core, processes, geoapi, catalog = _services(region=huge)
    result = await execute(
        CREATE, _env(core, processes, geoapi, catalog), {"draft": DRAFT}
    )
    assert catalog.paths() == ["/stac/nuts/DE212/geometry"]
    assert result["notes"] == [
        "Schools: the area is the bounding box of München, Kreisfreie Stadt, not its boundary, "
        "which is too detailed to store in a workflow. Features inside the box but outside the "
        "region are kept too."
    ]
    posted = json.loads(next(r for r in core.requests if r.method == "POST").content)
    area = json.loads(
        posted["config"]["nodes"][0]["data"]["filter"]["expressions"][0]["value"]
    )
    assert area["properties"] == {
        "type": "boundary",
        "label": "München, Kreisfreie Stadt (bounding box)",
    }
    unknown = _services(
        region=httpx.Response(404, json={"detail": "NUTS region not found"})
    )
    with pytest.raises(InputInvalid, match="find it with catalog_find_region"):
        await execute(CHECK_DRAFT, _env(*unknown), {"draft": DRAFT})


async def test_a_layer_still_copying_does_not_block_the_create() -> None:
    """Review Focus 4: geoapi cannot read the fields of a catalog layer yet."""
    draft = json.loads(json.dumps(DRAFT))
    draft["steps"][0]["filter"]["where"][0]["field"] = "type"
    core, processes, geoapi, catalog = _services(
        queryables=httpx.Response(404, json={"detail": "not found"})
    )
    result = await execute(
        CREATE, _env(core, processes, geoapi, catalog), {"draft": draft}
    )
    assert result["workflow"]["id"] == WORKFLOW_ID
    assert result["open_issues"] == []


@pytest.mark.parametrize(
    "properties",
    [{}, {"geom": {"$ref": "https://geojson.org/schema/Geometry.json"}}],
    ids=["none", "only-the-geometry"],
)
async def test_a_layer_whose_fields_are_not_listed_yet_does_not_block(
    properties: dict[str, Any],
) -> None:
    """geoapi lists no field of a table it does not see yet (a catalog
    dataset just added): a layer without a field besides its geometry is not
    judged, as one whose fields cannot be read."""
    draft = json.loads(json.dumps(DRAFT))
    draft["steps"][0]["filter"]["where"][0]["field"] = "type"
    core, processes, geoapi, catalog = _services(
        queryables={"type": "object", "properties": properties}
    )
    checked = await execute(
        CHECK_DRAFT, _env(core, processes, geoapi, catalog), {"draft": draft}
    )
    assert (checked["checked"], checked["issues"]) == (True, [])
    result = await execute(
        CREATE, _env(core, processes, geoapi, catalog), {"draft": draft}
    )
    assert result["workflow"]["id"] == WORKFLOW_ID


async def test_the_pack_needs_an_open_project() -> None:
    env = tool_env(fake_clients(), page=parse_context(None))
    with pytest.raises(ToolFailed, match="Open a project first"):
        await execute(CHECK_DRAFT, env, {"draft": DRAFT})


def _checked(processes: Recorder) -> bool:
    return "/workflows/check" in processes.paths()


async def test_a_draft_whose_tools_cannot_be_described_is_unchecked() -> None:
    """Without the tools' descriptions neither the layer inputs nor the field
    settings can be judged: nothing is checked or created."""
    failing = {"aggregate_polygon": httpx.Response(500, json={})}
    core, processes, geoapi, catalog = _services(descriptions=failing)
    result = await execute(
        CHECK_DRAFT, _env(core, processes, geoapi, catalog), {"draft": DRAFT}
    )
    assert result == {
        "checked": False,
        "issues": [],
        "blocking": 0,
        "open": 0,
        "note": NOT_CHECKED,
    }
    assert not _checked(processes)
    core, processes, geoapi, catalog = _services(descriptions=failing)
    with pytest.raises(ToolFailed) as caught:
        await execute(CREATE, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert caught.value.message == CHECK_UNAVAILABLE
    assert not _checked(processes)
    assert [r.method for r in core.requests] == ["GET"]


async def test_each_tool_is_described_once_and_names_its_step() -> None:
    core, processes, geoapi, catalog = _services()
    await execute(CREATE, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert sorted(processes.paths()) == [
        "/processes",
        "/processes/aggregate_polygon",
        "/processes/catchment_area_v2",
        "/workflows/check",
    ]
    posted = json.loads(next(r for r in core.requests if r.method == "POST").content)
    labels = [node["data"]["label"] for node in posted["config"]["nodes"]]
    assert labels[2:4] == ["15 minutes on foot", "Aggregate Polygons"]


LOCKED_LAYER = "e2000000-0000-0000-0000-000000000036"


@pytest.mark.parametrize("tool", [CHECK_DRAFT, CREATE], ids=["check", "create"])
async def test_a_setting_cannot_feed_a_layer_input(tool: Any) -> None:
    """A layer reaches a tool only through a connection from a dataset step,
    so the locked-layer refusal cannot be bypassed with a layer id in a
    setting."""
    draft = json.loads(json.dumps(DRAFT))
    draft["steps"][2]["settings"]["point_grid_layer_id"] = LOCKED_LAYER
    core, processes, geoapi, catalog = _services()
    with pytest.raises(InputInvalid) as caught:
        await execute(tool, _env(core, processes, geoapi, catalog), {"draft": draft})
    assert "step 'walk'" in caught.value.message
    assert "point_grid_layer_id" in caught.value.message
    assert "connect a dataset step" in caught.value.message
    assert not _checked(processes)
    assert all(LOCKED_LAYER not in r.content.decode() for r in processes.requests)
    assert [r.method for r in core.requests] == ["GET"]


async def test_a_hidden_opportunity_handle_is_no_setting_either() -> None:
    draft = {
        "name": "Schools: gravity",
        "steps": [
            {"id": "schools", "kind": "dataset", "layer": 31},
            {
                "id": "heat",
                "kind": "tool",
                "tool": "heatmap_gravity",
                "settings": {
                    "routing_mode": "walking",
                    "opportunity_layer_2_id": {"layer_id": LOCKED_LAYER},
                },
            },
        ],
        "connections": [
            {"from": "schools", "to": "heat", "input": "opportunity_layer_1_id"}
        ],
    }
    services = _services()
    with pytest.raises(InputInvalid, match="opportunity_layer_2_id"):
        await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
    assert not _checked(services[1])


async def test_a_required_field_of_an_open_input_stays_open() -> None:
    """catchment_area_v2's reference_field reads the starting points, which
    come from the step left open: its fields are not known yet."""
    core, processes, geoapi, catalog = _services(
        issues=[
            _issue(
                "setting_required",
                "walk",
                "Catchment Area: Reference field is required.",
                draft=OPEN_DRAFT,
                field="reference_field",
            )
        ]
    )
    result = await execute(
        CREATE, _env(core, processes, geoapi, catalog), {"draft": OPEN_DRAFT}
    )
    assert result["open_issues"] == [
        {
            "step": "Catchment Area",
            "code": "setting_required",
            "message": "Catchment Area: Reference field is required.",
        }
    ]


def _two_inputs(open_input: str, chosen_input: str) -> dict[str, Any]:
    return {
        "name": "Residents per district",
        "steps": [
            {"id": "districts", "kind": "dataset", "label": "Districts", "layer": None},
            {"id": "residents", "kind": "dataset", "layer": 33},
            {
                "id": "count",
                "kind": "tool",
                "tool": "aggregate_polygon",
                "settings": {"area_type": "polygon"},
            },
            {"id": "save", "kind": "export", "name": "Residents per district"},
        ],
        "connections": [
            {"from": "districts", "to": "count", "input": open_input},
            {"from": "residents", "to": "count", "input": chosen_input},
            {"from": "count", "to": "save"},
        ],
    }


@pytest.mark.parametrize(
    ("open_input", "chosen_input", "blocking", "still_open"),
    [
        ("source_layer_id", "area_layer_id", 0, 1),
        ("area_layer_id", "source_layer_id", 1, 0),
    ],
    ids=["read-input-open", "read-input-chosen"],
)
async def test_a_required_field_setting_stays_open_only_while_its_layer_is_open(
    open_input: str, chosen_input: str, blocking: int, still_open: int
) -> None:
    """aggregate_polygon's group_by_field reads source_layer_id: open while
    that input comes from the step left open, blocking once it has a layer,
    although the step reads from an open step either way."""
    draft = _two_inputs(open_input, chosen_input)
    services = _services(
        issues=[
            _issue(
                "setting_required",
                "count",
                "Aggregate Polygons: Group by is required.",
                draft=draft,
                field="group_by_field",
            )
        ]
    )
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
    assert (result["blocking"], result["open"]) == (blocking, still_open)
    if blocking:
        with pytest.raises(ToolFailed, match="Not created: 1 issue"):
            await execute(CREATE, _env(*services), {"draft": draft})
    else:
        created = await execute(CREATE, _env(*services), {"draft": draft})
        assert created["workflow"]["id"] == WORKFLOW_ID


@pytest.mark.parametrize(
    ("field", "still_open"),
    [
        ("starting_points", True),
        ("reference_field", True),
        (None, True),
        ("routing_mode", False),
    ],
    ids=["open-input", "its-field-setting", "whole-step", "a-choice"],
)
async def test_a_rejected_setting_downstream_stays_open_only_if_the_layer_reaches_it(
    field: str | None, still_open: bool
) -> None:
    """On a step reading from a step left open, a setting the tool rejects
    stays open when the layer still to be chosen can be its cause: the open
    input itself, a field setting reading it, or the step's validation as a
    whole. A value like routing_mode "foot" is wrong whatever layer the user
    picks, so it blocks."""
    services = _services(
        issues=[
            _issue(
                "setting_invalid",
                "walk",
                "Catchment Area: it does not fit.",
                draft=OPEN_DRAFT,
                field=field,
            )
        ]
    )
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": OPEN_DRAFT})
    assert (result["blocking"], result["open"]) == ((0, 1) if still_open else (1, 0))
    if still_open:
        created = await execute(CREATE, _env(*services), {"draft": OPEN_DRAFT})
        assert [issue["code"] for issue in created["open_issues"]] == [
            "setting_invalid"
        ]
    else:
        with pytest.raises(ToolFailed, match="Not created: 1 issue"):
            await execute(CREATE, _env(*services), {"draft": OPEN_DRAFT})


@pytest.mark.parametrize(
    ("open_input", "chosen_input", "blocking", "still_open"),
    [
        ("source_layer_id", "area_layer_id", 0, 1),
        ("area_layer_id", "source_layer_id", 1, 0),
    ],
    ids=["read-input-open", "read-input-chosen"],
)
async def test_a_statistic_without_a_field_stays_open_only_while_its_layer_is_open(
    open_input: str, chosen_input: str, blocking: int, still_open: int
) -> None:
    """column_statistics' items read their field from source_layer_id (the
    item's own widget names it): a sum without its field stays open while
    that input comes from the step left open."""
    draft = _two_inputs(open_input, chosen_input)
    draft["steps"][2]["settings"]["column_statistics"] = [{"operation": "sum"}]
    services = _services(
        issues=[
            _issue(
                "setting_invalid",
                "count",
                "Aggregate Polygons: Statistics Configuration: Field is required.",
                draft=draft,
                field="column_statistics",
            )
        ]
    )
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
    assert (result["blocking"], result["open"]) == (blocking, still_open)


@pytest.mark.parametrize(
    ("field", "still_open"),
    [
        ("opportunity_1_potential_field", True),
        ("opportunity_1_input_path", True),
        ("opportunity_2_potential_field", False),
        ("routing_mode", False),
    ],
)
async def test_an_opportunitys_setting_stays_open_while_its_layer_is_open(
    field: str, still_open: bool
) -> None:
    """A heatmap keeps the settings of the opportunity on handle N as
    opportunity_<N>_<name>: open for the handle fed from the step left open,
    blocking for the one whose layer is chosen."""
    draft = {
        "name": "Toilets and schools: gravity",
        "steps": [
            {"id": "toilets", "kind": "dataset", "label": "Toilets", "layer": None},
            {"id": "schools", "kind": "dataset", "layer": 31},
            {
                "id": "heat",
                "kind": "tool",
                "tool": "heatmap_gravity",
                "settings": {"routing_mode": "walking"},
            },
            {"id": "save", "kind": "export", "name": "Gravity"},
        ],
        "connections": [
            {"from": "toilets", "to": "heat", "input": "opportunity_layer_1_id"},
            {"from": "schools", "to": "heat", "input": "opportunity_layer_2_id"},
            {"from": "heat", "to": "save"},
        ],
    }
    services = _services(
        issues=[
            _issue(
                "setting_invalid",
                "heat",
                "Heatmap Gravity: it does not fit.",
                draft=draft,
                field=field,
            )
        ]
    )
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
    assert (result["blocking"], result["open"]) == ((0, 1) if still_open else (1, 0))


def _potential_draft(*, chosen_second: bool) -> dict[str, Any]:
    """A gravity heatmap whose first opportunity reads its potential from a
    field left out while its layer is open; with ``chosen_second`` a second
    opportunity reads a chosen layer."""
    settings: dict[str, Any] = {
        "routing_mode": "walking",
        "opportunity_1_potential_type": "field",
    }
    steps: list[dict[str, Any]] = [
        {"id": "toilets", "kind": "dataset", "label": "Toilets", "layer": None},
        {"id": "heat", "kind": "tool", "tool": "heatmap_gravity", "settings": settings},
        {"id": "save", "kind": "export", "name": "Gravity"},
    ]
    connections: list[dict[str, Any]] = [
        {"from": "toilets", "to": "heat", "input": "opportunity_layer_1_id"},
        {"from": "heat", "to": "save"},
    ]
    if chosen_second:
        steps.insert(1, {"id": "schools", "kind": "dataset", "layer": 31})
        connections.append(
            {"from": "schools", "to": "heat", "input": "opportunity_layer_2_id"}
        )
        settings["opportunity_2_potential_type"] = "constant"
        settings["opportunity_2_potential_constant"] = 1
    return {"name": "Toilets: gravity", "steps": steps, "connections": connections}


@pytest.mark.parametrize(
    ("chosen_second", "still_open"),
    [(False, True), (True, False)],
    ids=["every-opportunity-open", "one-opportunity-chosen"],
)
async def test_an_unnumbered_opportunity_error_stays_open_while_every_one_is_open(
    chosen_second: bool, still_open: bool
) -> None:
    """Processes reports an opportunity's own validation under
    ``opportunities`` when the error names no setting of it (here a field
    left out while its layer is open, as the skill says). It may stem from
    any connected opportunity: open while every one reads a layer still to be
    chosen, blocking once one of them has its layer."""
    draft = _potential_draft(chosen_second=chosen_second)
    services = _services(
        issues=[
            _issue(
                "setting_invalid",
                "heat",
                "Heatmap Gravity: Opportunities: potential_field must be set when "
                "potential_type is 'field'.",
                draft=draft,
                field="opportunities",
            )
        ]
    )
    result = await execute(CHECK_DRAFT, _env(*services), {"draft": draft})
    assert (result["blocking"], result["open"]) == ((0, 1) if still_open else (1, 0))
    if still_open:
        created = await execute(CREATE, _env(*services), {"draft": draft})
        assert [issue["code"] for issue in created["open_issues"]] == [
            "setting_invalid"
        ]
    else:
        with pytest.raises(ToolFailed, match="Not created: 1 issue"):
            await execute(CREATE, _env(*services), {"draft": draft})


BOTH_TOOLS = pytest.mark.parametrize(
    "tool", [CHECK_DRAFT, CREATE], ids=["check", "create"]
)


@BOTH_TOOLS
@pytest.mark.parametrize("status", [400, 422])
async def test_a_draft_processes_refuses_goes_back_to_the_model(
    tool: Any, status: int
) -> None:
    """Processes' verdict on the draft (here a setting named like a path,
    which only the server sets): the same draft gets the same answer, so the
    model must change it, not try again."""
    refused = httpx.Response(
        status, json={"detail": "source_path is set by the server, not the caller"}
    )
    core, processes, geoapi, catalog = _services(check=refused)
    with pytest.raises(InputInvalid, match="source_path is set by the server"):
        await execute(tool, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert [r.method for r in core.requests] == ["GET"]


@BOTH_TOOLS
@pytest.mark.parametrize("status", [401, 403, 404])
async def test_a_project_processes_will_not_check_for_the_user_says_so(
    tool: Any, status: int
) -> None:
    core, processes, geoapi, catalog = _services(
        check=httpx.Response(status, json={"detail": "Project not found"})
    )
    with pytest.raises(ToolFailed) as caught:
        await execute(tool, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert caught.value.message == NOT_READABLE
    assert [r.method for r in core.requests] == ["GET"]


#: A tool processes describes and runs but keeps out of every toolbox.
LAYER_DELETE: dict[str, Any] = {
    "id": "layer_delete",
    "title": "Layer Delete",
    "inputs": {
        "layer_id": {
            "title": "Layer",
            "schema": {"type": "string", "x-ui": {"widget": "layer-selector"}},
            "minOccurs": 1,
        }
    },
}
DELETE_DRAFT: dict[str, Any] = {
    "name": "Schools removed",
    "steps": [
        {"id": "schools", "kind": "dataset", "layer": 31},
        {"id": "drop", "kind": "tool", "tool": "layer_delete"},
    ],
    "connections": [{"from": "schools", "to": "drop", "input": "layer_id"}],
}
GRAVITY_DRAFT: dict[str, Any] = {
    "name": "Schools: gravity",
    "steps": [
        {"id": "schools", "kind": "dataset", "layer": 31},
        {
            "id": "heat",
            "kind": "tool",
            "tool": "heatmap_gravity",
            "settings": {"routing_mode": "walking"},
        },
        {"id": "save", "kind": "export", "name": "Gravity"},
    ],
    "connections": [
        {"from": "schools", "to": "heat", "input": "opportunity_layer_1_id"},
        {"from": "heat", "to": "save"},
    ],
}
UNKNOWN_DRAFT: dict[str, Any] = {
    **DRAFT,
    "steps": [
        *DRAFT["steps"][:3],
        {"id": "count", "kind": "tool", "tool": "aggregate_polygon_v9"},
        DRAFT["steps"][4],
    ],
}


@BOTH_TOOLS
@pytest.mark.parametrize(
    ("draft", "tool_id", "services"),
    [
        (
            DELETE_DRAFT,
            "layer_delete",
            {
                "descriptions": {"layer_delete": LAYER_DELETE},
                "toolbox": _toolbox(
                    extra=[
                        {
                            "id": "layer_delete",
                            "title": "Layer Delete",
                            "x-ui-toolbox-hidden": True,
                        }
                    ]
                ),
            },
        ),
        (
            GRAVITY_DRAFT,
            "heatmap_gravity",
            {"toolbox": _toolbox(without=frozenset({"heatmap_gravity"}))},
        ),
        (
            UNKNOWN_DRAFT,
            "aggregate_polygon_v9",
            {
                "descriptions": {
                    "aggregate_polygon_v9": httpx.Response(404, json={"detail": "none"})
                }
            },
        ),
    ],
    ids=["toolbox-hidden", "beta-outside-the-beta", "unknown"],
)
async def test_a_tool_outside_the_users_toolbox_is_refused(
    tool: Any, draft: dict[str, Any], tool_id: str, services: dict[str, Any]
) -> None:
    """Processes describes, checks and runs tools the user's toolbox leaves
    out (hidden ones, beta tools for a user outside the beta); a draft takes
    only the tools of ``GET /processes`` for this user, as workflow_tools
    lists them, and an id processes does not know at all goes back the same
    way."""
    core, processes, geoapi, catalog = _services(**services)
    with pytest.raises(InputInvalid) as caught:
        await execute(tool, _env(core, processes, geoapi, catalog), {"draft": draft})
    assert repr(tool_id) in caught.value.message
    assert "workflow_tools" in caught.value.message
    assert not _checked(processes)
    assert [r.method for r in core.requests] == ["GET"]


@pytest.mark.parametrize(
    "unavailable",
    [
        httpx.Response(503, json={"detail": "busy"}),
        httpx.Response(200, json={"links": []}),
    ],
    ids=["failing", "without-a-list"],
)
async def test_a_draft_is_unchecked_while_the_toolbox_cannot_be_read(
    unavailable: httpx.Response,
) -> None:
    """Which tools the user may use comes from the toolbox listing; without
    it nothing is checked or created. An answer without a list of tools is
    no listing: it would refuse every tool as outside the toolbox."""
    core, processes, geoapi, catalog = _services(toolbox=unavailable)
    result = await execute(
        CHECK_DRAFT, _env(core, processes, geoapi, catalog), {"draft": DRAFT}
    )
    assert (result["checked"], result["note"]) == (False, NOT_CHECKED)
    assert not _checked(processes)
    core, processes, geoapi, catalog = _services(toolbox=unavailable)
    with pytest.raises(ToolFailed) as caught:
        await execute(CREATE, _env(core, processes, geoapi, catalog), {"draft": DRAFT})
    assert caught.value.message == CHECK_UNAVAILABLE
    assert not _checked(processes)
    assert [r.method for r in core.requests] == ["GET"]


async def test_the_audit_row_keeps_the_workflow_created(
    repo: Repository, db: Database
) -> None:
    user = UUID(int=1)
    conversation = await repo.create_conversation(user, "project.workflows", None, None)
    run_id, _ = await repo.begin_run(
        UUID(str(conversation["id"])),
        user,
        [{"type": "user_text", "text": "build it"}],
        "test",
        "test",
        3,
    )
    core, processes, geoapi, catalog = _services()
    env = tool_env(
        fake_clients(core=core, processes=processes, geoapi=geoapi, catalog=catalog),
        page=PAGE,
        user_id=user,
        repo=repo,
        run_id=run_id,
    )
    result = await execute(CREATE, env, {"draft": DRAFT}, tool_call_id="c1")
    created = {"kind": "workflow", "ids": [WORKFLOW_ID], "project_id": PROJECT}
    assert WorkflowCreated.model_validate(result).created() == created
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            f"SELECT tool, status, created FROM {db.t('tool_call')}"
        )
    assert [dict(row) for row in rows] == [
        {"tool": "workflow_create", "status": "ok", "created": created}
    ]
