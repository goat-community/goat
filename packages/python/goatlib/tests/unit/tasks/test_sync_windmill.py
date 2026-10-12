"""Syncing a task's schedule to Windmill keeps what operators set there.

Whether a schedule runs, the arguments it runs with (a base-data mirror, a
bounding box), a pause and error handlers are set in the Windmill UI. A sync
runs on every deploy and must update the cron, not reset those. Windmill's
update replaces every field it does not receive.
"""

import json
from typing import Any

import httpx
import pytest
from goatlib.tasks.registry import TASK_REGISTRY
from goatlib.tasks.sync_windmill import WindmillTaskSyncer

SCHEDULED = next(t for t in TASK_REGISTRY if t.schedule)


def _syncer(existing: dict[str, Any] | None) -> tuple[WindmillTaskSyncer, list]:
    """A syncer against a fake Windmill holding `existing` as the schedule."""
    sent: list[tuple[str, dict[str, Any]]] = []

    def handle(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if "/schedules/get/" in path:
            if existing is None:
                return httpx.Response(404)
            return httpx.Response(200, json=existing)
        sent.append((path, json.loads(request.content)))
        return httpx.Response(200, json={})

    syncer = WindmillTaskSyncer("http://windmill.test", "token")
    syncer.client = httpx.Client(transport=httpx.MockTransport(handle))
    return syncer, sent


@pytest.mark.unit
def test_an_update_keeps_the_arguments_set_in_windmill() -> None:
    args = {"source": "s3://mirror/goat-base-data/", "bbox": [11.4, 48.0, 11.8, 48.3]}
    syncer, sent = _syncer({"args": args, "enabled": True, "schedule": "0 0 1 * * *"})

    assert syncer._create_or_update_schedule(SCHEDULED) is not None

    ((path, body),) = sent
    assert "/schedules/update/" in path
    assert body["args"] == args
    assert "enabled" not in body


@pytest.mark.unit
def test_an_update_keeps_a_pause_and_error_handling() -> None:
    kept = {
        "paused_until": "2026-11-01T00:00:00Z",
        "on_failure": "script/f/goat/notify",
        "on_failure_times": 2,
        "retry": {"constant": {"attempts": 3, "seconds": 60}},
        "no_flow_overlap": True,
        "tag": "tools",
    }
    syncer, sent = _syncer(
        {**kept, "args": {}, "enabled": True, "schedule": "0 0 1 * * *"}
    )

    syncer._create_or_update_schedule(SCHEDULED)

    ((_, body),) = sent
    assert {k: body[k] for k in kept} == kept
    assert body["schedule"] == SCHEDULED.schedule


@pytest.mark.unit
def test_an_unchanged_schedule_is_not_updated() -> None:
    syncer, sent = _syncer({"schedule": SCHEDULED.schedule, "timezone": "UTC"})

    assert syncer._create_or_update_schedule(SCHEDULED) is not None

    assert sent == []


@pytest.mark.unit
def test_a_new_schedule_starts_with_no_arguments() -> None:
    syncer, sent = _syncer(None)

    assert syncer._create_or_update_schedule(SCHEDULED) is not None

    ((path, body),) = sent
    assert "/schedules/create" in path
    assert body["args"] == {}
