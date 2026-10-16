"""A failed workflow step's error text carries neither usernames nor
credentials."""

from goatlib.tools.workflow_runner import _sanitize_error_msg


def test_a_step_error_carries_no_credentials() -> None:
    error = (
        "IO Error: Unable to connect to Postgres at "
        '"postgresql://goat:hunter2@db:5432/goat": connection refused'
    )

    text = _sanitize_error_msg(error)

    assert "hunter2" not in text
    assert "connection refused" in text


def test_a_cancellation_does_not_name_who_cancelled() -> None:
    assert _sanitize_error_msg("Job cancelled by admin@example.com") == "Job cancelled"
