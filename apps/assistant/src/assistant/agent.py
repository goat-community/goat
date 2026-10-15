"""The assistant's agent: GOAT's tools (assistant.tools), the prompt of
assistant.prompt, models from the model layer (assistant.llm)."""

import asyncio
import functools
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.messages import ModelMessage, RetryPromptPart, ToolReturnPart
from pydantic_ai.models import Model
from pydantic_ai.models.function import (
    AgentInfo,
    DeltaToolCall,
    DeltaToolCalls,
    FunctionModel,
)
from pydantic_ai.models.instrumented import InstrumentationSettings
from pydantic_ai.models.test import TestModel

from assistant.budget import RunBudget
from assistant.events import DataPart, RunEvent
from assistant.history import shorten_earlier_results
from assistant.llm.types import DataPolicy
from assistant.prompt import ANSWER_NOW, INSTRUCTIONS, static_instructions
from assistant.tools.runtime import ToolEnv
from assistant.tools.toolset import TOOL_RETRIES, goat_toolset

__all__ = ["INSTRUCTIONS", "PartIds", "RunDeps", "build_agent", "dev_model"]


class PartIds:
    """``{message_id}:{n}`` part IDs, stable across replay (spec §6.2)."""

    def __init__(self, message_id: str) -> None:
        self._message_id = message_id
        self._n = 0

    def next(self) -> str:
        self._n += 1
        return f"{self._message_id}:{self._n}"


@dataclass
class RunDeps:
    message_id: str
    emit: Callable[[RunEvent], Awaitable[None]]
    part_ids: PartIds | None = None
    #: The organization's data policy (spec §4.7); the tool layer (plan 3)
    #: filters what data-returning tools send to the model by it.
    data_policy: DataPolicy = "restricted"
    #: The run's tool environment (assistant.tools.runtime); None runs without
    #: GOAT's tools (the run machinery's own tests).
    env: ToolEnv | None = None
    #: The run's note: UI language and page context (assistant.prompt.render_note).
    #: It goes into the user message (assistant.prompt.with_note), not the
    #: instructions, so the cached prefix stays the same between messages.
    prompt_note: str = ""
    #: The run's limits; near them the model answers without tools
    #: (assistant.budget). None: no early answer (the hard limits still apply).
    budget: RunBudget | None = None
    #: Read tools' results of this answer by call (assistant.tools.toolset): a
    #: repeated call gets the earlier result instead of a second request. The
    #: fallback model never inherits any: it only takes over before a tool ran.
    earlier_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.part_ids is None:
            self.part_ids = PartIds(self.message_id)

    async def emit_data(self, name: str, data: dict[str, Any]) -> str:
        assert self.part_ids is not None
        part_id = self.part_ids.next()
        await self.emit(DataPart(name=name, part_id=part_id, data=data))
        return part_id


async def _demo_stream(
    messages: list[ModelMessage], info: AgentInfo
) -> AsyncIterator[str | DeltaToolCalls]:
    """Development model: where it is offered (every page) it proposes filters
    once, then gives a slow answer (long enough to reload mid-run)."""
    last_parts = getattr(messages[-1], "parts", [])
    answered = any(
        isinstance(part, (ToolReturnPart, RetryPromptPart)) for part in last_parts
    )
    offered = {tool.name for tool in info.function_tools}
    if not answered and "catalog_propose_filters" in offered:
        yield {
            0: DeltaToolCall(
                name="catalog_propose_filters",
                json_args='{"title": "Cycling networks", "q": "Radverkehr"}',
            )
        }
        return
    for word in ("This ", "is ", "a ", "slow ", "demo ", "answer. ") * 10:
        await asyncio.sleep(0.4)
        yield word


def dev_model(model_name: str) -> Model:
    if model_name == "demo":
        return FunctionModel(stream_function=_demo_stream)
    if model_name == "test":
        return TestModel(custom_output_text="Here is a test answer.")
    raise ValueError(f"Unknown development model {model_name!r} (use 'test' or 'demo')")


@functools.cache
def _content_free_tracing() -> InstrumentationSettings:
    return InstrumentationSettings(include_content=False)


def instrumentation() -> InstrumentationSettings | None:
    """Tracing for an agent (spec §3): one trace per run with a span per model
    and tool call, never prompts, answers or tool results. On only with
    ``OTEL_ENABLED``, the switch ``goatobs.setup_observability`` reads; read at
    call time, so it follows the environment of the process."""
    enabled = os.environ.get("OTEL_ENABLED", "").lower() in ("true", "1", "yes")
    return _content_free_tracing() if enabled else None


def answer_now(ctx: RunContext[RunDeps]) -> str:
    """The instruction for a run near its limits; nothing otherwise, so the
    fixed instructions stay the cached prefix."""
    budget = ctx.deps.budget
    return ANSWER_NOW if budget is not None and budget.spent(ctx.usage) else ""


def build_agent(model: Model | str) -> Agent[RunDeps, str]:
    """The assistant's agent on ``model``; a string selects a development model
    (``test`` or ``demo``). Fixed instructions only (cached; the run's note
    travels in the user message), GOAT's tools for the run's surface in a
    fixed order."""
    agent: Agent[RunDeps, str] = Agent(
        dev_model(model) if isinstance(model, str) else model,
        deps_type=RunDeps,
        instructions=[*static_instructions(), answer_now],
        toolsets=[goat_toolset()],
        # Earlier answers' long tool results go to the model as counts.
        capabilities=[ProcessHistory(shorten_earlier_results)],
        # Also the budget for a tool name the surface does not offer: a history
        # from another page can make the model call one (spec §4.8).
        retries=TOOL_RETRIES,
    )
    agent.instrument = instrumentation()
    return agent
