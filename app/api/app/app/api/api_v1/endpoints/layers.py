from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse, StreamingResponse

from app import crud
from app.api import deps
from app.schemas.msg import Msg
from app.schemas.table_metadata import TableMetadata

router = APIRouter()
