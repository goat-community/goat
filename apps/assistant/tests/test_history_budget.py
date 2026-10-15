"""A long conversation stays affordable: earlier answers' long tool results
go to the model as counts (assistant.history), and a run near its limits
answers with what it found instead of failing (assistant.budget)."""

from typing import Any

import pytest
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.usage import RunUsage

from assistant.agent import RunDeps, build_agent
from assistant.budget import RunBudget
from assistant.context import parse_context
from assistant.history import SHORTENED, shorten_earlier_results
from assistant.prompt import ANSWER_NOW, render_note, with_note
from assistant.tools.testing import ScriptedModel, fake_clients, tool_env

WORKFLOWS = {
    "projects": [],
    "workflows": [
        {"id": str(n), "name": f"Workflow {n}", "description": "d" * 200}
        for n in range(20)
    ],
    "total": 20,
    "query": "Anna",
}


def _call(tool: str, call_id: str) -> ModelResponse:
    return ModelResponse(
        parts=[ToolCallPart(tool_name=tool, args={}, tool_call_id=call_id)]
    )


def _result(tool: str, call_id: str, content: Any) -> ModelRequest:
    return ModelRequest(
        parts=[ToolReturnPart(tool_name=tool, content=content, tool_call_id=call_id)]
    )


def _content(message: ModelMessage) -> Any:
    [part] = message.parts
    assert isinstance(part, ToolReturnPart)
    return part.content


def test_earlier_long_results_are_shortened_to_their_counts() -> None:
    shown = {
        "groups": [{"title": "Tool 3", "items": [{"id": "w1", "name": "Huff"}] * 30}]
    }
    messages: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="workflows from Anna?")]),
        _call("core_find", "c1"),
        _result("core_find", "c1", WORKFLOWS),
        _call("core_whoami", "c2"),
        _result("core_whoami", "c2", {"name": "Tom"}),
        _call("core_show_items", "c3"),
        _result("core_show_items", "c3", shown),
        ModelResponse(parts=[TextPart(content="Here are her workflows.")]),
        # The current answer: its results stay whole.
        ModelRequest(parts=[UserPromptPart(content="and her layouts?")]),
        _call("core_find", "c4"),
        _result("core_find", "c4", WORKFLOWS),
    ]

    sent = shorten_earlier_results(messages)

    assert len(sent) == len(messages)
    assert _content(sent[2]) == {
        "shortened": SHORTENED,
        "projects": "0 items",
        "workflows": "20 items",
        "total": 20,
        "query": "Anna",
    }
    # Short results, and what the user was shown as cards, stay whole.
    assert _content(sent[4]) == {"name": "Tom"}
    assert _content(sent[6]) == shown
    # The answers' own words, and the current answer, are untouched.
    assert sent[7] is messages[7]
    assert _content(sent[10]) == WORKFLOWS
    # The input is not changed: the stored history keeps everything.
    assert _content(messages[2]) == WORKFLOWS


def test_earlier_reasoning_is_left_out_and_the_current_kept() -> None:
    earlier = ModelResponse(
        parts=[
            ThinkingPart(content="long reasoning " * 200),
            TextPart(content="She has 20."),
        ]
    )
    only_reasoning = ModelResponse(parts=[ThinkingPart(content="hm")])
    current = ModelResponse(
        parts=[
            ThinkingPart(content="now"),
            ToolCallPart(tool_name="core_find", args={}),
        ]
    )
    messages: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="q")]),
        earlier,
        only_reasoning,
        ModelRequest(parts=[UserPromptPart(content="next")]),
        current,
    ]
    sent = shorten_earlier_results(messages)
    assert sent[1].parts == [TextPart(content="She has 20.")]
    assert sent[2] is only_reasoning
    assert sent[4] is current


def test_a_long_text_or_list_result_keeps_its_start_or_its_count() -> None:
    messages: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="q")]),
        _call("catalog_get_record", "c1"),
        _result("catalog_get_record", "c1", "x" * 5000),
        _call("project_sample_features", "c2"),
        _result("project_sample_features", "c2", [{"a": "y" * 100}] * 40),
        ModelResponse(parts=[TextPart(content="a")]),
        ModelRequest(parts=[UserPromptPart(content="next")]),
    ]
    sent = shorten_earlier_results(messages)
    text = _content(sent[2])
    assert text.startswith("x" * 300) and text.endswith(f"({SHORTENED})")
    assert _content(sent[4]) == {"shortened": SHORTENED, "items": "40 items"}


async def test_the_model_gets_earlier_results_shortened_in_a_real_run() -> None:
    page = parse_context(None)

    async def emit(event: Any) -> None:
        return None

    deps = RunDeps(
        message_id="m2",
        emit=emit,
        env=tool_env(fake_clients(), page=page),
        prompt_note=render_note(page, None, "en"),
    )
    history: list[ModelMessage] = [
        ModelRequest(parts=[UserPromptPart(content="workflows from Anna?")]),
        _call("core_find", "c1"),
        _result("core_find", "c1", WORKFLOWS),
        ModelResponse(parts=[TextPart(content="She has 20.")]),
    ]
    script = ScriptedModel()
    result = await build_agent(script.model).run(
        with_note(deps.prompt_note, "which are newest?"),
        deps=deps,
        message_history=history,
    )
    [request] = script.requests
    assert _content(request[2])["shortened"] == SHORTENED
    assert result.output == "done"


@pytest.mark.parametrize(
    ("usage", "spent"),
    [
        (RunUsage(), False),
        (RunUsage(requests=3, tool_calls=24, input_tokens=30), False),
        # Five tool calls kept in reserve of 30.
        (RunUsage(requests=3, tool_calls=25, input_tokens=30), True),
        # 600 spent in two calls: the next may take 600 more, past 1000.
        (RunUsage(requests=2, input_tokens=560, output_tokens=40), True),
        (RunUsage(requests=2, input_tokens=280, output_tokens=20), False),
    ],
)
def test_the_budget_is_spent_near_either_limit(usage: RunUsage, spent: bool) -> None:
    assert RunBudget(max_tokens=1000, max_tool_calls=30).spent(usage) is spent


def test_a_small_tool_call_limit_keeps_a_smaller_reserve() -> None:
    budget = RunBudget(max_tokens=10**9, max_tool_calls=1)
    assert budget.spent(RunUsage(requests=1, tool_calls=0)) is False
    assert budget.spent(RunUsage(requests=1, tool_calls=1)) is True


async def test_near_its_limits_a_run_answers_without_tools() -> None:
    page = parse_context(None)

    async def emit(event: Any) -> None:
        return None

    deps = RunDeps(
        message_id="m1",
        emit=emit,
        env=tool_env(fake_clients(), page=page),
        prompt_note=render_note(page, None, "en"),
        # One tool call kept in reserve of six: tools for five.
        budget=RunBudget(max_tokens=10**9, max_tool_calls=6),
    )
    script = ScriptedModel(calls=[("core_page_context", {})] * 5)
    result = await build_agent(script.model).run(
        with_note(deps.prompt_note, "where am I?"), deps=deps
    )
    assert result.output == "done"

    def instructions(index: int) -> str:
        parts = script.infos[index].model_request_parameters.instruction_parts or []
        return "\n".join(part.content for part in parts)

    assert script.infos[0].function_tools and ANSWER_NOW not in instructions(0)
    # After five calls: no tools, and the model is told to answer.
    assert script.infos[5].function_tools == []
    assert ANSWER_NOW in instructions(5)
