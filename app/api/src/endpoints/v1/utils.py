from typing import Any

import httpx
import requests
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic.networks import EmailStr
from starlette.responses import StreamingResponse

from src import schemas
from src.core.celery_app import celery_app
from src.db import models
from src.endpoints import deps
from src.utils import send_test_email

router = APIRouter()


@router.get("/reverse-proxy")
async def reverse_proxy(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    url: str = Query(..., description="URL to reverse proxy"),
) -> Response:
    """
    Reverse proxy to another server.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    if (
        url.startswith("http://localhost")
        or url.startswith("https://localhost")
        or url.startswith("localhost")
    ):
        raise HTTPException(status_code=400, detail="URL should not start with localhost")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"http://{url}"
    response = requests.get(url)
    return Response(content=response.content)


@router.post("/test-celery", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}
