"""Pytest configuration for Processes API tests."""

import os

# processes.config builds its settings at import and refuses AUTH on (the
# default) without a Keycloak server; this placeholder satisfies that check.
os.environ.setdefault("KEYCLOAK_SERVER_URL", "http://keycloak.test")


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _access_check_allows_everything(monkeypatch: pytest.MonkeyPatch) -> None:
    """The access check asks Postgres, which the mocked suite has not got.

    Tests of the check itself (test_access.py) replace this with their own
    answer; the SQL is tested against a real database in
    apps/core/tests/authz/test_processes_access_sql.py.
    """

    async def allow_all(user_id: object, entries: list) -> list:
        return []

    monkeypatch.setattr("processes.services.access.denied_references", allow_all)
