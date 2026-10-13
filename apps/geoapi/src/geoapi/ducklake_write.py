"""Write-capable DuckLake manager instance for GeoAPI.

Creates a read-write singleton instance of BaseDuckLakeManager from goatlib.
Used exclusively for mutation endpoints (feature CRUD, column management).
The existing read-only manager continues serving reads without contention.

DuckDB's single-writer constraint is handled by BaseDuckLakeManager's
internal threading.Lock, which serializes all write operations.

The connection is created lazily on first use rather than at startup. Every
DuckLake connection loads the full catalog file-set into native memory, so a
pod that only ever serves reads should not pay for a write connection it never
touches. Most geoapi traffic is read-only, so this drops the steady-state
connection count per pod.
"""

import threading
from contextlib import contextmanager
from typing import Generator

import duckdb
from goatlib.storage import BaseDuckLakeManager


class LazyDuckLakeWriteManager(BaseDuckLakeManager):
    """Write manager that defers connection creation until first use."""

    def __init__(self) -> None:
        super().__init__(read_only=False, application_name="goat-geoapi-ducklake")
        self._lazy_init_lock = threading.Lock()

    def _ensure_initialized(self) -> None:
        """Create the connection on first use (thread-safe, idempotent)."""
        if self._connection is not None:
            return
        with self._lazy_init_lock:
            if self._connection is not None:
                return
            # Imported here to avoid a config import at module load time.
            from geoapi.config import settings

            self.init(settings)

    @contextmanager
    def connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """Get the write connection, initializing it on first access."""
        self._ensure_initialized()
        with BaseDuckLakeManager.connection(self) as con:
            yield con


# Singleton instance in read-write mode (connection created on first write)
ducklake_write_manager = LazyDuckLakeWriteManager()
