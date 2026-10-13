"""Shared fixtures for integration tests against a real PostgreSQL catalog.

Requires a reachable PG (local compose), configured through the usual
POSTGRES_* environment variables. Tests skip when it is not reachable.
"""

import os
import uuid
from pathlib import Path
from typing import Callable, Iterator
from urllib.parse import urlparse

import duckdb
import pytest
from goatlib.storage import BaseDuckLakeManager

PG_URI = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
    f"{os.getenv('POSTGRES_SERVER', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'goat')}"
)


def _libpq() -> str:
    p = urlparse(PG_URI)
    return (
        f"host={p.hostname} port={p.port} user={p.username} "
        f"password={p.password} dbname={p.path.lstrip('/')}"
    )


def _pg_reachable() -> bool:
    try:
        con = duckdb.connect()
        con.execute("LOAD postgres")
        con.execute(f"ATTACH '{_libpq()}' AS probe (TYPE postgres, READ_ONLY)")
        con.close()
        return True
    except Exception:
        return False


class TmpSettings:
    POSTGRES_DATABASE_URI: str
    DUCKLAKE_CATALOG_SCHEMA: str
    DUCKLAKE_DATA_DIR: str | None
    DUCKLAKE_S3_ENDPOINT: str | None
    DUCKLAKE_S3_BUCKET: str | None
    DUCKLAKE_S3_ACCESS_KEY: str | None
    DUCKLAKE_S3_SECRET_KEY: str | None

    def __init__(self, schema: str, data_dir: str) -> None:
        self.POSTGRES_DATABASE_URI = PG_URI
        self.DUCKLAKE_CATALOG_SCHEMA = schema
        self.DUCKLAKE_DATA_DIR = data_dir
        self.DUCKLAKE_S3_ENDPOINT = None
        self.DUCKLAKE_S3_BUCKET = None
        self.DUCKLAKE_S3_ACCESS_KEY = None
        self.DUCKLAKE_S3_SECRET_KEY = None
        self.DATA_DIR = data_dir
        self.DUCKDB_MEMORY_LIMIT: str | None = None
        self.DUCKDB_THREADS: int | None = None


@pytest.fixture()
def lake_env(tmp_path: Path) -> Iterator[tuple[TmpSettings, BaseDuckLakeManager]]:
    """A throwaway DuckLake catalog schema with one table, plus its writer."""
    if not _pg_reachable():
        if os.getenv("CI"):
            pytest.fail("PostgreSQL not reachable; CI provides it for these tests")
        pytest.skip("PostgreSQL not reachable")
    schema = f"ducklake_test_{uuid.uuid4().hex[:8]}"
    settings = TmpSettings(schema, str(tmp_path / "data"))
    writer = BaseDuckLakeManager(read_only=False)
    writer.init(settings)
    writer.execute("CREATE TABLE lake.main.t_first AS SELECT 1 AS x")
    yield settings, writer
    try:
        writer.close()
    finally:
        con = duckdb.connect()
        con.execute("LOAD postgres")
        con.execute(f"ATTACH '{_libpq()}' AS pgadmin (TYPE postgres)")
        con.execute(
            f"CALL postgres_execute('pgadmin', 'DROP SCHEMA IF EXISTS {schema} CASCADE')"
        )
        con.close()


@pytest.fixture()
def pg_session_states() -> Iterator[Callable[[str], list[str]]]:
    """States of the server sessions carrying an application_name, one per session."""
    con = duckdb.connect()
    con.execute("LOAD postgres")
    con.execute(f"ATTACH '{_libpq()}' AS pgadmin (TYPE postgres, READ_ONLY)")

    def states(application_name: str) -> list[str]:
        rows = con.execute(
            "SELECT * FROM postgres_query('pgadmin', 'SELECT state "
            "FROM pg_stat_activity WHERE application_name = "
            f"''{application_name}''')"
        ).fetchall()
        return sorted(row[0] for row in rows)

    yield states
    con.close()
