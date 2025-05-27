from core.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models.system_task import SystemTask
from datetime import datetime, timedelta, timezone


async def fetch_last_run_timestamp(async_session: AsyncSession, system_task_id: str):
    """Fetch the last run timestamp of the thumbnail update task."""

    result = await CRUDBase(SystemTask).get(async_session, system_task_id)
    return result, (
        result.last_run
        if result is not None
        else datetime.now(timezone.utc) - timedelta(minutes=5)
    )


async def update_last_run_timestamp(
    async_session: AsyncSession,
    system_task: SystemTask,
    new_timestamp: datetime,
):
    """Update the last run timestamp of the thumbnail update task."""

    await CRUDBase(SystemTask).update(
        db=async_session,
        db_obj=system_task,
        obj_in={"last_run": new_timestamp},
    )
