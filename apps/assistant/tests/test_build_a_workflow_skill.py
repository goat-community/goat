"""The built-in skill build-a-workflow (spec §6.2) and the prompt around it
(spec §7): the skill loads and is listed, and every tool, input and setting it
names is one GOAT has."""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from assistant.prompt import (
    ANSWER_OPEN,
    INSTRUCTIONS,
    SKILLS_INDEX,
    static_instructions,
)
from assistant.skills import BUILT_IN
from assistant.tools.registry import BY_WIRE_NAME
from assistant.tools.workflows import CHECK_DRAFT
from assistant.workflows import issues, tool_info
from assistant.workflows.draft import DatasetStep, Draft, ExportStep, ToolStep
from assistant.workflows.tool_info import SettingInfo

FIXTURE = Path(__file__).parent / "fixtures" / "process_descriptions.json"
DESCRIPTIONS: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))[
    "descriptions"
]
SKILL = BUILT_IN["build-a-workflow"]
TEXTS = {"SKILL.md": SKILL.instructions, **SKILL.files}
NUMBERED = re.compile(r"^opportunity_[123]_(?P<name>[a-z_]+)$")
TOOL_NAME = re.compile(r"\b(?:workflow|project|catalog|core|ask|skills)_[a-z_]+\b")


def _drafts() -> list[tuple[str, dict[str, Any]]]:
    return [
        (name, json.loads(block))
        for name, text in TEXTS.items()
        for block in re.findall(r"```json\n(.*?)\n```", text, re.S)
    ]


def test_the_skill_loads_and_is_in_the_instructions() -> None:
    assert set(SKILL.files) == {"recipes.md"}
    assert f"- `build-a-workflow`: {SKILL.description}" in SKILLS_INDEX
    assert static_instructions() == [INSTRUCTIONS, SKILLS_INDEX]


def test_the_skill_names_only_tools_that_exist() -> None:
    named = {name for text in TEXTS.values() for name in TOOL_NAME.findall(text)}
    named -= {"project_id", "catalog_id"}
    assert {"workflow_create", "ask_user", "project_add_catalog_layer"} <= named
    assert named <= set(BY_WIRE_NAME), named - set(BY_WIRE_NAME)


@pytest.mark.parametrize(
    ("source", "draft"), _drafts(), ids=lambda value: str(value)[:40]
)
def test_every_draft_uses_real_tools_inputs_and_settings(
    source: str, draft: dict[str, Any]
) -> None:
    model = Draft.model_validate(draft)
    tools = {step.id: step for step in model.steps if isinstance(step, ToolStep)}
    for step in tools.values():
        description = DESCRIPTIONS[step.tool]
        settings = {
            setting.name: setting for setting in tool_info.settings(description)
        }
        per_opportunity = {
            setting.name
            for setting in tool_info.opportunity_settings(description) or []
        }
        for key, value in step.settings.items():
            numbered = NUMBERED.match(key)
            if numbered:
                assert numbered["name"] in per_opportunity, (source, step.tool, key)
                continue
            assert key in settings, (source, step.tool, key)
            items = settings[key].items
            if items is not None:
                names = {item.name for item in items}
                assert all(set(entry) <= names for entry in value), (source, key)
    for connection in model.connections:
        if connection.target in tools:
            described = DESCRIPTIONS[tools[connection.target].tool]
            inputs = {item.name for item in tool_info.layer_inputs(described)}
            assert connection.input in inputs, (source, connection)


def _not_offered(setting: SettingInfo, value: Any) -> list[Any]:
    """The parts of ``value`` that are not among the choices ``setting``, or
    one of its list's items, offers."""
    if setting.items is not None:
        items = {item.name: item for item in setting.items}
        return [
            wrong
            for entry in value
            for key, part in entry.items()
            if key in items
            for wrong in _not_offered(items[key], part)
        ]
    if setting.choices is None:
        return []
    return [
        part
        for part in (value if isinstance(value, list) else [value])
        if part not in setting.choices
    ]


@pytest.mark.parametrize(
    ("source", "draft"), _drafts(), ids=lambda value: str(value)[:40]
)
def test_every_choice_in_the_drafts_is_one_the_setting_offers(
    source: str, draft: dict[str, Any]
) -> None:
    model = Draft.model_validate(draft)
    for step in model.steps:
        if not isinstance(step, ToolStep):
            continue
        description = DESCRIPTIONS[step.tool]
        settings = {s.name: s for s in tool_info.settings(description)}
        per_opportunity = {
            s.name: s for s in tool_info.opportunity_settings(description) or []
        }
        for key, value in step.settings.items():
            numbered = NUMBERED.match(key)
            setting = (
                per_opportunity.get(numbered["name"]) if numbered else settings.get(key)
            )
            assert setting is not None, (source, step.tool, key)
            assert not _not_offered(setting, value), (source, step.tool, key, value)


def test_the_recipes_cover_the_spec() -> None:
    used = {
        step["tool"]
        for _, draft in _drafts()
        for step in draft["steps"]
        if step["kind"] == "tool"
    }
    assert {
        "catchment_area_v2",
        "aggregate_polygon",
        "aggregate_points",
        "heatmap_closest_average",
        "join",
        "buffer",
    } <= used


def test_only_a_one_step_issue_is_said_to_start_with_the_steps_name() -> None:
    """An issue of the whole workflow or of several steps keeps processes'
    message as it is, so no text the model reads says that every message
    starts with a step's name."""
    texts = {
        "workflow_check_draft": CHECK_DRAFT.description,
        "workflows.issues": issues.__doc__ or "",
        "SKILL.md": SKILL.instructions,
    }
    for name, text in texts.items():
        flat = " ".join(text.split())
        assert "one-step issue" in flat, name
        for claim in (
            "each message starting with",
            "Each message starts with",
            "its message starts with the step's",
        ):
            assert claim not in flat, (name, claim)


def test_the_skill_lists_only_issues_a_draft_can_get() -> None:
    """A draft naming a tool workflow_tools does not list is refused before
    the check, so the check never answers it with tool_missing or
    tool_removed."""
    for code in ("tool_missing", "tool_removed"):
        assert code not in SKILL.instructions, code


def test_the_skill_has_no_dashes_inside_sentences() -> None:
    for name, text in TEXTS.items():
        assert "—" not in text and "–" not in text, name


def test_the_prompt_says_what_the_assistant_creates_and_how_it_asks() -> None:
    assert "You cannot change anything in GOAT" not in INSTRUCTIONS
    assert "You change nothing that exists in GOAT." in INSTRUCTIONS
    for name in (
        "workflow_create",
        "project_add_catalog_layer",
        "ask_user",
        "skills_load",
    ):
        assert name in INSTRUCTIONS
    assert ANSWER_OPEN in INSTRUCTIONS
    assert "the user clicks Run" in INSTRUCTIONS


def test_one_rule_says_when_to_ask_and_how() -> None:
    """Asking in text and asking with the card are one rule, so the model does
    not ask a question in text where a card fits."""
    bullets = INSTRUCTIONS.split("\n- ")
    [rule] = [bullet for bullet in bullets if "ask_user" in bullet]
    assert "ambiguous" in rule and "one short question" in rule
    assert ANSWER_OPEN in rule
    assert [bullet for bullet in bullets if "ambiguous" in bullet] == [rule]


def test_the_skill_limits_a_layer_larger_than_the_place() -> None:
    """project_get_layers shows a layer's extent and feature count when
    known; a layer far larger than the place asked about gets `filter.area`,
    and the heatmap's destination limit is fixed the same way."""
    flat = " ".join(SKILL.instructions.split())
    # A table, an empty extent and a locked layer come without one.
    assert "shows a layer's `extent`" in flat
    assert "`feature_count` when known" in flat
    assert "project layers included" in flat
    assert "- `too_many_destinations`:" in SKILL.instructions


def test_a_template_input_takes_only_a_layer_that_fits_the_place() -> None:
    """A template's inputs are bound to layers as they are, without a filter,
    so a layer far larger than the place makes a draft with `filter.area`."""
    template_step = SKILL.instructions.split("2. **Look for a template.**")[1]
    flat = " ".join(template_step.split("3. **")[0].split())
    assert "A binding takes no filter" in flat
    assert "covers far more than the place" in flat
    assert "build a draft with `filter.area` instead of using the template" in flat


def test_what_the_workflow_is_named_follows_the_users_message() -> None:
    """The skill said "in the user's language", which models read as the
    language of the project's German layer names (wf-02, wf-03). The prompt
    and the draft's own field descriptions say the same as the skill."""
    flat = " ".join(SKILL.instructions.split())
    assert (
        "The workflow's `name`, the step labels and the export names are in the "
        "language of the user's message, as your answer is" in flat
    )
    assert "the names of layers stay as they are" in flat
    assert "the user's language" not in flat
    for model, name in (
        (Draft, "name"),
        (ToolStep, "label"),
        (DatasetStep, "label"),
        (ExportStep, "name"),
    ):
        described = model.model_fields[name].description or ""
        assert "in the language of the user's message" in described, model


def test_the_skill_searches_the_catalog_once_per_dataset() -> None:
    """wf-05 and wf-09: with no rule on when the search is done, models
    searched the catalog in circles until the answer's budget was gone."""
    find = SKILL.instructions.split("3. **Find the data.**")[1].split("4. **")[0]
    flat = " ".join(find.split())
    assert "search the catalog for it once" in flat
    assert "German and English words in q, separated by commas" in flat
    assert "do not search for that dataset again with other words" in flat
    # A step left open is the user's to fill in the editor, not a card's.
    assert "needs no card" in flat
