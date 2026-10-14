"""DuckLake manager instance for GeoAPI.

Creates a read-only singleton instance of BaseDuckLakeManager from goatlib.
GeoAPI only reads data - all writes happen through the core app.
"""

from goatlib.storage import BaseDuckLakeManager

from geoapi.config import settings

# Singleton instance in read-only mode
# This allows geoapi and core to run concurrently without lock conflicts
ducklake_manager = BaseDuckLakeManager(
    read_only=True,
    pin_snapshot=settings.DUCKLAKE_PIN_SNAPSHOT,
    refresh_interval=settings.DUCKLAKE_SNAPSHOT_REFRESH_SECONDS,
    application_name="goat-geoapi-ducklake",
)
