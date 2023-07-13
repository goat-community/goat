from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints.legacy import deps

router = APIRouter()


@router.get("", response_model=List[models.Role])
async def read_roles(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all roles.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    roles = await crud.role.get_multi(db)
    return roles
