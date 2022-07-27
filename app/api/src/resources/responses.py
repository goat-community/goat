"""responses: Response models."""

import json
from typing import Any

from fastapi import Response
from starlette.responses import JSONResponse


class JSONIndented(JSONResponse):
    """Default JSON response with indentation."""

    def render(self, content: Any) -> bytes:
        """Render response."""
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(",", ":"),
        ).encode("utf-8")


class OctetStreamResponse(Response):
    media_type = "application/octet-stream"
