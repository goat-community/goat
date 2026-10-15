"""The Pydantic AI adapter of the tool layer (spec §3: one definition, two
adapters; the MCP adapter is ``assistant.mcp_server``).

Every tool is registered once with its input model's JSON schema; validation,
the data policy and the audit happen in ``execute``. A filter keeps the tools of
the run's surface, in registry order. A run without a tool environment (the run
machinery's own tests) is offered none.
"""

import json
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError
from pydantic_ai import RunContext, Tool
from pydantic_ai.exceptions import ModelRetry, ToolFailed
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import AbstractToolset, FunctionToolset
from pydantic_core import SchemaValidator, core_schema

from assistant.history import SHOWN_TOOLS
from assistant.tools.registry import ALL_TOOLS, tools_for
from assistant.tools.runtime import InputInvalid, ToolSpec, execute

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


def _as_arguments(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {_NOT_AN_OBJECT: True}


_ARGUMENTS_VALIDATOR = SchemaValidator(
    core_schema.no_info_plain_validator_function(_as_arguments)
)


def _call_key(spec: ToolSpec[Any, Any], arguments: dict[str, Any]) -> str | None:
    """The same for two calls of a read tool that ask the same, defaults
    included; None for a tool whose every call counts (a proposal, a card) and
    for arguments that do not validate (``execute`` says why)."""
    if spec.risk != "read" or spec.wire_name in SHOWN_TOOLS:
        return None
    try:
        validated = spec.input_model.model_validate(arguments)
    except ValidationError:
        return None
    canonical = json.dumps(validated.model_dump(mode="json"), sort_keys=True)
    return f"{spec.wire_name} {canonical}"


def _tool(spec: ToolSpec[Any, Any]) -> "Tool[RunDeps]":
    # ``ctx`` is positional-only: a model-chosen argument named "ctx" must reach
    # ``execute`` as an argument, not collide with the context parameter.
    async def call(ctx: "RunContext[RunDeps]", /, **arguments: Any) -> dict[str, Any]:
        env = ctx.deps.env
        if env is None:  # filtered out below; kept as a guard
            raise ModelRetry("This tool is not available here.")
        try:
            if _NOT_AN_OBJECT in arguments:
                raise InputInvalid("The arguments must be a JSON object.")
            # The whole result again, not only the note: the web app labels
            # each step from its own result.
            key = _call_key(spec, arguments)
            earlier = ctx.deps.earlier_results.get(key) if key else None
            if earlier is not None:
                return {**earlier, "repeated_call": REPEATED_CALL}
            result = await execute(spec, env, arguments, tool_call_id=ctx.tool_call_id)
            if key:
                ctx.deps.earlier_results[key] = result
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
    )
    tool.function_schema.validator = _ARGUMENTS_VALIDATOR
    return tool


async def _surface_tools(
    ctx: "RunContext[RunDeps]", tool_defs: list[ToolDefinition]
) -> list[ToolDefinition]:
    env = ctx.deps.env
    if env is None:
        return []
    # Near the run's limits the model answers with what it has (assistant.budget).
    budget = ctx.deps.budget
    if budget is not None and budget.spent(ctx.usage):
        return []
    loaded = {spec.wire_name for spec in tools_for(env.page.surface)}
    return [tool_def for tool_def in tool_defs if tool_def.name in loaded]


def goat_toolset() -> "AbstractToolset[RunDeps]":
    toolset: FunctionToolset[RunDeps] = FunctionToolset(
        [_tool(spec) for spec in ALL_TOOLS], max_retries=TOOL_RETRIES
    )
    return toolset.prepared(_surface_tools)
