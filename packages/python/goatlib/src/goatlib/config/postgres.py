"""How goatlib reaches Postgres: session names, DuckLake's catalog endpoint and
what a transaction pooler needs.

Operators see which part of GOAT holds a connection by its application_name.
"""

import os
from collections.abc import Callable
from typing import Any

# Analytics tools and workflows, run as Windmill jobs.
TOOLS_APPLICATION_NAME = "goat-tools"
# Scheduled maintenance and housekeeping tasks.
TASKS_APPLICATION_NAME = "goat-tasks"
# The one-shot bootstrap that creates the DuckLake catalog.
DUCKLAKE_INIT_APPLICATION_NAME = "goat-ducklake-init"


def ducklake_postgres_endpoint(
    postgres_server: str,
    postgres_port: str | int,
    ducklake_server: str | None = None,
    ducklake_port: str | int | None = None,
) -> tuple[str, int]:
    """Host and port of DuckLake's catalog connections.

    They stay open for as long as an attach lives, so behind a transaction
    pooler they go to the database itself: `ducklake_server` and
    `ducklake_port` (DUCKLAKE_POSTGRES_SERVER / DUCKLAKE_POSTGRES_PORT) when
    set, otherwise the app's own `postgres_server` and `postgres_port`.
    """
    return ducklake_server or postgres_server, int(ducklake_port or postgres_port)


# TCP keepalives a long-lived connection asks the server for, as startup
# parameters.
KEEPALIVE_SERVER_SETTINGS = {
    "tcp_keepalives_idle": "30",
    "tcp_keepalives_interval": "5",
    "tcp_keepalives_count": "5",
}


def parse_transaction_pooler(value: object) -> bool:
    """A POSTGRES_TRANSACTION_POOLER value: "true", "1", "yes", "on" in any
    case and spacing; anything else, empty included, is off. The services'
    settings parse it this way too, so no spelling stops one from starting."""
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in ("1", "true", "yes", "on")


def transaction_pooler_enabled(
    getenv: Callable[[str, str], str | None] = os.getenv,
) -> bool:
    """POSTGRES_TRANSACTION_POOLER: POSTGRES_SERVER is a pooler in transaction mode."""
    return parse_transaction_pooler(getenv("POSTGRES_TRANSACTION_POOLER", ""))


def asyncpg_connect_args(
    application_name: str, transaction_pooler: bool, keepalives: bool = False
) -> dict[str, Any]:
    """`server_settings` and statement cache for asyncpg.connect / create_pool.

    Behind a pooler in transaction mode each query may run on another server
    connection, and a pooler with stock settings neither keeps track of
    prepared statements nor passes on startup parameters it doesn't know. So
    there asyncpg caches no prepared statements and sends no keepalive
    settings.
    """
    server_settings = {"application_name": application_name}
    if keepalives and not transaction_pooler:
        server_settings.update(KEEPALIVE_SERVER_SETTINGS)
    args: dict[str, Any] = {"server_settings": server_settings}
    if transaction_pooler:
        args["statement_cache_size"] = 0
    return args
