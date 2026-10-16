"""A failed job's message carries no credentials, whatever its error text
held (`goatlib.utils.credentials.redact_credentials`)."""

from typing import Any

from processes.routers.processes import _windmill_job_to_status_info

BASE = "http://processes.test"
ERROR = (
    "IO Error: Failed to get table information from DuckLake: Unable to connect "
    'to Postgres at "postgresql://goat:hunter2@db:5432/goat": connection '
    "to server failed: Connection refused"
)


def _failed(script_path: str, result: dict[str, Any], success: bool) -> dict:
    return {
        "id": "01a0538a-d853-19e5-e97f-cfdd4d119e10",
        "script_path": script_path,
        "created_at": "2026-01-01T00:00:00Z",
        "success": success,
        "result": result,
    }


def test_a_failed_tool_jobs_message_carries_no_credentials() -> None:
    job = _failed(
        "f/goat/tools/join",
        {"error": {"name": "IOException", "message": ERROR}},
        success=False,
    )

    info = _windmill_job_to_status_info(job, BASE)

    assert info.status == "failed"
    assert "hunter2" not in (info.message or "")
    assert "Connection refused" in (info.message or "")


def test_a_failed_workflow_steps_message_carries_no_credentials() -> None:
    job = _failed(
        "f/goat/tools/workflow_runner",
        {
            "status": "partial",
            "errors": [
                {
                    "node_id": "tool-1",
                    "error": {"name": "IOException", "message": ERROR},
                }
            ],
        },
        success=True,
    )

    info = _windmill_job_to_status_info(job, BASE)

    assert info.status == "failed"
    assert "hunter2" not in (info.message or "")


async def test_the_results_of_a_failed_job_carry_no_credentials(monkeypatch) -> None:
    from uuid import UUID

    import pytest
    from fastapi import HTTPException

    from processes.routers import processes as router

    user = UUID("00000000-0000-0000-0000-000000000001")
    job = _failed(
        "f/goat/tools/join",
        {"error": {"name": "IOException", "message": ERROR}},
        success=False,
    )
    job["args"] = {"user_id": str(user)}

    async def get_job_status(job_id: str) -> dict:
        return job

    monkeypatch.setattr(router.windmill_client, "get_job_status", get_job_status)

    with pytest.raises(HTTPException) as failed:
        await router.get_job_results(None, job["id"], user_id=user)  # type: ignore[arg-type]

    assert failed.value.status_code == 500
    assert "hunter2" not in str(failed.value.detail)
