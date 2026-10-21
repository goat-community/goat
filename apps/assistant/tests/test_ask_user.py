"""ask_user (spec §5.1, §5.2): the card's limits, the data-ask part, option
values that never reach the web, and a run that ends after asking."""

import json
import re
from typing import Any

import pytest
from pydantic import ValidationError
from pydantic_ai.exceptions import ToolFailed

from assistant.agent import RunDeps, build_agent
from assistant.asks import CARD_ID_PATTERN, AskUserInput, card_data, public_args
from assistant.context import parse_context
from assistant.encoding.ai_sdk import AiSdkEncoder
from assistant.events import DataPart, ToolCalled, to_ui_message
from assistant.prompt import render_note
from assistant.tools.ask import ASK_USER, ASKED_NOTE
from assistant.tools.registry import BY_WIRE_NAME
from assistant.tools.runtime import execute
from assistant.tools.testing import ScriptedModel, fake_clients, tool_env
from assistant.tools.toolset import _call_key

CARD: dict[str, Any] = {
    "questions": [
        {
            "question": "Which schools should the catchments start from?",
            "header": "Schools",
            "options": [
                {
                    "label": "Schulen (Stand 2019)",
                    "description": "Older list",
                    "value": "32",
                },
                {
                    "label": "Schulen",
                    "description": "The current list",
                    "recommended": True,
                    "value": "31",
                },
            ],
        },
        {
            "question": "Which destinations matter?",
            "header": "Destinations",
            "multi_select": True,
            "options": [
                {
                    "label": "Supermarkets",
                    "description": "Adds it to the project",
                    "value": "eval-supermaerkte-bayern",
                },
                {"label": "Leave it open", "description": "Choose it later"},
            ],
        },
    ]
}


def _question(**changes: Any) -> dict[str, Any]:
    question: dict[str, Any] = {
        "question": "Which one?",
        "header": "Data",
        "options": [{"label": "A"}, {"label": "B"}],
    }
    question.update(changes)
    return question


def _rejected(card: dict[str, Any]) -> str:
    with pytest.raises(ValidationError) as caught:
        AskUserInput.model_validate(card)
    return str(caught.value)


def test_a_card_has_one_to_four_questions() -> None:
    assert "at least 1" in _rejected({"questions": []})
    assert "at most 4" in _rejected({"questions": [_question()] * 5})
    assert (
        len(AskUserInput.model_validate({"questions": [_question()] * 4}).questions)
        == 4
    )


def test_a_question_is_a_sentence_ending_in_a_question_mark() -> None:
    assert "ends in '?'" in _rejected({"questions": [_question(question="Pick one")]})
    assert "at most 300" in _rejected(
        {"questions": [_question(question="x" * 300 + "?")]}
    )


def test_a_header_is_a_chip_of_at_most_twelve_characters() -> None:
    assert "at most 12" in _rejected({"questions": [_question(header="Destinations!")]})
    assert "at least 1" in _rejected({"questions": [_question(header="")]})


def test_a_question_has_two_to_four_options() -> None:
    assert "at least 2" in _rejected(
        {"questions": [_question(options=[{"label": "A"}])]}
    )
    five = [{"label": f"O{n}"} for n in range(5)]
    assert "at most 4" in _rejected({"questions": [_question(options=five)]})


def test_labels_and_descriptions_are_short() -> None:
    long_label = [{"label": "x" * 61}, {"label": "B"}]
    assert "at most 60" in _rejected({"questions": [_question(options=long_label)]})
    long_text = [{"label": "A", "description": "x" * 201}, {"label": "B"}]
    assert "at most 200" in _rejected({"questions": [_question(options=long_text)]})


def test_at_most_one_option_is_recommended_and_it_comes_first() -> None:
    both = [{"label": "A", "recommended": True}, {"label": "B", "recommended": True}]
    assert "at most one option" in _rejected({"questions": [_question(options=both)]})
    card = AskUserInput.model_validate(CARD)
    assert [o.label for o in card.questions[0].options] == [
        "Schulen",
        "Schulen (Stand 2019)",
    ]


@pytest.mark.parametrize("label", ["Other", "other…", "Andere", "Sonstiges"])
def test_the_model_never_adds_other_the_card_does(label: str) -> None:
    options = [{"label": "A"}, {"label": label}]
    assert "free-text 'Other' itself" in _rejected(
        {"questions": [_question(options=options)]}
    )


async def test_ask_user_shows_the_card_without_values_and_says_to_wait() -> None:
    emitted: list[tuple[str, dict[str, Any], str | None]] = []

    async def emit(
        name: str, data: dict[str, Any], *, part_id: str | None = None
    ) -> str:
        emitted.append((name, data, part_id))
        return part_id or "m:1"

    env = tool_env(fake_clients(), emit_data=emit)
    result = await execute(ASK_USER, env, CARD, tool_call_id="call-7")
    card_id = result["card_id"]
    # Minted for the card: providers may repeat their tool call ids.
    assert re.fullmatch(CARD_ID_PATTERN, card_id) and "call-7" not in card_id
    assert result == {"card_id": card_id, "status": "asked", "note": ASKED_NOTE}
    [(name, data, part_id)] = emitted
    assert (name, part_id) == ("ask", card_id)
    assert data == card_data(card_id, AskUserInput.model_validate(CARD))
    assert data["questions"][0]["options"][0] == {
        "label": "Schulen",
        "description": "The current list",
        "recommended": True,
    }
    assert "value" not in json.dumps(data)


async def test_ask_user_needs_the_assistant_dock() -> None:
    with pytest.raises(ToolFailed, match="only be asked in the GOAT assistant"):
        await execute(ASK_USER, tool_env(fake_clients()), CARD, tool_call_id="c1")


def test_public_args_drop_values_from_ask_user_only() -> None:
    public = public_args("ask_user", CARD)
    assert "value" not in json.dumps(public)
    assert public["questions"][0]["options"][1]["label"] == "Schulen"
    other = {"questions": [{"options": [{"value": "kept"}]}]}
    assert public_args("core_find", other) == other
    # Arguments that are not a card show nothing: they may be the model's raw
    # text, values included.
    assert public_args("ask_user", {"questions": "not a list"}) == {}
    raw = '{"questions":[{"options":[{"label":"A","value":"31"'
    public = public_args("ask_user", {"INVALID_JSON": raw})
    assert raw not in json.dumps(public) and "31" not in json.dumps(public)


_RAW_OPTIONS = '[{"label":"A","value":"31"},{"label":"B"}]'
_RAW_QUESTION = '{"question":"Q?","options":[{"label":"A","value":"31"}]}'
_RAW_OPTION = '{"label":"A","value":"31"}'


@pytest.mark.parametrize(
    ("args", "shown"),
    [
        (
            {"questions": [{"question": "Q?", "options": _RAW_OPTIONS}]},
            {"questions": [{"question": "Q?"}]},
        ),
        ({"questions": [_RAW_QUESTION]}, {"questions": []}),
        (
            {
                "questions": [
                    {"question": "Q?", "options": [_RAW_OPTION, {"label": "B"}]}
                ]
            },
            {"questions": [{"question": "Q?", "options": [{"label": "B"}]}]},
        ),
        (
            {"questions": [], "values": _RAW_OPTION},
            {"questions": []},
        ),
        (
            {"questions": [{"options": [{"label": "A", "values": "31"}]}]},
            {"questions": [{"options": [{"label": "A"}]}]},
        ),
        (
            {"questions": [{"options": [{"label": "A", "Value": "31"}]}]},
            {"questions": [{"options": [{"label": "A"}]}]},
        ),
        (
            {"questions": [{"question": "Q?", "note": "31"}]},
            {"questions": [{"question": "Q?"}]},
        ),
        (
            {"questions": [{"options": [{"label": {"text": "A", "value": "31"}}]}]},
            {"questions": [{"options": [{}]}]},
        ),
    ],
    ids=[
        "options-as-text",
        "question-as-text",
        "option-as-text",
        "own-key",
        "option-key-values",
        "option-key-Value",
        "question-key-note",
        "label-as-object",
    ],
)
def test_public_args_show_only_the_shapes_of_a_card(
    args: dict[str, Any], shown: dict[str, Any]
) -> None:
    """Rebuilt, not filtered: text where a question, its options or an option
    belongs, keys of the model's own and objects where a card has a plain value
    may hold values."""
    public = public_args("ask_user", args)
    assert public == shown
    assert "31" not in json.dumps(public)


def test_the_stream_never_carries_option_values() -> None:
    chunks = AiSdkEncoder().encode(
        ToolCalled(tool_call_id="c1", tool_name="ask_user", args=CARD)
    )
    assert "eval-supermaerkte-bayern" not in json.dumps(chunks)
    assert chunks[1]["input"] == public_args("ask_user", CARD)


def test_a_reloaded_message_never_carries_option_values() -> None:
    part = {
        "type": "tool",
        "tool_call_id": "c1",
        "tool_name": "ask_user",
        "args": CARD,
        "state": "output",
        "output": {"card_id": "ask-c1", "status": "asked", "note": ASKED_NOTE},
        "error": None,
    }
    message = to_ui_message("m1", "assistant", [part])
    assert "eval-supermaerkte-bayern" not in json.dumps(message)
    assert message["parts"][0]["input"] == public_args("ask_user", CARD)


async def test_after_asking_the_run_offers_no_more_tools() -> None:
    script = ScriptedModel([("ask_user", CARD)], answer="I asked you above.")
    page = parse_context({"surface": "catalog"})
    seen: list[DataPart] = []

    async def emit(event: Any) -> None:
        if isinstance(event, DataPart):
            seen.append(event)

    deps = RunDeps(
        message_id="m1", emit=emit, prompt_note=render_note(page, None, "en")
    )
    deps.env = tool_env(fake_clients(), page=page, emit_data=deps.emit_data)
    result = await build_agent(script.model).run("which data?", deps=deps)
    assert result.output == "I asked you above."
    assert script.infos[0].function_tools != []
    assert script.infos[1].function_tools == []
    assert deps.asked is True
    [part] = seen
    assert part.name == "ask" and part.part_id == part.data["card_id"]


def test_ask_user_is_never_answered_from_an_earlier_call() -> None:
    assert _call_key(BY_WIRE_NAME["ask_user"], CARD) is None


def test_ask_user_is_on_every_page_and_not_on_mcp() -> None:
    assert ASK_USER.wire_name == "ask_user"
    assert ASK_USER.risk == "read" and not ASK_USER.mcp and not ASK_USER.returns_data
