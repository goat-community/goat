"""End-to-end pinned-read behavior against a real PostgreSQL catalog.

Requires a reachable PG (local compose). Creates a throwaway metadata schema
and drops it afterwards. Run explicitly with:
    uv run pytest tests/integration/test_pinned_reads_pg.py -m integration -v
"""

from typing import Any

import pytest
from goatlib.storage import BaseDuckLakeManager, DuckLakePool

pytestmark = pytest.mark.integration


def test_pool_pin_immune_and_miss_refresh(
    lake_env: tuple[Any, BaseDuckLakeManager],
) -> None:
    settings, writer = lake_env
    pool = DuckLakePool(pool_size=1, pin_snapshot=True, refresh_interval=999.0)
    pool.init(settings)
    try:
        assert pool.execute_with_retry(
            "SELECT count(*) FROM lake.main.t_first", fetch_all=False
        ) == (1,)

        writer.execute("CREATE TABLE lake.main.t_second AS SELECT 2 AS x")

        # pinned: still serves t_first without paying a reload, cannot see t_second
        assert pool.execute_with_retry(
            "SELECT count(*) FROM lake.main.t_first", fetch_all=False
        ) == (1,)

        # miss on the new table triggers force-refresh + retry and succeeds
        assert pool.execute_with_retry(
            "SELECT count(*) FROM lake.main.t_second", fetch_all=False
        ) == (1,)
    finally:
        pool.close()


def test_manager_pin_poll_advances(
    lake_env: tuple[Any, BaseDuckLakeManager],
) -> None:
    settings, writer = lake_env
    mgr = BaseDuckLakeManager(read_only=True, pin_snapshot=True, refresh_interval=0.5)
    mgr.init(settings)
    try:
        writer.execute("CREATE TABLE lake.main.t_polled AS SELECT 3 AS x")
        import time

        deadline = time.monotonic() + 10.0
        seen = False
        while time.monotonic() < deadline:
            try:
                if mgr.execute_one("SELECT count(*) FROM lake.main.t_polled") == (1,):
                    seen = True
                    break
            except Exception:
                pass
            time.sleep(0.5)
        assert seen, "poll did not pick up the new snapshot within 10s"
    finally:
        mgr.close()
