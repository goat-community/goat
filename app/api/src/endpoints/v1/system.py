
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints.legacy import deps
from src.schemas.system import SystemStatusModel

router = APIRouter()


@router.put("/status", response_model=SystemStatusModel)
async def status_check(
    status_in: SystemStatusModel,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    results = await crud.system.get_by_key(db, key="type", value="status")
    system = results[0]
    system.setting = status_in.dict()
    system = await crud.system.update(db, db_obj=system, obj_in=system)

    return system.setting
