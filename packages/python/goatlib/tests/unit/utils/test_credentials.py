"""`postgres_attach_target` keeps the password out of the connection string
DuckDB gets; `redact_credentials` removes credentials from text."""

import duckdb
import pytest
from goatlib.utils.credentials import (
    postgres_attach_target,
    redact_credentials,
    without_password,
)


@pytest.mark.parametrize(
    ("dsn", "target", "password"),
    [
        # DuckDB merges its Postgres secret into a libpq string only, so a
        # URI that loses its password becomes one.
        (
            "postgresql://goat:pw@db:5432/goat",
            "host=db port=5432 user=goat dbname=goat",
            "pw",
        ),
        (
            "postgres://goat:p%40ss%3A@db/goat?sslmode=disable&application_name=a b",
            "host=db user=goat dbname=goat sslmode=disable application_name='a b'",
            "p@ss:",
        ),
        (
            "host=db port=5432 user=goat password=pw dbname=goat",
            "host=db port=5432 user=goat dbname=goat",
            "pw",
        ),
        ("host=db password='a b\\'c' dbname=goat", "host=db dbname=goat", "a b'c"),
        ("host=db user=goat dbname=goat", "host=db user=goat dbname=goat", None),
        ("postgresql://goat@db/goat", "postgresql://goat@db/goat", None),
    ],
)
def test_the_password_comes_out_of_a_connection_string(
    dsn: str, target: str, password: str | None
) -> None:
    assert without_password(dsn) == (target, password)


@pytest.fixture
def con() -> duckdb.DuckDBPyConnection:
    connection = duckdb.connect()
    try:
        connection.execute("INSTALL postgres")
        connection.execute("LOAD postgres")
    except duckdb.Error:
        pytest.skip("DuckDB's postgres extension is not available")
    return connection


@pytest.mark.parametrize(
    "dsn",
    [
        "host=127.0.0.1 port=1 user=goat password='S3cr3t\\'pw' dbname=goat",
        "postgresql://goat:S3cr3t%27pw@127.0.0.1:1/goat?application_name=goat-tools",
        # A value libpq needs quoted stays inside the ATTACH's string literal.
        "postgresql://goat:S3cr3t%27pw@127.0.0.1:1/goat?application_name=a%20b",
    ],
)
def test_the_attach_string_carries_no_password(
    con: duckdb.DuckDBPyConnection, dsn: str
) -> None:
    target = postgres_attach_target(con, dsn)

    with pytest.raises(duckdb.Error) as failed:
        con.execute(f"ATTACH '{target}' AS pg (TYPE postgres)")

    # libpq read the string and tried the port: the password was not needed
    # to parse it, and DuckDB merged its secret in.
    assert 'connection to server at "127.0.0.1", port 1 failed' in str(failed.value)
    assert "S3cr3t" not in str(failed.value)


def test_the_password_waits_in_the_connections_postgres_secret(
    con: duckdb.DuckDBPyConnection,
) -> None:
    postgres_attach_target(con, "postgresql://goat:pw@db/goat")
    postgres_attach_target(con, "postgresql://goat:pw@db/goat")

    secrets = con.execute(
        "SELECT count(*) FROM duckdb_secrets() WHERE type = 'postgres'"
    ).fetchone()
    assert secrets == (1,)


def test_any_password_goes_into_the_secret(con: duckdb.DuckDBPyConnection) -> None:
    postgres_attach_target(con, "postgresql://goat:a%00b%27c%5Cd@db/goat")

    secrets = con.execute(
        "SELECT count(*) FROM duckdb_secrets() WHERE type = 'postgres'"
    ).fetchone()
    assert secrets == (1,)


def test_a_connection_string_without_a_password_creates_no_secret(
    con: duckdb.DuckDBPyConnection,
) -> None:
    assert postgres_attach_target(con, "host=db dbname=goat") == "host=db dbname=goat"

    secrets = con.execute(
        "SELECT count(*) FROM duckdb_secrets() WHERE type = 'postgres'"
    ).fetchone()
    assert secrets == (0,)


def test_credentials_are_removed_from_a_connection_error() -> None:
    message = (
        "IO Error: Failed to get table information from DuckLake: Unable to "
        'connect to Postgres at "postgresql://goat:hunter2@db:5432/goat": '
        "connection to server failed: Connection refused"
    )

    redacted = redact_credentials(message)

    assert "hunter2" not in redacted
    assert '"postgresql://goat:***@db:5432/goat"' in redacted
    assert "Connection refused" in redacted


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            'at "host=db user=goat password=hunter2 dbname=goat": refused',
            'at "host=db user=goat password=*** dbname=goat": refused',
        ),
        ("password='a b' dbname=goat", "password=*** dbname=goat"),
        ("PASSWORD = hunter2", "PASSWORD = ***"),
        (
            "POSTGRES_PASSWORD=hunter2 PGPASSWORD=hunter2",
            "POSTGRES_PASSWORD=*** PGPASSWORD=***",
        ),
        ("{'password': 'hunter2'}", "{'password': ***}"),
        ('{"password": "hunter2"}', '{"password": ***}'),
        (
            "SECRET (TYPE postgres, PASSWORD 'hunter2')",
            "SECRET (TYPE postgres, PASSWORD ***)",
        ),
        ("postgresql://:hunter2@db/goat", "postgresql://:***@db/goat"),
        (
            "postgres://u:p@h/db and postgres://v:q@h/db",
            "postgres://u:***@h/db and postgres://v:***@h/db",
        ),
        (
            "Buffer: the distance must be positive.",
            "Buffer: the distance must be positive.",
        ),
    ],
)
def test_every_form_of_a_password_in_text_is_redacted(text: str, expected: str) -> None:
    assert redact_credentials(text) == expected
