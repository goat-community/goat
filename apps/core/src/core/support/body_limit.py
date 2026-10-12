"""Request-size cap for the support API, enforced before anything is spooled.

Starlette writes a multipart body to a temp file before the endpoint (or the
feature gate, or auth) runs, so a per-file check in the handler comes too
late. This pure-ASGI middleware looks at Content-Length up front and counts
bytes for chunked bodies, answering 413 once the cap is exceeded.
"""

import json

from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

DETAIL = "files_too_large"


class SupportBodyLimit:
    def __init__(self, app: ASGIApp, *, max_bytes: int, prefix: str) -> None:
        self.app = app
        self.max_bytes = max_bytes
        self.prefix = prefix.rstrip("/") + "/"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not (scope["path"] + "/").startswith(self.prefix):
            await self.app(scope, receive, send)
            return

        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None:
            try:
                too_big = int(declared) > self.max_bytes
            except ValueError:
                too_big = False  # malformed: let the server stack reject it
            if too_big:
                await self._reject(send)
                return

        total = 0

        async def counting_receive() -> Message:
            nonlocal total
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > self.max_bytes:
                    # An HTTPException survives FastAPI's body-parsing error
                    # handling and is rendered as the 413 by the router.
                    raise HTTPException(413, DETAIL)
            return message

        await self.app(scope, counting_receive, send)

    @staticmethod
    async def _reject(send: Send) -> None:
        body = json.dumps({"detail": DETAIL}).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                    (b"connection", b"close"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
