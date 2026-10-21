"""The workflow suite of the evals (spec §10): its fixture projects and check,
the two-turn card tasks, and the new checks. Scripted models stand in for a
provider, so no token is spent."""

import asyncio
import json
import subprocess
import sys
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic_ai.messages import ModelMessage, ModelResponse
from pydantic_ai.models.function import (
    AgentInfo,
    DeltaThinkingCalls,
    DeltaThinkingPart,
    DeltaToolCall,
    DeltaToolCalls,
    FunctionModel,
)

from assistant.asks import AskUserInput
from assistant.config import AssistantSettings
from assistant.tools.catalog import NO_SUCH_WORD, NOTHING_FOUND
from assistant.tools.testing import ScriptedModel, TurnModel
from assistant.tools.toolset import FRUITLESS_SEARCHES, SEARCHED_ENOUGH
from assistant.tools.workflow_tools import clear_description_cache
from assistant.workflows.draft import Draft, ProjectLayer, to_config
from evals.backends import (
    CATALOG_LAYERS,
    EMPTY_PROJECT_ID,
    TEMPLATE_ID,
    WF_PROJECT_ID,
    WORKFLOW_LAYERS,
    Backends,
    fixture_check,
    write_eval_catalog,
)
from evals.graders import grade
from evals.harness import ToolCall, Transcript, auto_answer, run_task
from evals.tasks import EvalTask, load_tasks

DRAFTS = json.loads(
    (Path(__file__).parent / "fixtures" / "workflow_drafts.json").read_text(
        encoding="utf-8"
    )
)
MUNICH_CARD: dict[str, Any] = {
    "questions": [
        {
            "question": "Which supermarkets should count as everyday needs?",
            "header": "Shops",
            "options": [
                {
                    "label": "Supermärkte Bayern",
                    "description": "Adds it to the project",
                    "recommended": True,
                    "value": "eval-supermaerkte-bayern",
                },
                {"label": "Leave it open", "description": "Choose it later"},
            ],
        },
        {
            "question": "Which schools should count as everyday needs?",
            "header": "Schools",
            "options": [
                {
                    "label": "Schulen Bayern",
                    "description": "Adds it to the project",
                    "value": "eval-schulen-bayern",
                },
                {"label": "Leave it open", "description": "Choose it later"},
            ],
        },
    ]
}


def _munich_draft(shops: int, schools: int) -> dict[str, Any]:
    return {
        "name": "Everyday needs within 15 minutes in Munich",
        "steps": [
            {
                "id": "shops",
                "kind": "dataset",
                "label": "Supermarkets",
                "layer": shops,
                "filter": {"area": "DE212"},
            },
            {
                "id": "schools",
                "kind": "dataset",
                "label": "Schools",
                "layer": schools,
                "filter": {"area": "DE212"},
            },
            {
                "id": "heat",
                "kind": "tool",
                "tool": "heatmap_closest_average",
                "settings": {
                    "routing_mode": "walking",
                    "opportunity_1_max_cost": 15,
                    "opportunity_2_max_cost": 15,
                },
            },
            {
                "id": "save",
                "kind": "export",
                "name": "Everyday needs within 15 minutes",
            },
        ],
        "connections": [
            {"from": "shops", "to": "heat", "input": "opportunity_layer_1_id"},
            {"from": "schools", "to": "heat", "input": "opportunity_layer_2_id"},
            {"from": "heat", "to": "save"},
        ],
    }


SHOPS_DRAFT: dict[str, Any] = {
    "name": "Residents within 15 minutes of the supermarkets",
    "steps": [
        {"id": "shops", "kind": "dataset", "layer": 34},
        {"id": "people", "kind": "dataset", "layer": 33},
        {
            "id": "walk",
            "kind": "tool",
            "tool": "catchment_area_v2",
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
        {"from": "shops", "to": "walk", "input": "starting_points"},
        {"from": "walk", "to": "count", "input": "area_layer_id"},
        {"from": "people", "to": "count", "input": "source_layer_id"},
        {"from": "count", "to": "save"},
    ],
}


@pytest.fixture(scope="session")
def backends(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Backends]:
    path = tmp_path_factory.mktemp("eval-catalog-wf")
    write_eval_catalog(path)
    backends = Backends(path)
    yield backends
    backends.close()


@pytest.fixture(autouse=True)
def _fresh_cache() -> Iterator[None]:
    clear_description_cache()
    yield
    clear_description_cache()


def _task(task_id: str) -> EvalTask:
    return next(task for task in load_tasks("workflow") if task.id == task_id)


def _codes(issues: list[dict[str, Any]]) -> list[str]:
    return [issue["code"] for issue in issues if issue["level"] != "warning"]


def test_the_suite_has_nine_tasks_on_the_two_workflow_pages() -> None:
    tasks = load_tasks("workflow")
    assert [task.id for task in tasks] == [f"wf-{n:02d}" for n in range(1, 10)]
    assert {task.context["surface"] for task in tasks} == {
        "project.map",
        "project.workflows",
    }
    assert [task.id for task in tasks if task.critical] == ["wf-06"]
    assert sum(task.answer_card for task in tasks) == 3


def test_the_fixture_check_passes_the_shared_drafts_except_open_steps() -> None:
    first, second, third = DRAFTS["cases"]
    assert _codes(fixture_check(first["config"])) == []
    assert _codes(fixture_check(second["config"])) == ["layer_not_chosen"]
    assert _codes(fixture_check(third["config"])) == []


def test_the_fixture_check_finds_what_stops_a_run() -> None:
    config = json.loads(json.dumps(DRAFTS["cases"][0]["config"]))
    walk = config["nodes"][2]
    walk["data"]["config"].pop("routing_mode")
    config["edges"] = [
        edge for edge in config["edges"] if edge["targetHandle"] != "starting_points"
    ]
    config["nodes"][3]["data"]["processId"] = "no_such_tool"
    config["nodes"][4]["data"]["datasetName"] = " "
    assert sorted(_codes(fixture_check(config))) == [
        "export_name_missing",
        "input_not_connected",
        "setting_required",
        "tool_removed",
    ]
    assert [issue["code"] for issue in fixture_check({"nodes": "x", "edges": []})] == [
        "nodes_not_list"
    ]


def test_the_eval_user_answers_every_question_with_its_first_option() -> None:
    card = AskUserInput.model_validate(MUNICH_CARD)
    answer, text = auto_answer("ask-call-0-1", card)
    assert [(reply.question, reply.options) for reply in answer.answers] == [
        (0, [0]),
        (1, [0]),
    ]
    assert text == "Shops: Supermärkte Bayern. Schools: Schulen Bayern"


async def test_a_draft_that_passes_the_check_is_created_and_graded(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(
        calls=[
            ("workflow_check_draft", {"draft": SHOPS_DRAFT}),
            ("workflow_create", {"draft": SHOPS_DRAFT}),
        ],
        answer="I created the workflow; start it with Run in Workflows mode.",
    )
    transcript = await run_task(_task("wf-01"), model.model, backends, settings)
    assert transcript.error is None, transcript.error
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert [g.passed for g in await grade(_task("wf-01"), transcript, backends)] == [
        True,
        True,
        True,
    ]


async def test_a_viewer_is_refused_once(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(
        calls=[("workflow_create", {"draft": SHOPS_DRAFT})],
        answer="You can view this project but not create workflows in it.",
    )
    transcript = await run_task(_task("wf-06"), model.model, backends, settings)
    [create] = transcript.tool_calls
    assert create.failed
    assert [g.passed for g in await grade(_task("wf-06"), transcript, backends)] == [
        True,
        True,
    ]


async def test_the_munich_task_runs_two_turns_through_the_card(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = TurnModel(
        [
            (
                [
                    ("catalog_find_region", {"name": "München"}),
                    ("catalog_search", {"q": "Supermärkte", "nuts": ["DE212"]}),
                    ("ask_user", MUNICH_CARD),
                ],
                "Which datasets should I use?",
            ),
            (
                [
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "eval-supermaerkte-bayern"},
                    ),
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "eval-schulen-bayern"},
                    ),
                    ("workflow_check_draft", {"draft": _munich_draft(41, 42)}),
                    ("workflow_create", {"draft": _munich_draft(41, 42)}),
                ],
                "I created the workflow. Start it with Run in Workflows mode.",
            ),
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    assert transcript.error is None, transcript.error
    failed = [call for call in transcript.tool_calls if call.failed]
    assert failed == [], failed
    assert any(EMPTY_PROJECT_ID in str(r.url) for r in transcript.requests["core"])
    assert [g.passed for g in await grade(_task("wf-09"), transcript, backends)] == [
        True,
        True,
        True,
    ]
    # The second turn read the answer with its values.
    second = model.requests[-1]
    assert "Shops: Supermärkte Bayern (value eval-supermaerkte-bayern)" in json.dumps(
        [getattr(m, "parts", []) for m in second], default=str, ensure_ascii=False
    )


async def test_a_card_task_without_a_card_runs_one_turn(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(answer="I would need the data first.")
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    assert len(model.requests) == 1
    assert [g.passed for g in await grade(_task("wf-09"), transcript, backends)] == [
        False,
        False,
        False,
    ]


def _transcript(
    calls: list[ToolCall],
    core: list[httpx.Request] | None = None,
    saved: list[dict[str, Any]] | None = None,
) -> Transcript:
    return Transcript(
        task_id="wf-99",
        answer="",
        tool_calls=calls,
        proposals=[],
        requests={"core": core or []},
        error=None,
        input_tokens=0,
        output_tokens=0,
        seconds=0.0,
        first_text_seconds=None,
        saved=saved or [],
    )


def _check_task(*checks: str) -> EvalTask:
    return EvalTask.model_validate_json(
        '{"id": "wf-99", "suite": "workflow", "context": {"surface": "project.workflows", '
        '"project_id": "00000000-0000-0000-0000-0000000005e4"}, "prompt": "x y z", "checks": ['
        + ", ".join(checks)
        + "]}"
    )


async def test_the_asked_check_reads_the_cards_values(backends: Backends) -> None:
    task = _check_task(
        '{"kind": "asked", "questions_min": 2, "offers": ["eval-schulen-bayern"]}'
    )
    asked = _transcript(
        [ToolCall("ask_user", MUNICH_CARD, {"card_id": "ask-1"}, False)]
    )
    assert [g.passed for g in await grade(task, asked, backends)] == [True]
    one = {"questions": MUNICH_CARD["questions"][:1]}
    assert [
        g.passed
        for g in await grade(
            task, _transcript([ToolCall("ask_user", one, {}, False)]), backends
        )
    ] == [False]
    assert [g.passed for g in await grade(task, _transcript([]), backends)] == [False]


async def test_the_workflow_created_check_reads_what_was_saved(
    backends: Backends,
) -> None:
    config = DRAFTS["cases"][0]["config"]
    posted = httpx.Request(
        "POST",
        "http://core/api/v2/project/00000000-0000-0000-0000-0000000005e4/workflow",
        json={"name": "W", "config": config},
    )
    # What core saved: the graders read it, not the requests sent.
    saved = [{"id": "w1", "name": "W", "project_id": "p", "config": config}]
    created = {
        "workflow": {"id": "w1", "name": "W", "project_id": "p"},
        "open_issues": [],
        "groups": [],
    }
    call = ToolCall("workflow_create", {}, created, False)
    task = _check_task(
        '{"kind": "workflow_created", "via": "draft", "tools": ["catchment_area_v2"], "area_layers": [31]}'
    )
    assert [
        g.passed
        for g in await grade(task, _transcript([call], [posted], saved), backends)
    ] == [True]
    # A config core did not save (a refused POST) counts for nothing.
    assert [
        g.passed for g in await grade(task, _transcript([call], [posted]), backends)
    ] == [False]
    without_area = _check_task('{"kind": "workflow_created", "area_layers": [33]}')
    assert [
        g.passed
        for g in await grade(
            without_area, _transcript([call], [posted], saved), backends
        )
    ] == [False]
    left = {
        **created,
        "open_issues": [{"step": "S", "code": "setting_required", "message": "m"}],
    }
    assert [
        g.passed
        for g in await grade(
            task,
            _transcript(
                [ToolCall("workflow_create", {}, left, False)], [posted], saved
            ),
            backends,
        )
    ] == [False]
    template = _check_task('{"kind": "workflow_created", "via": "template"}')
    assert [
        g.passed
        for g in await grade(template, _transcript([call], [posted], saved), backends)
    ] == [False]


async def test_the_tools_check_counts_calls(backends: Backends) -> None:
    task = _check_task('{"kind": "tools", "at_most": {"workflow_create": 1}}')
    once = [ToolCall("workflow_create", {}, None, True)]
    assert [g.passed for g in await grade(task, _transcript(once), backends)] == [True]
    assert [g.passed for g in await grade(task, _transcript(once * 2), backends)] == [
        False
    ]


# What the delivered tools need from the fixture backends beyond the brief.


def _with_dataset_ids(card: dict[str, Any]) -> dict[str, Any]:
    """The card as a model writes it from catalog_search, whose rows are the
    datasets (``src-<item id>``)."""
    copied: dict[str, Any] = json.loads(json.dumps(card))
    for question in copied["questions"]:
        for option in question["options"]:
            if "value" in option:
                option["value"] = f"src-{option['value']}"
    return copied


async def test_the_munich_task_takes_the_dataset_ids_of_the_search(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = TurnModel(
        [
            (
                [
                    ("catalog_find_region", {"name": "München"}),
                    ("ask_user", _with_dataset_ids(MUNICH_CARD)),
                ],
                "Which datasets should I use?",
            ),
            (
                [
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "src-eval-supermaerkte-bayern"},
                    ),
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "src-eval-schulen-bayern"},
                    ),
                    ("workflow_create", {"draft": _munich_draft(41, 42)}),
                ],
                "I created the workflow.",
            ),
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    assert transcript.error is None, transcript.error
    failed = [call for call in transcript.tool_calls if call.failed]
    assert failed == [], failed
    assert [g.passed for g in await grade(_task("wf-09"), transcript, backends)] == [
        True,
        True,
        True,
    ]


class _RepeatedIds(TurnModel):
    """Numbers its tool calls per answer, as some providers do, so the second
    turn repeats the tool call ids of the first."""

    def _place(
        self, messages: list[ModelMessage], info: AgentInfo
    ) -> tuple[list[tuple[str, dict[str, Any]]], str, int, int]:
        calls, answer, _, step = super()._place(messages, info)
        return calls, answer, 0, step


async def test_a_second_turn_repeating_tool_call_ids_keeps_the_first_turns_calls(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = _RepeatedIds(
        [
            ([("ask_user", MUNICH_CARD)], "Which datasets should I use?"),
            (
                [
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "eval-supermaerkte-bayern"},
                    ),
                    ("catalog_find_region", {"name": "München"}),
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "eval-schulen-bayern"},
                    ),
                    ("workflow_create", {"draft": _munich_draft(41, 42)}),
                ],
                "I created the workflow.",
            ),
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    assert [call.name for call in transcript.tool_calls] == [
        "ask_user",
        "project_add_catalog_layer",
        "catalog_find_region",
        "project_add_catalog_layer",
        "workflow_create",
    ]
    assert [g.passed for g in await grade(_task("wf-09"), transcript, backends)] == [
        True,
        True,
        True,
    ]


async def test_the_template_task_can_pass(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(
        calls=[
            ("workflow_find_templates", {"query": "schools walking"}),
            (
                "workflow_create_from_template",
                {
                    "template_id": TEMPLATE_ID,
                    "bindings": {"node:dataset-schools": 31},
                },
            ),
        ],
        answer="I created the workflow from the template.",
    )
    transcript = await run_task(_task("wf-07"), model.model, backends, settings)
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert transcript.tool_calls[-1].result["open_issues"] == []
    assert [g.passed for g in await grade(_task("wf-07"), transcript, backends)] == [
        True,
        True,
    ]


async def test_a_tool_outside_the_toolbox_goes_back_to_the_model(
    backends: Backends, settings: AssistantSettings
) -> None:
    """The fixture's toolbox is what workflow_tools lists; a draft naming
    any other tool is refused before it reaches the check."""
    draft = json.loads(json.dumps(SHOPS_DRAFT))
    draft["steps"][3] = {"id": "count", "kind": "tool", "tool": "no_such_tool"}
    model = ScriptedModel(calls=[("workflow_check_draft", {"draft": draft})])
    transcript = await run_task(_task("wf-01"), model.model, backends, settings)
    [checked] = transcript.tool_calls
    assert checked.failed, checked.result
    assert "'no_such_tool'" in str(checked.result), checked.result
    assert "/processes" in [r.url.path for r in transcript.requests["processes"]]
    assert "/workflows/check" not in [
        r.url.path for r in transcript.requests["processes"]
    ]


async def test_a_catalog_layers_fields_are_the_columns_its_record_lists(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(
        calls=[
            ("catalog_get_record", {"item_id": f"src-{catalog_id}"})
            for catalog_id in CATALOG_LAYERS
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    for call, layer in zip(transcript.tool_calls, CATALOG_LAYERS.values(), strict=True):
        assert not call.failed, call.result
        [member] = call.result["goat:items"]
        assert [column["name"] for column in member["columns"]] == list(layer.fields)


# The eval grades what production does: the stand-in check judges a draft as
# processes' check does, and the graders read what core saved.


def _config(draft: dict[str, Any]) -> dict[str, Any]:
    """The draft converted with the workflow project's layers, as the tools
    send it to the check."""
    layers = {
        layer.layer_project_id: ProjectLayer(
            layer.layer_project_id,
            layer.layer_id,
            layer.name,
            "feature",
            layer.geometry,
        )
        for layer in WORKFLOW_LAYERS
    }
    converted = to_config(
        Draft.model_validate(draft), layers=layers, regions={}, titles={}
    )
    return converted.config


def _found(issues: list[dict[str, Any]]) -> list[tuple[str, str | None]]:
    return [
        (issue["code"], issue["field"])
        for issue in issues
        if issue["level"] != "warning"
    ]


def _changed(draft: dict[str, Any], step: str, **settings: Any) -> dict[str, Any]:
    """The draft with settings of one tool step changed."""
    copied: dict[str, Any] = json.loads(json.dumps(draft))
    for item in copied["steps"]:
        if item["id"] == step:
            item["settings"] = {**item["settings"], **settings}
    return copied


def _join_draft(settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "Schools with their district",
        "steps": [
            {"id": "schools", "kind": "dataset", "layer": 31},
            {"id": "districts", "kind": "dataset", "layer": 35},
            {"id": "join", "kind": "tool", "tool": "join", "settings": settings},
            {"id": "save", "kind": "export", "name": "Schools with their district"},
        ],
        "connections": [
            {"from": "schools", "to": "join", "input": "target_layer_id"},
            {"from": "districts", "to": "join", "input": "join_layer_id"},
            {"from": "join", "to": "save"},
        ],
    }


JOIN_SETTINGS: dict[str, Any] = {
    "use_attribute_relationship": False,
    "use_spatial_relationship": True,
    "spatial_relationship": "intersects",
    "join_operation": "one_to_one",
    "add_join_fields": True,
    "join_fields": ["name"],
}
LOOP_DRAFT: dict[str, Any] = {
    "name": "Rings",
    "steps": [
        {"id": "shops", "kind": "dataset", "layer": 34},
        {"id": "a", "kind": "tool", "tool": "buffer", "settings": {"distances": [500]}},
        {"id": "b", "kind": "tool", "tool": "buffer", "settings": {"distances": [100]}},
        {"id": "save", "kind": "export", "name": "Rings"},
    ],
    "connections": [
        {"from": "a", "to": "b", "input": "input_layer_id"},
        {"from": "b", "to": "a", "input": "input_layer_id"},
        {"from": "b", "to": "save"},
    ],
}


def _heat_draft(**settings: Any) -> dict[str, Any]:
    """The Munich heatmap on the project's own layers, without an area."""
    draft = _munich_draft(34, 31)
    for step in draft["steps"]:
        step.pop("filter", None)
        if step["id"] == "heat":
            step["settings"].update(settings)
    return draft


def test_the_fixture_check_validates_settings_as_processes_does() -> None:
    foot = _changed(SHOPS_DRAFT, "walk", routing_mode="foot")
    assert _found(fixture_check(_config(foot))) == [("setting_invalid", "routing_mode")]
    no_field = _changed(SHOPS_DRAFT, "count", column_statistics=[{"operation": "sum"}])
    assert _found(fixture_check(_config(no_field))) == [
        ("setting_invalid", "column_statistics")
    ]
    [empty] = fixture_check(_config(_join_draft({})))
    assert (empty["code"], empty["field"]) == ("setting_invalid", None)
    assert empty["message"].endswith(
        "At least one attribute relationship is required when "
        "use_attribute_relationship is enabled"
    )
    assert fixture_check(_config(_join_draft(JOIN_SETTINGS))) == []
    assert fixture_check(_config(_heat_draft())) == []
    assert _found(
        fixture_check(_config(_heat_draft(opportunity_1_max_cost="fifteen")))
    ) == [("setting_invalid", "opportunity_1_max_cost")]


def test_the_fixture_check_reads_a_field_from_the_dataset_its_setting_reads() -> None:
    def found(draft: dict[str, Any]) -> list[tuple[str, str | None]]:
        return _found(fixture_check(_config(draft)))

    assert found(SHOPS_DRAFT) == []
    assert found(_changed(SHOPS_DRAFT, "count", group_by_field=["population"])) == [
        ("field_not_in_layer", "group_by_field")
    ]
    # A statistic's field reads source_layer_id (its own widget options say so).
    guessed = [{"operation": "sum", "field": "population"}]
    assert found(_changed(SHOPS_DRAFT, "count", column_statistics=guessed)) == [
        ("field_not_in_layer", "column_statistics")
    ]
    assert found(_join_draft({**JOIN_SETTINGS, "join_fields": ["bezirk_name"]})) == [
        ("field_not_in_layer", "join_fields")
    ]
    # Fed by a tool step: processes predicts that step's columns and only warns.
    fed = _changed(SHOPS_DRAFT, "count", group_by_field=["population"])
    fed["connections"] = [
        {"from": "shops", "to": "walk", "input": "starting_points"},
        {"from": "walk", "to": "count", "input": "source_layer_id"},
        {"from": "people", "to": "count", "input": "area_layer_id"},
        {"from": "count", "to": "save"},
    ]
    assert found(fed) == []
    # A step left open has no fields yet.
    opened = _changed(SHOPS_DRAFT, "count", group_by_field=["population"])
    opened["steps"][1] = {
        "id": "people",
        "kind": "dataset",
        "label": "Residents",
        "layer": None,
    }
    assert found(opened) == [("layer_not_chosen", None)]


def test_the_fixture_check_finds_loops_and_connections_to_no_input() -> None:
    assert _found(fixture_check(_config(LOOP_DRAFT))) == [("loop", None)]
    into: dict[str, Any] = {
        "name": "Walk",
        "steps": [
            {"id": "shops", "kind": "dataset", "layer": 34},
            {
                "id": "walk",
                "kind": "tool",
                "tool": "catchment_area_v2",
                "settings": {"routing_mode": "walking", "max_cost": 15},
            },
            {"id": "save", "kind": "export", "name": "Walk"},
        ],
        "connections": [
            {"from": "shops", "to": "walk", "input": "routing_mode"},
            {"from": "walk", "to": "save"},
        ],
    }
    assert _found(fixture_check(_config(into))) == [
        ("connection_to_unknown_input", "routing_mode"),
        ("input_not_connected", "starting_points"),
        ("setting_invalid", "routing_mode"),
    ]
    # The editor's handle for a tool whose inputs it does not know yet.
    into["connections"][0]["input"] = "input"
    assert _found(fixture_check(_config(into))) == [
        ("input_not_connected", "starting_points")
    ]
    gone = _config(SHOPS_DRAFT)
    gone["edges"].append(
        {"id": "e", "source": gone["nodes"][0]["id"], "target": "tool-gone"}
    )
    assert ("connection_to_removed_step", None) in _found(fixture_check(gone))


@pytest.mark.parametrize(
    ("task_id", "draft", "reason"),
    [
        (
            "wf-01",
            _changed(SHOPS_DRAFT, "walk", routing_mode="foot"),
            "Input should be",
        ),
        (
            "wf-01",
            _changed(
                SHOPS_DRAFT,
                "count",
                column_statistics=[{"operation": "sum", "field": "population"}],
            ),
            "population",
        ),
        ("wf-03", _join_draft({}), "attribute relationship"),
        ("wf-01", LOOP_DRAFT, "loop"),
    ],
    ids=["foot", "population", "empty-join", "loop"],
)
async def test_a_draft_production_refuses_is_not_created(
    task_id: str,
    draft: dict[str, Any],
    reason: str,
    backends: Backends,
    settings: AssistantSettings,
) -> None:
    model = ScriptedModel(calls=[("workflow_create", {"draft": draft})])
    transcript = await run_task(_task(task_id), model.model, backends, settings)
    [create] = transcript.tool_calls
    assert create.failed and reason in str(create.result), create.result
    grades = await grade(_task(task_id), transcript, backends)
    assert [g.passed for g in grades if g.check == "workflow_created"] == [False]


async def test_a_refused_add_and_open_steps_do_not_pass_the_munich_task(
    backends: Backends, settings: AssistantSettings
) -> None:
    draft = _munich_draft(41, 42)
    for step in draft["steps"][:2]:
        step["layer"] = None
        step.pop("filter")
    model = ScriptedModel(
        calls=[
            ("catalog_find_region", {"name": "München"}),
            # No card was answered: the add is refused.
            ("project_add_catalog_layer", {"catalog_id": "eval-supermaerkte-bayern"}),
            ("workflow_create", {"draft": draft}),
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    assert [call.failed for call in transcript.tool_calls] == [False, True, False]
    assert [g.passed for g in await grade(_task("wf-09"), transcript, backends)] == [
        False,
        False,
        False,
    ]


async def test_a_workflow_that_leaves_the_named_layers_open_does_not_pass(
    backends: Backends, settings: AssistantSettings
) -> None:
    draft = json.loads(json.dumps(SHOPS_DRAFT))
    draft["steps"][0] = {
        "id": "shops",
        "kind": "dataset",
        "label": "Supermarkets",
        "layer": None,
    }
    draft["steps"][1] = {
        "id": "people",
        "kind": "dataset",
        "label": "Residents",
        "layer": None,
    }
    draft["steps"][3]["settings"]["column_statistics"] = [{"operation": "count"}]
    model = ScriptedModel(
        calls=[
            ("workflow_check_draft", {"draft": draft}),
            ("workflow_create", {"draft": draft}),
        ],
        answer="I created the workflow; choose the layers in the editor.",
    )
    transcript = await run_task(_task("wf-01"), model.model, backends, settings)
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert [g.passed for g in await grade(_task("wf-01"), transcript, backends)] == [
        False,
        True,
        True,
    ]


async def test_a_template_with_its_input_left_open_does_not_pass(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(
        calls=[
            ("workflow_find_templates", {"query": "schools walking"}),
            ("workflow_create_from_template", {"template_id": TEMPLATE_ID}),
        ],
        answer="I created the workflow from the template.",
    )
    transcript = await run_task(_task("wf-07"), model.model, backends, settings)
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert [g.passed for g in await grade(_task("wf-07"), transcript, backends)] == [
        True,
        False,
    ]


async def test_the_fixture_finds_templates_as_core_does(backends: Backends) -> None:
    services = backends.clients()[0]
    try:

        async def found(search: str, kind: str = "workflow") -> list[str]:
            response = await services.core.get(
                "/api/v2/template", params={"kind": kind, "search": search}
            )
            return [row["id"] for row in response.json()["items"]]

        assert await found("walking distance") == [TEMPLATE_ID]
        assert await found("SCHULEN") == [TEMPLATE_ID]  # in the description
        assert await found("schools walking") == []
        assert await found("schools", kind="layout") == []
    finally:
        await services.aclose()


PLAYGROUND_CARD: dict[str, Any] = {
    "questions": [
        {
            "question": "Which playgrounds should count?",
            "header": "Play",
            "options": [
                {
                    "label": "Spielplätze München",
                    "description": "Adds it to the project",
                    "value": "src-eval-spielplaetze-muenchen",
                },
                {"label": "Leave it open", "description": "Choose it later"},
            ],
        }
    ]
}


async def test_a_catalog_dataset_found_in_munich_can_be_added(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = TurnModel(
        [
            (
                [
                    ("catalog_search", {"q": "Spielplätze", "nuts": ["DE212"]}),
                    ("ask_user", PLAYGROUND_CARD),
                ],
                "Which playgrounds should count?",
            ),
            (
                [
                    (
                        "project_add_catalog_layer",
                        {"catalog_id": "src-eval-spielplaetze-muenchen"},
                    ),
                    ("project_get_fields", {"layer_project_id": 43}),
                    (
                        "catalog_get_record",
                        {"item_id": "src-eval-spielplaetze-muenchen"},
                    ),
                ],
                "Added.",
            ),
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    search, _, added, fields, record = transcript.tool_calls
    assert "src-eval-spielplaetze-muenchen" in [
        row["id"] for row in search.result["results"]
    ]
    assert not added.failed, added.result
    assert [layer["layer_project_id"] for layer in added.result["layers"]] == [43]
    assert not fields.failed, fields.result
    [member] = record.result["goat:items"]
    columns = [column["name"] for column in member["columns"]]
    assert [field["name"] for field in fields.result["fields"]] == [
        name for name in columns if name not in ("geometry", "bbox")
    ]


def test_only_one_workflow_layer_holds_residents() -> None:
    assert [layer.name for layer in WORKFLOW_LAYERS if "einwohner" in layer.fields] == [
        "Einwohner Raster"
    ]


class _Slow(TurnModel):
    """Takes its time before each response."""

    async def _stream(
        self, messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str | DeltaToolCalls]:
        await asyncio.sleep(0.6)
        async for item in super()._stream(messages, info):
            yield item


async def test_each_turn_has_its_own_time_limit(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = _Slow(
        [
            ([("ask_user", MUNICH_CARD)], "Which datasets should I use?"),
            ([("catalog_find_region", {"name": "München"})], "Thanks."),
        ]
    )
    # Each turn takes about 1.2 s; both together take longer than the limit.
    limited = settings.model_copy(update={"run_max_seconds": 2})
    transcript = await run_task(_task("wf-09"), model.model, backends, limited)
    assert transcript.error is None, transcript.error
    assert len(model.requests) == 4


async def test_a_write_repeated_after_the_card_is_not_made_twice(
    backends: Backends, settings: AssistantSettings
) -> None:
    join = _join_draft(JOIN_SETTINGS)
    card = {
        "questions": [
            {
                "question": "Should the districts come from Stadtbezirke?",
                "header": "Districts",
                "options": [
                    {
                        "label": "Stadtbezirke",
                        "description": "The layer",
                        "value": "35",
                    },
                    {"label": "Leave it open", "description": "Choose it later"},
                ],
            }
        ]
    }
    model = TurnModel(
        [
            (
                [("workflow_create", {"draft": join}), ("ask_user", card)],
                "Is this the layer you meant?",
            ),
            ([("workflow_create", {"draft": join})], "The workflow is created."),
        ]
    )
    transcript = await run_task(_task("wf-03"), model.model, backends, settings)
    first, _, again = transcript.tool_calls
    assert not first.failed and not again.failed, transcript.tool_calls
    assert "repeated_call" in again.result
    posted = [
        r
        for r in transcript.requests["core"]
        if r.method == "POST" and r.url.path.endswith("/workflow")
    ]
    assert len(posted) == 1


class _SameIds(ScriptedModel):
    """Gives every tool call the same id, as a provider may."""

    async def _stream(
        self, messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str | DeltaToolCalls]:
        step = self._step(messages, info)
        if step < len(self.calls):
            name, args = self.calls[step]
            yield {
                0: DeltaToolCall(
                    name=name, json_args=json.dumps(args), tool_call_id="call"
                )
            }
            return
        yield self.answer


async def test_tool_call_ids_reused_in_one_turn_keep_every_call(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = _SameIds(
        calls=[
            ("workflow_check_draft", {"draft": SHOPS_DRAFT}),
            ("workflow_create", {"draft": SHOPS_DRAFT}),
        ],
        answer="I created the workflow; start it with Run in Workflows mode.",
    )
    transcript = await run_task(_task("wf-01"), model.model, backends, settings)
    assert [(call.name, call.failed) for call in transcript.tool_calls] == [
        ("workflow_check_draft", False),
        ("workflow_create", False),
    ]
    assert [g.passed for g in await grade(_task("wf-01"), transcript, backends)] == [
        True,
        True,
        True,
    ]


async def test_the_tools_must_be_in_one_saved_workflow(
    backends: Backends, settings: AssistantSettings
) -> None:
    walk_only: dict[str, Any] = {
        "name": "Walk",
        "steps": [
            {"id": "shops", "kind": "dataset", "layer": 34},
            {
                "id": "walk",
                "kind": "tool",
                "tool": "catchment_area_v2",
                "settings": {"routing_mode": "walking", "max_cost": 15},
            },
            {"id": "save", "kind": "export", "name": "Walk"},
        ],
        "connections": [
            {"from": "shops", "to": "walk", "input": "starting_points"},
            {"from": "walk", "to": "save"},
        ],
    }
    count_only: dict[str, Any] = {
        "name": "Count",
        "steps": [
            {"id": "people", "kind": "dataset", "layer": 33},
            {"id": "districts", "kind": "dataset", "layer": 35},
            {
                "id": "count",
                "kind": "tool",
                "tool": "aggregate_polygon",
                "settings": {
                    "area_type": "polygon",
                    "column_statistics": [{"operation": "sum", "field": "einwohner"}],
                },
            },
            {"id": "save", "kind": "export", "name": "Count"},
        ],
        "connections": [
            {"from": "people", "to": "count", "input": "source_layer_id"},
            {"from": "districts", "to": "count", "input": "area_layer_id"},
            {"from": "count", "to": "save"},
        ],
    }
    model = ScriptedModel(
        calls=[
            ("workflow_check_draft", {"draft": walk_only}),
            ("workflow_create", {"draft": walk_only}),
            ("workflow_create", {"draft": count_only}),
        ],
        answer="I created the workflows; start them with Run in Workflows mode.",
    )
    transcript = await run_task(_task("wf-01"), model.model, backends, settings)
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert [g.passed for g in await grade(_task("wf-01"), transcript, backends)] == [
        False,
        True,
        True,
    ]


def test_the_fixture_check_finds_an_undefined_variable() -> None:
    draft = _changed(SHOPS_DRAFT, "walk", max_cost="{{@minutes}}")
    assert _found(fixture_check(_config(draft))) == [("variable_undefined", "max_cost")]
    draft["variables"] = [{"name": "minutes", "type": "number", "defaultValue": 15}]
    assert fixture_check(_config(draft)) == []


# Fix round 2.


async def test_a_template_bound_by_a_layer_id_as_text_passes(
    backends: Backends, settings: AssistantSettings
) -> None:
    model = ScriptedModel(
        calls=[
            ("workflow_find_templates", {"query": "schools walking"}),
            (
                "workflow_create_from_template",
                {
                    "template_id": TEMPLATE_ID,
                    # The tool reads it as 31; core gets the layer's id.
                    "bindings": {"node:dataset-schools": "31"},
                },
            ),
        ],
        answer="I created the workflow from the template.",
    )
    transcript = await run_task(_task("wf-07"), model.model, backends, settings)
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert transcript.saved[-1]["bindings"] == {
        "node:dataset-schools": "e2000000-0000-0000-0000-000000000031"
    }
    assert [g.passed for g in await grade(_task("wf-07"), transcript, backends)] == [
        True,
        True,
    ]


def _gravity_draft(**settings: Any) -> dict[str, Any]:
    return {
        "name": "Supermarkets on foot",
        "steps": [
            {"id": "shops", "kind": "dataset", "layer": 34},
            {
                "id": "heat",
                "kind": "tool",
                "tool": "heatmap_gravity",
                "settings": {
                    "routing_mode": "walking",
                    "opportunity_1_max_cost": 15,
                    **settings,
                },
            },
            {"id": "save", "kind": "export", "name": "Supermarkets on foot"},
        ],
        "connections": [
            {"from": "shops", "to": "heat", "input": "opportunity_layer_1_id"},
            {"from": "heat", "to": "save"},
        ],
    }


def test_an_empty_opportunity_field_is_not_judged() -> None:
    empty = _gravity_draft(opportunity_1_potential_field="")
    assert fixture_check(_config(empty)) == []
    wrong = _gravity_draft(
        opportunity_1_potential_type="field", opportunity_1_potential_field="population"
    )
    assert _found(fixture_check(_config(wrong))) == [
        ("field_not_in_layer", "opportunity_1_potential_field")
    ]


async def test_an_open_opportunitys_left_out_field_is_created_open(
    backends: Backends, settings: AssistantSettings
) -> None:
    """The stand-in reports an opportunity's own validation under
    ``opportunities`` as processes does; while every connected opportunity
    reads a step left open, the create keeps it open."""
    draft = _munich_draft(34, 31)
    draft["steps"][0] = {
        "id": "shops",
        "kind": "dataset",
        "label": "Supermarkets",
        "layer": None,
    }
    draft["steps"][1:2] = []
    draft["connections"] = [
        {"from": "shops", "to": "heat", "input": "opportunity_layer_1_id"},
        {"from": "heat", "to": "save"},
    ]
    draft["steps"][1]["tool"] = "heatmap_gravity"
    draft["steps"][1]["settings"] = {
        "routing_mode": "walking",
        "opportunity_1_potential_type": "field",
    }
    model = ScriptedModel(calls=[("workflow_create", {"draft": draft})])
    transcript = await run_task(_task("wf-02"), model.model, backends, settings)
    [create] = transcript.tool_calls
    assert not create.failed, create.result
    assert sorted(
        (issue["code"], issue["message"].split(": ")[1])
        for issue in create.result["open_issues"]
    ) == [
        ("layer_not_chosen", "no layer is chosen."),
        ("setting_invalid", "Opportunities"),
    ]


def test_the_opportunity_handles_are_goatlibs() -> None:
    from goatlib.tools._opportunity_handles import NUMBERED_OPPORTUNITY_ID_FIELDS

    from evals.backends import OPPORTUNITY_HANDLES

    assert OPPORTUNITY_HANDLES == NUMBERED_OPPORTUNITY_ID_FIELDS


def test_the_fixture_backends_load_without_goatlibs_analysis() -> None:
    code = "import sys, evals.backends; print('goatlib.analysis' in sys.modules)"
    loaded = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )
    assert loaded.stdout.strip() == "False"


# Round 2 of the eval fixes: runs that circled, failed or ended without text.

SCHOOLS_CARD: dict[str, Any] = {
    "questions": [
        {
            "question": "Which schools should the catchments start from?",
            "header": "Schools",
            "options": [
                {"label": "Schulen", "recommended": True, "value": "31"},
                {"label": "Schulen (Stand 2019)", "value": "32"},
            ],
        }
    ]
}


async def test_a_model_that_answers_nothing_after_the_layers_still_asks(
    backends: Backends, settings: AssistantSettings
) -> None:
    """wf-04 failed with "Exceeded maximum output retries (3)" after
    skills_load and project_get_layers: four responses in a row held neither
    text nor a tool call, and Pydantic AI asked again each time with every
    tool offered. After the second, the answer step offers only the card."""
    offered: list[list[str]] = []

    async def stream(
        messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str | DeltaToolCalls | DeltaThinkingCalls]:
        tools = sorted(tool.name for tool in info.function_tools)
        offered.append(tools)
        step = len(offered) - 1
        if step == 0:
            yield {0: DeltaToolCall("skills_load", '{"name": "build-a-workflow"}')}
        elif step == 1:
            yield {0: DeltaToolCall("project_get_layers", "{}")}
        elif tools == ["ask_user"]:
            yield {0: DeltaToolCall("ask_user", json.dumps(SCHOOLS_CARD))}
        elif not tools:
            yield "Pick the school layer in the card."
        else:
            yield {0: DeltaThinkingPart(content="Two school layers: ask which.")}

    task = _task("wf-04")
    model = FunctionModel(stream_function=stream)
    transcript = await run_task(task, model, backends, settings)
    assert transcript.error is None, transcript.error
    assert [call.name for call in transcript.tool_calls] == [
        "skills_load",
        "project_get_layers",
        "ask_user",
    ]
    assert len(offered[2]) > 1 and len(offered[3]) > 1 and offered[4] == ["ask_user"]
    assert transcript.answer == "Pick the school layer in the card."
    assert [g.passed for g in await grade(task, transcript, backends)] == [True, True]


async def test_the_workflow_answer_ends_with_text_after_its_cards(
    backends: Backends, settings: AssistantSettings
) -> None:
    """wf-08: created, shown as a card, and the answer was " ". The text is
    asked for, and the answer the run ends with is graded."""
    shown = {
        "groups": [
            {
                "items": [
                    {"kind": "layer", "id": str(layer), "project_id": WF_PROJECT_ID}
                    for layer in (34, 33)
                ]
            }
        ]
    }
    answer = (
        "Der Workflow ist angelegt: Einzugsgebiete von 15 Minuten zu Fuß um die "
        "Supermärkte und die Einwohner darin. Du startest ihn mit Run."
    )

    async def stream(
        messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str | DeltaToolCalls]:
        step = sum(isinstance(message, ModelResponse) for message in messages)
        calls = [
            ("workflow_check_draft", {"draft": SHOPS_DRAFT}),
            ("workflow_create", {"draft": SHOPS_DRAFT}),
            ("core_show_items", shown),
        ]
        if step < len(calls):
            name, args = calls[step]
            yield {0: DeltaToolCall(name, json.dumps(args), tool_call_id=f"c{step}")}
        elif step == len(calls):
            yield " "
        else:
            yield answer

    task = _task("wf-08")
    transcript = await run_task(
        task, FunctionModel(stream_function=stream), backends, settings
    )
    assert transcript.error is None, transcript.error
    assert not any(call.failed for call in transcript.tool_calls), transcript.tool_calls
    assert transcript.answer == answer
    assert [g.passed for g in await grade(task, transcript, backends)] == [True, True]


TOILETS_DRAFT: dict[str, Any] = {
    "name": "Public toilets: 5 minutes on foot",
    "steps": [
        {"id": "toilets", "kind": "dataset", "label": "Public toilets", "layer": None},
        {
            "id": "walk",
            "kind": "tool",
            "tool": "catchment_area_v2",
            "label": "5 minutes on foot",
            "settings": {
                "routing_mode": "walking",
                "cost_type": "time",
                "max_cost": 5,
                "steps": 1,
            },
        },
        {"id": "save", "kind": "export", "name": "Within 5 minutes of public toilets"},
    ],
    "connections": [
        {"from": "toilets", "to": "walk", "input": "starting_points"},
        {"from": "walk", "to": "save"},
    ],
}


def _searches(transcript: Transcript) -> list[str]:
    return [
        request.url.path
        for request in transcript.requests["catalog"]
        if request.url.path in ("/stac/collections", "/stac/suggest")
    ]


async def test_the_catalog_says_when_it_has_nothing_and_stops_being_searched(
    backends: Backends, settings: AssistantSettings
) -> None:
    """wf-05: the fixture catalog has no public toilets. Each search came
    back with empty facet lists and nothing else, the search tool's own text
    said to try other words, and the model searched until the answer's
    budget was gone, then asked with a card instead of building the draft.
    An empty result says what it means and what comes next; after
    ``FRUITLESS_SEARCHES`` empty ones in a row, the catalog is not searched
    again in that answer."""
    searches = [
        ("catalog_search", {"q": "toilette,toiletten,wc,toilet", "nuts": ["DED51"]}),
        ("catalog_suggest_terms", {"prefix": "toilet"}),
        ("catalog_search", {"q": "toilette,wc"}),
        ("catalog_search", {"q": "sanitär,abort", "nuts": ["DED51"]}),
        ("catalog_suggest_terms", {"prefix": "klo"}),
    ]
    model = ScriptedModel(
        calls=[
            ("catalog_find_region", {"name": "Leipzig"}),
            *searches,
            ("workflow_check_draft", {"draft": TOILETS_DRAFT}),
            ("workflow_create", {"draft": TOILETS_DRAFT}),
        ],
        answer=(
            "The workflow is created. Neither the project nor the catalog has "
            "public toilets, so its first step is open: choose a toilet layer "
            "there, then start it with Run."
        ),
    )
    task = _task("wf-05")
    transcript = await run_task(task, model.model, backends, settings)
    assert transcript.error is None, transcript.error
    found = transcript.tool_calls[1 : 1 + len(searches)]
    first = found[0].result
    assert first["numberMatched"] == 0 and "facets" not in first
    assert first["note"] == NOTHING_FOUND
    assert found[1].result["note"] == NO_SUCH_WORD
    # The fifth did not run.
    assert [call.failed for call in found] == [False] * 4 + [True]
    assert found[-1].result == SEARCHED_ENOUGH
    assert len(_searches(transcript)) == FRUITLESS_SEARCHES
    assert [g.passed for g in await grade(task, transcript, backends)] == [True, True]


async def test_a_search_that_finds_something_starts_the_count_again(
    backends: Backends, settings: AssistantSettings
) -> None:
    """Searching for several datasets of one workflow goes on while the
    searches find some of them."""
    empty = ("catalog_search", {"q": "apotheke,pharmacy", "nuts": ["DE212"]})
    hit = ("catalog_search", {"q": "schule,schulen", "nuts": ["DE212"]})
    model = ScriptedModel(
        calls=[
            *[(empty[0], {**empty[1], "limit": n}) for n in (1, 2, 3)],
            hit,
            *[(empty[0], {**empty[1], "limit": n}) for n in (4, 5, 6)],
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    assert transcript.error is None, transcript.error
    assert not any(call.failed for call in transcript.tool_calls)
    assert transcript.tool_calls[3].result["numberMatched"] >= 1


async def test_a_catalog_record_describes_the_layer_adding_it_gives(
    backends: Backends, settings: AssistantSettings
) -> None:
    """wf-09: the fixture's Bavarian supermarkets came as a line dataset in
    the catalog but as a point layer once added, and a model that read the
    record looked for other supermarkets instead of using them."""
    model = ScriptedModel(
        calls=[
            ("catalog_get_record", {"item_id": f"src-{catalog_id}"})
            for catalog_id in CATALOG_LAYERS
        ]
    )
    transcript = await run_task(_task("wf-09"), model.model, backends, settings)
    for call, layer in zip(transcript.tool_calls, CATALOG_LAYERS.values(), strict=True):
        [member] = call.result["goat:items"]
        assert member["geometry_type"] == layer.geometry, member
