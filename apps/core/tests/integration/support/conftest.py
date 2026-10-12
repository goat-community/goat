"""These tests talk to the staging Odoo only: no database, no app.

The root conftest has two autouse fixtures that build a Postgres test schema
for the whole session; override them with no-ops so this directory never needs
a database (and keeps working when none is running).

They write: tickets and contacts on the staging Odoo, which notify the team
there. So an Odoo key in the local .env is not enough to start them; they run
only when asked for with ODOO_INTEGRATION_TESTS=1.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def opt_in() -> None:
    if os.environ.get("ODOO_INTEGRATION_TESTS") != "1":
        pytest.skip("writes to the staging Odoo: set ODOO_INTEGRATION_TESTS=1 to run")


@pytest.fixture(scope="session", autouse=True)
def session_fixture() -> None:
    return None


@pytest.fixture(autouse=True)
def session_override() -> None:
    return None
