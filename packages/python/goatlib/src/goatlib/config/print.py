import os

from goatlib.config.base import BaseSettingsModel

#: Where the print and thumbnail renderers reach the web app.
DEFAULT_PRINT_BASE_URL = "http://goat-web:3000"


def print_base_url() -> str:
    """Base URL of the web app the renderers load pages from.

    ``PRINT_BASE_URL`` (set on the Windmill workers), else
    ``DEFAULT_PRINT_BASE_URL``; read on every call.
    """
    return (os.environ.get("PRINT_BASE_URL") or DEFAULT_PRINT_BASE_URL).rstrip("/")


class PrintSettings(BaseSettingsModel):
    """Settings for report printing / atlas rendering."""

    atlas_max_pages: int = 120  # Maximum number of atlas pages allowed per report
    atlas_batch_size: int = (
        2  # Parallel atlas pages per batch (1 per CPU core recommended)
    )
