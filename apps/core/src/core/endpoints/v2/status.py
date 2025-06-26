from fastapi import Body, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from core.endpoints.deps import get_db
from core.deps.auth import is_superuser
from core.db.models import Status
from core.crud.crud_status import status as crud_status

router = APIRouter()


@router.get(
    "",
    summary="Get the status of the service",
    response_model=Status,
    status_code=201,
)
async def get_status(
    *,
    async_session: AsyncSession = Depends(get_db),
):
    """
    Get the status of the service.
    """

    # Get the status
    status = await crud_status.get_all(async_session)
    return status[0]


@router.put(
    "",
    summary="Update the status of the service",
    response_model=Status,
    status_code=201,
    dependencies=[Depends(is_superuser)],
)
async def update_status(
    *,
    async_session: AsyncSession = Depends(get_db),
    obj_in: Status = Body(...),
):
    """
    Update the status of the service.
    """

    # Get the status
    status = await crud_status.get_all(async_session)
    status = status[0]

    # Update the status
    status = await crud_status.update(db=async_session, db_obj=status, obj_in=obj_in)
    return status
