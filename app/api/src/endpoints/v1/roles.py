from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps

router = APIRouter()


@router.get("/", response_model=List[models.Role])
async def read_roles(db: AsyncSession = Depends(deps.get_db)) -> Any:
    """
    Retrieve all roles.
    """
    roles = await crud.role.get_multi(db)
    return roles
