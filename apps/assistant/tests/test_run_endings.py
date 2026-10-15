"""How a run ends, as the dock reads it (spec §10: run errors in the UI language)."""

import asyncio
from collections.abc import AsyncIterator, Callable
from uuid import UUID

import pytest
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelAPIError, UsageLimitExceeded
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.function import AgentInfo, FunctionModel

from assistant.agent import INSTRUCTIONS, RunDeps
from assistant.bus import InMemoryEventBus
from assistant.config import AssistantSettings
from assistant.encoding.ai_sdk import AiSdkEncoder
from assistant.events import (
    RunEnded,
    RunStarted,
    TextDelta,
    TextStarted,
    UsageReported,
    fold_parts,
    to_ui_message,
)
from assistant.llm.failures import (
    FailureKind,
    ProviderFailure,
    failure_code,
    user_message,
)
from assistant.llm.providers import OpenModels, Target
from assistant.repo import Repository
from assistant.runs.manager import RunManager
from tests.test_manager import _gated_agent

USER = UUID(int=1)


async def _conversation(repo: Repository) -> UUID:
    return UUID(
        str((await repo.create_conversation(USER, "catalog", None, None))["id"])
    )


async def _ended(repo: Repository, run_id: UUID) -> RunEnded:
    events = [event for _, event in await repo.list_events(run_id)]
    ended = events[-1]
    assert isinstance(ended, RunEnded)
    return ended


async def test_a_timed_out_run_ends_with_its_code(
    repo: Repository, settings: AssistantSettings
) -> None:
    gate = asyncio.Event()
    short = settings.model_copy(update={"run_max_seconds": 0})
    manager = RunManager(
        repo,
        InMemoryEventBus(),
        short,
        owner="a",
        agent_factory=lambda _: _gated_agent(gate),
    )
    conversation_id = await _conversation(repo)
    run_id, message_id = await manager.start_run(conversation_id, USER, "go", None)
    await manager.wait(run_id)

    ended = await _ended(repo, run_id)
    assert (ended.status, ended.code) == ("failed", "run_timeout")
    stored = [
        m
        for m in await repo.list_messages(conversation_id, exclude_message_id=None)
        if m["id"] == message_id
    ]
    assert stored[0]["parts"][-1] == {
        "type": "run_status",
        "status": "failed",
        "error": "The run took longer than allowed.",
        "code": "run_timeout",
    }


def _failing_opener(error: Exception) -> Callable[[Target], OpenModels]:
    async def stream(
        messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str]:
        raise error
        yield ""  # an async generator

    def open_(target: Target) -> OpenModels:
        model = FunctionModel(stream_function=stream)
        return OpenModels(main=model, background=model)

    return open_


async def test_a_provider_failure_ends_with_the_code_of_its_message(
    repo: Repository, settings: AssistantSettings
) -> None:
    manager = RunManager(
        repo,
        InMemoryEventBus(),
        settings,
        owner="a",
        opener=_failing_opener(ModelAPIError("test", "Connection error.")),
    )
    run_id, _ = await manager.start_run(await _conversation(repo), USER, "go", None)
    await manager.wait(run_id)
    ended = await _ended(repo, run_id)
    # The test connection is GOAT AI, not an organization's own one.
    assert (ended.status, ended.code, ended.error) == (
        "failed",
        "goat_ai_unreachable",
        "GOAT AI isn't reachable right now.",
    )


@pytest.mark.parametrize("own", [True, False])
@pytest.mark.parametrize(
    "kind", ["rejected", "blocked", "unreachable", "busy", "error"]
)
def test_every_failure_has_a_code_matching_its_message(
    kind: FailureKind, own: bool
) -> None:
    failure = ProviderFailure(kind, None, "")
    code = failure_code(failure, own=own)
    message = user_message(failure, own=own)
    if kind == "rejected":
        assert code == "ai_unavailable"
        return
    assert code.startswith("provider_" if own else "goat_ai_")
    assert message.startswith("Your organization's AI provider" if own else "GOAT AI")
    suffix = {
        "blocked": "unreachable",
        "unreachable": "unreachable",
        "busy": "busy",
        "error": "error",
    }[kind]
    assert code.endswith(suffix)


async def _failed_run(
    repo: Repository,
    settings: AssistantSettings,
    factory: Callable[[str], Agent[RunDeps, str]],
) -> RunEnded:
    manager = RunManager(
        repo, InMemoryEventBus(), settings, owner="a", agent_factory=factory
    )
    run_id, _ = await manager.start_run(await _conversation(repo), USER, "go", None)
    await manager.wait(run_id)
    return await _ended(repo, run_id)


async def test_a_usage_limit_ends_with_run_limit(
    repo: Repository, settings: AssistantSettings
) -> None:
    async def stream(
        messages: list[ModelMessage], info: AgentInfo
    ) -> AsyncIterator[str]:
        raise UsageLimitExceeded("too many requests")
        yield ""  # an async generator

    def factory(_: str) -> Agent[RunDeps, str]:
        return Agent(
            FunctionModel(stream_function=stream),
            deps_type=RunDeps,
            instructions=INSTRUCTIONS,
        )

    ended = await _failed_run(repo, settings, factory)
    assert (ended.status, ended.code) == ("failed", "run_limit")
    assert ended.error is not None
    assert ended.error.startswith("The run hit a limit: too many requests")


async def test_a_timeout_outside_the_deadline_is_an_internal_error(
    repo: Repository, settings: AssistantSettings
) -> None:
    def factory(_: str) -> Agent[RunDeps, str]:
        raise TimeoutError("upstream timed out")

    ended = await _failed_run(repo, settings, factory)
    assert (ended.status, ended.code, ended.error) == (
        "failed",
        "internal_error",
        "The assistant failed unexpectedly.",
    )


async def test_an_unexpected_exception_is_an_internal_error(
    repo: Repository, settings: AssistantSettings
) -> None:
    def factory(_: str) -> Agent[RunDeps, str]:
        raise RuntimeError("secret detail")

    ended = await _failed_run(repo, settings, factory)
    assert (ended.status, ended.code, ended.error) == (
        "failed",
        "internal_error",
        "The assistant failed unexpectedly.",
    )


@pytest.mark.parametrize(
    "ended",
    [
        RunEnded(status="failed", error="slow", code="run_timeout"),
        RunEnded(status="cancelled"),
    ],
)
def test_live_and_stored_endings_carry_the_same_data(ended: RunEnded) -> None:
    usage = UsageReported(
        model="m", provider="p", input_tokens=3, output_tokens=2, cache_read_tokens=1
    )
    events = [
        RunStarted(message_id="m1"),
        TextStarted(part_id="m1:1"),
        TextDelta(part_id="m1:1", delta="Hi"),
        usage,
        ended,
    ]
    encoder = AiSdkEncoder()
    chunks = [chunk for event in events for chunk in encoder.encode(event)]
    live_status = next(c for c in chunks if c["type"] == "data-run-status")
    live_usage = next(c for c in chunks if c["type"] == "message-metadata")

    stored = to_ui_message("m1", "assistant", fold_parts(events))
    stored_status = next(p for p in stored["parts"] if p["type"] == "data-run-status")
    assert live_status["data"] == stored_status["data"]
    assert live_usage["messageMetadata"] == stored["metadata"]
