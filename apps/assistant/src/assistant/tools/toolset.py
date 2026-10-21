"""The Pydantic AI adapter of the tool layer (spec §3: one definition, two
adapters; the MCP adapter is ``assistant.mcp_server``).

Every tool is registered once with its input model's JSON schema; validation,
the data policy and the audit happen in ``execute``. A filter keeps the tools of
the run's surface, in registry order. A run without a tool environment (the run
machinery's own tests) is offered none.
"""

import json
from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal

from pydantic import ValidationError
from pydantic_ai import RunContext, Tool
from pydantic_ai.exceptions import ModelRetry, ToolFailed
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import AbstractToolset, FunctionToolset
from pydantic_core import SchemaValidator, core_schema

from assistant.asks import ASK_TOOL
from assistant.budget import StepGuard, next_call
from assistant.history import SHOWN_TOOLS
from assistant.tools.http import service_failed
from assistant.tools.registry import ALL_TOOLS, BY_WIRE_NAME, tools_for
from assistant.tools.runtime import (
    InputInvalid,
    ResultOverCap,
    ToolSpec,
    execute,
    refuse,
)

if TYPE_CHECKING:
    from assistant.agent import RunDeps

#: Retries the model gets to fix the arguments of one tool. The attempt after
#: the last retry fails the call (ToolFailed), not the run (Decision T22).
TOOL_RETRIES = 3

#: Key under which arguments that are not a JSON object reach ``call``. The
#: framework unpacks the arguments as keywords, so a list or a string would
#: fail before ``call`` runs and take the whole run down with it.
_NOT_AN_OBJECT = "<arguments>"

#: Added to a read tool's result when the same call already ran in this answer.
REPEATED_CALL = (
    "You made this call with the same arguments earlier in this answer; this is "
    "its result again. Use it instead of repeating the call."
)

#: Added to a write tool's result when the same call already ran in this
#: conversation: nothing was created again, also when the user has removed
#: what the first call created.
REPEATED_WRITE = (
    "You made this call with the same arguments earlier in this conversation; "
    "nothing was created again. This is the first call's result. If the user "
    "removed it and wants it again, say so: they add a dataset again by hand "
    "(Add to project in the catalog), and you create a workflow again under a "
    "changed name."
)


#: The failure of a call past the run's tool-call limit (``assistant.budget``):
#: the call did not run, and the answer comes next.
LOOK_UPS_USED_UP = (
    "This answer's look-ups are used up, so this call did not run. Answer from "
    "what you found."
)

#: The failure of a result that would leave the answer too little room
#: (``assistant.budget``): the call ran, or repeats one that was refused; its
#: result is not sent, and the run's look-ups are over.
RESULT_TOO_LARGE = (
    "This result is too large for what is left of this answer, so it was not "
    "sent. Answer from what you found."
)

#: The failure of a call the service failed twice for in this answer (the
#: same tool with the same arguments, ``http.service_failed``): the call did
#: not run. The first retry runs, since a service can fail for a moment.
SERVICE_FAILED_TWICE = (
    "The service failed twice for this call, so it did not run again. Answer "
    "from what you found, or try something else."
)
SERVICE_FAILURES = 2

#: Results in a row of the answer's catalog searches (the tools with
#: ``ToolSpec.found_nothing``) that found nothing, after which they do not run
#: again in that answer. A model that finds nothing tends to search on with
#: other words, and each search takes a look-up and a model call from the
#: answer's budget, which the answer then lacks for what it was asked to do. A
#: result that finds something starts the count again, so an answer can still
#: look for several datasets.
FRUITLESS_SEARCHES = 4
SEARCHED_ENOUGH = (
    f"This answer's last {FRUITLESS_SEARCHES} catalog searches found nothing, so "
    "this one did not run. The catalog has no dataset for what you searched: "
    "answer without it, and in a workflow leave that dataset step open."
)

#: Responses of a run with neither text nor a tool call (only reasoning, only
#: whitespace, or nothing) that end its look-ups: the next call is the answer
#: step. Each is asked again with the same tools (by Pydantic AI, or for only
#: whitespace by ``assistant.agent.ends_with_text``), and a model that gave one
#: often gives the next alike, until the run fails on its output retries. The
#: first is asked again as it is, since a provider can return one by chance.
SILENT_RESPONSES = 2


def _as_arguments(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {_NOT_AN_OBJECT: True}


_ARGUMENTS_VALIDATOR = SchemaValidator(
    core_schema.no_info_plain_validator_function(_as_arguments)
)


def _call_key(spec: ToolSpec[Any, Any], arguments: dict[str, Any]) -> str | None:
    """The same for two calls that ask the same, defaults included, and for
    every call of a tool that runs once per answer (``once_per_answer``); None
    for a call that counts every time (a proposal, a card the user is shown)
    and for arguments that do not validate (``execute`` says why). A write tool
    always has one, card or not: a retry gets what the first call created
    instead of creating it again."""
    if spec.risk == "propose" or (
        spec.risk == "read" and spec.wire_name in SHOWN_TOOLS
    ):
        return None
    try:
        validated = spec.input_model.model_validate(arguments)
    except ValidationError:
        return None
    if spec.once_per_answer is not None:
        return spec.wire_name
    canonical = json.dumps(validated.model_dump(mode="json"), sort_keys=True)
    return f"{spec.wire_name} {canonical}"


def earlier_writes(messages: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """The first result of each write call stored in a conversation, by call
    key. A run starts with them in ``RunDeps.earlier_results``, so a write
    repeated in a later answer (a retry, "try again") returns what the first
    call created. Read from the stored parts (``events.fold_parts``), which
    keep every call that returned, also of an answer cancelled afterwards."""
    found: dict[str, dict[str, Any]] = {}
    for message in messages:
        if message.get("role") != "assistant":
            continue
        for part in message.get("parts") or []:
            if not isinstance(part, dict) or part.get("type") != "tool":
                continue
            spec = BY_WIRE_NAME.get(str(part.get("tool_name")))
            output, args = part.get("output"), part.get("args")
            if (
                spec is None
                or spec.risk != "write"
                or part.get("state") != "output"
                or not isinstance(output, dict)
                or not isinstance(args, dict)
                or "repeated_call" in output
            ):
                continue
            key = _call_key(spec, args)
            if key is not None:
                found.setdefault(key, output)
    return found


def _tool(spec: ToolSpec[Any, Any]) -> "Tool[RunDeps]":
    # ``ctx`` is positional-only: a model-chosen argument named "ctx" must reach
    # ``execute`` as an argument, not collide with the context parameter.
    async def call(ctx: "RunContext[RunDeps]", /, **arguments: Any) -> dict[str, Any]:
        env = ctx.deps.env
        if env is None:  # filtered out below; kept as a guard
            raise ModelRetry("This tool is not available here.")
        guard = _step_guard(ctx)
        if guard is not None and not guard.admit_call():
            await refuse(
                spec, env, arguments, LOOK_UPS_USED_UP, tool_call_id=ctx.tool_call_id
            )
        if spec.found_nothing is not None and (
            ctx.deps.fruitless_searches.get(ctx.run_id, 0) >= FRUITLESS_SEARCHES
        ):
            await refuse(
                spec, env, arguments, SEARCHED_ENOUGH, tool_call_id=ctx.tool_call_id
            )
        try:
            if _NOT_AN_OBJECT in arguments:
                raise InputInvalid("The arguments must be a JSON object.")
            # The whole result again, not only the note: the web app labels
            # each step from its own result.
            key = _call_key(spec, arguments)
            refused = ctx.deps.refused_results.get(key) if key else None
            if refused is not None:
                refused_bytes, refusal = refused
                await refuse(
                    spec,
                    env,
                    arguments,
                    refusal,
                    tool_call_id=ctx.tool_call_id,
                    result_bytes=refused_bytes,
                )
            earlier = ctx.deps.earlier_results.get(key) if key else None
            check = _result_check(ctx, spec, guard, key)
            if earlier is not None:
                if spec.risk == "write":
                    note = REPEATED_WRITE
                else:
                    note = spec.once_per_answer or REPEATED_CALL
                again = {**earlier, "repeated_call": note}
                size = _size(again)
                if check is not None and (reason := check(size)) is not None:
                    await refuse(
                        spec,
                        env,
                        arguments,
                        reason,
                        tool_call_id=ctx.tool_call_id,
                        result_bytes=size,
                    )
                _count_search(ctx, spec, again)
                return again
            try:
                result = await execute(
                    spec,
                    env,
                    arguments,
                    tool_call_id=ctx.tool_call_id,
                    check_result=check,
                )
            except ResultOverCap as exc:
                # Its text asks for a narrower call, and the look-ups go on:
                # only the same call is refused again without running.
                if key:
                    ctx.deps.refused_results[key] = (exc.size, exc.message)
                raise
            except ToolFailed as exc:
                # A first retry runs, since a service can fail for a moment;
                # after a second failure the same call is refused without
                # asking the service again. It still counts toward the run's
                # tool-call limit (``admit_call`` above).
                if key and service_failed(exc):
                    failures = ctx.deps.failed_calls.get(key, 0) + 1
                    ctx.deps.failed_calls[key] = failures
                    if failures >= SERVICE_FAILURES:
                        ctx.deps.refused_results[key] = (0, SERVICE_FAILED_TWICE)
                raise
            if spec.wire_name == ASK_TOOL:
                ctx.deps.asked = True
            if key:
                ctx.deps.earlier_results[key] = result
            _count_search(ctx, spec, result)
            return result
        except InputInvalid as exc:
            # ctx.retry / ctx.max_retries are this tool's own (FunctionToolset sets them).
            if ctx.retry >= ctx.max_retries:
                raise ToolFailed(
                    f"Gave up after {ctx.retry + 1} invalid calls. {exc.message}"
                ) from exc
            raise ModelRetry(exc.message) from exc

    tool: Tool[RunDeps] = Tool.from_schema(
        call,
        name=spec.wire_name,
        description=spec.description,
        json_schema=spec.json_schema(),
        takes_ctx=True,
        # The calls of one response run concurrently. A write, and a tool
        # that runs once per answer, runs alone, so its twin in the same
        # response finds the first result above instead of running again.
        sequential=spec.risk == "write" or spec.once_per_answer is not None,
    )
    tool.function_schema.validator = _ARGUMENTS_VALIDATOR
    return tool


def _count_search(
    ctx: "RunContext[RunDeps]", spec: ToolSpec[Any, Any], result: dict[str, Any]
) -> None:
    """Counts the answer's catalog searches in a row that found nothing
    (``FRUITLESS_SEARCHES``); a repeated search's earlier result counts again."""
    if spec.found_nothing is None:
        return
    counts = ctx.deps.fruitless_searches
    counts[ctx.run_id] = (
        counts.get(ctx.run_id, 0) + 1 if spec.found_nothing(result) else 0
    )


def _step_guard(ctx: "RunContext[RunDeps]") -> StepGuard | None:
    """The guard of the step whose call is about to run: a new one at a
    step's first call. None without a budget."""
    budget = ctx.deps.budget
    if budget is None:
        return None
    step = (ctx.run_id, ctx.run_step)
    guard = ctx.deps.step
    if guard is None or guard.step != step:
        # The messages end with the step's own response here.
        context = next_call(ctx.messages, ctx.run_id).raw
        guard = StepGuard(
            budget=budget,
            step=step,
            calls=ctx.deps.admitted_calls,
            context=context,
        )
        ctx.deps.step = guard
    return guard


def _result_check(
    ctx: "RunContext[RunDeps]",
    spec: ToolSpec[Any, Any],
    guard: StepGuard | None,
    key: str | None,
) -> Callable[[int], str | None] | None:
    """The check of a result's size against the room left for answering, for
    the tools whose result is only data the model reads: a write has already
    happened and a card or a proposal is already shown when their result is
    known. A refused result ends the run's look-ups, as the refusal tells the
    model, and the same call is refused again without running."""
    if guard is None or spec.risk != "read" or spec.wire_name in SHOWN_TOOLS:
        return None

    def check(size: int) -> str | None:
        if guard.admit_result(ctx.usage, size):
            return None
        ctx.deps.refused_run = ctx.run_id
        if key:
            ctx.deps.refused_results[key] = (size, RESULT_TOO_LARGE)
        return RESULT_TOO_LARGE

    return check


#: Where a run stands at the model call being prepared (``answer_step``).
Stage = Literal["look up", "answer or ask", "answer"]


def _silent(response: ModelResponse) -> bool:
    return not any(
        isinstance(part, ToolCallPart)
        or (isinstance(part, TextPart) and part.content.strip())
        for part in response.parts
    )


def silent_responses(messages: Sequence[ModelMessage], run_id: str | None) -> int:
    """The responses of the run ``run_id`` that held neither a tool call nor
    text beyond whitespace (``SILENT_RESPONSES``)."""
    return sum(
        isinstance(message, ModelResponse)
        and message.run_id == run_id
        and _silent(message)
        for message in messages
    )


def answer_step(ctx: "RunContext[RunDeps]") -> Stage | None:
    """Whether the call being prepared may look things up, or is the step
    that answers, with or without room for a card (``assistant.budget``).
    None without a budget. A result refused for its size has ended the run's
    look-ups (``_result_check``), and so have ``SILENT_RESPONSES`` responses
    without text or a tool call."""
    budget = ctx.deps.budget
    if budget is None:
        return None
    call = next_call(ctx.messages, ctx.run_id)
    # Every call let run counts, failed ones too (StepGuard); pydantic_ai's
    # count has only the successful ones.
    tool_calls = max(ctx.usage.tool_calls, ctx.deps.admitted_calls.get(ctx.run_id, 0))
    if (
        ctx.deps.refused_run != ctx.run_id
        and silent_responses(ctx.messages, ctx.run_id) < SILENT_RESPONSES
        and not budget.spent(ctx.usage, call, tool_calls)
    ):
        return "look up"
    if budget.can_ask(ctx.usage, call, tool_calls):
        return "answer or ask"
    return "answer"


def _size(result: dict[str, Any]) -> int:
    """A result's size in bytes, measured as ``execute`` measures it."""
    return len(json.dumps(result, separators=(",", ":"), ensure_ascii=False).encode())


async def _surface_tools(
    ctx: "RunContext[RunDeps]", tool_defs: list[ToolDefinition]
) -> list[ToolDefinition]:
    env = ctx.deps.env
    if env is None:
        return []
    # After a card the model ends its answer and waits for the user's.
    if ctx.deps.asked:
        return []
    loaded = {spec.wire_name for spec in tools_for(env.page.surface)}
    # Near the run's limits the model answers with what it has
    # (assistant.budget), or asks with a card when the user has to choose: the
    # card ends the answer, and the user's answer starts a run of its own.
    stage = answer_step(ctx)
    if stage == "answer or ask":
        loaded &= {ASK_TOOL}
    elif stage == "answer":
        loaded = set()
    return [tool_def for tool_def in tool_defs if tool_def.name in loaded]


def goat_toolset() -> "AbstractToolset[RunDeps]":
    toolset: FunctionToolset[RunDeps] = FunctionToolset(
        [_tool(spec) for spec in ALL_TOOLS], max_retries=TOOL_RETRIES
    )
    return toolset.prepared(_surface_tools)
