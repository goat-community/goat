"""Runs one eval task with a model: the production agent, prompt, tool layer
and limits, against the fixed backends, and records what happened."""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

import httpx
from pydantic_ai import AgentRunResultEvent
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    PartDeltaEvent,
    PartStartEvent,
    RetryPromptPart,
    TextPart,
    TextPartDelta,
    UserPromptPart,
)
from pydantic_ai.models import Model
from pydantic_ai.usage import RunUsage, UsageLimits

from assistant.agent import RunDeps, build_agent
from assistant.budget import RunBudget
from assistant.config import AssistantSettings
from assistant.context import PageContext, parse_context
from assistant.events import DataPart, RunEvent
from assistant.login import StaticLogin
from assistant.prompt import render_note, with_note
from assistant.tools.runtime import ToolEnv, client_secrets
from evals.backends import Backends
from evals.tasks import EvalTask

#: The eval user; the fixed backends answer for anyone.
EVAL_USER = UUID(int=0xE7A1)


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]
    result: Any
    failed: bool


@dataclass
class Transcript:
    task_id: str
    answer: str
    tool_calls: list[ToolCall]
    proposals: list[dict[str, Any]]
    requests: dict[str, list[httpx.Request]] = field(repr=False)
    error: str | None
    input_tokens: int
    output_tokens: int
    seconds: float
    first_text_seconds: float | None
    #: Of ``input_tokens``, read from the provider's prompt cache.
    cache_read_tokens: int = 0


def _content(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


class _ToolLog:
    """The run's tool calls, built from the stream as it happens, so a run that
    fails halfway still shows what it did (the safety checks read this)."""

    def __init__(self) -> None:
        self._calls: dict[str, ToolCall] = {}

    def see(self, event: Any) -> None:
        if isinstance(event, FunctionToolCallEvent):
            part = event.part
            self._calls[part.tool_call_id] = ToolCall(
                part.tool_name, part.args_as_dict(), None, False
            )
        elif isinstance(event, FunctionToolResultEvent):
            reply = event.part
            call = self._calls.get(reply.tool_call_id)
            if call is None:
                return
            call.result = _content(reply.content)
            # A ToolFailed from the tool: the model sees the failure and the run goes on.
            # Anything but success (failed, denied, interrupted), as runs/translate.py reads it.
            call.failed = isinstance(reply, RetryPromptPart) or (
                getattr(reply, "outcome", "success") != "success"
            )

    @property
    def calls(self) -> list[ToolCall]:
        return list(self._calls.values())


def _is_text(event: Any) -> bool:
    if isinstance(event, PartStartEvent):
        return isinstance(event.part, TextPart) and bool(event.part.content)
    return isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta)


def _history(task: EvalTask, page: PageContext) -> list[ModelMessage]:
    """The task's earlier turns as the app replays them: each user text with
    the note of its time, then the answer."""
    messages: list[ModelMessage] = []
    for turn in task.history:
        note = render_note(page, page if messages else None, task.locale, turn.user)
        messages.append(
            ModelRequest(parts=[UserPromptPart(content=with_note(note, turn.user))])
        )
        messages.append(ModelResponse(parts=[TextPart(content=turn.assistant)]))
    return messages


async def run_task(
    task: EvalTask, model: Model, backends: Backends, settings: AssistantSettings
) -> Transcript:
    page = parse_context(task.context)
    services, requests = backends.clients()
    events: list[RunEvent] = []

    async def emit(event: RunEvent) -> None:
        events.append(event)

    env = ToolEnv(
        services=services,
        login=StaticLogin("eval-token"),
        user_id=EVAL_USER,
        data_policy=task.data_policy,
        page=page,
        locale=task.locale,
        extra_secrets=client_secrets(settings),
    )
    deps = RunDeps(
        message_id=str(uuid4()),
        emit=emit,
        data_policy=task.data_policy,
        env=env,
        prompt_note=render_note(
            page, page if task.history else None, task.locale, task.prompt
        ),
        budget=RunBudget(
            max_tokens=settings.run_max_tokens,
            max_tool_calls=settings.run_max_tool_calls,
        ),
    )
    env.emit_data = deps.emit_data
    agent = build_agent(model)
    limits = UsageLimits(
        tool_calls_limit=settings.run_max_tool_calls,
        total_tokens_limit=settings.run_max_tokens,
    )
    started = time.monotonic()
    first_text: float | None = None
    result = None
    error: str | None = None
    log = _ToolLog()
    # The caller's usage, as RunManager does: tokens of a run that fails or
    # times out are still counted.
    usage = RunUsage()
    try:
        async with asyncio.timeout(settings.run_max_seconds):
            async with agent.run_stream_events(
                with_note(deps.prompt_note, task.prompt),
                deps=deps,
                message_history=_history(task, page) or None,
                usage_limits=limits,
                usage=usage,
            ) as stream:
                async for event in stream:
                    log.see(event)
                    if isinstance(event, AgentRunResultEvent):
                        result = event.result
                    elif first_text is None and _is_text(event):
                        first_text = time.monotonic() - started
    except Exception as exc:  # a failed run is a failed task, not a failed eval
        error = f"{type(exc).__name__}: {exc}"
    finally:
        await services.aclose()
    return Transcript(
        task_id=task.id,
        answer=str(result.output) if result is not None else "",
        tool_calls=log.calls,
        proposals=[
            e.data for e in events if isinstance(e, DataPart) and e.name == "proposal"
        ],
        requests=requests,
        error=error,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        seconds=time.monotonic() - started,
        first_text_seconds=first_text,
        cache_read_tokens=usage.cache_read_tokens,
    )
