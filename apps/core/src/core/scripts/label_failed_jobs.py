import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from core.db.session import session_manager
from core.core.config import settings
from utils import fetch_last_run_timestamp, update_last_run_timestamp
from core.utils import print_info

SYSTEM_TASK_ID = "label_failed_jobs"
MAX_JOB_TIME = 60  # minutes


async def label_failed_jobs(async_session: AsyncSession, current_run: datetime):
    print_info("Labeling jobs that have been running for too long as failed")
    updated_jobs = await async_session.execute(
        text(
            f"""
                UPDATE customer.job
                SET status_simple = 'failed'
                WHERE '{current_run}' - created_at  > interval '60 minutes'
                AND status_simple IN ('running', 'pending')
                RETURNING id
            """
        )
    )
    updated_jobs = updated_jobs.all()
    updated_jobs = list(updated_jobs)
    await async_session.commit()

    if len(updated_jobs) > 0:
        for job in updated_jobs:
            print_info(f"Job {job[0]} has been labeled as failed.")
    else:
        print_info("No jobs to label.")


async def main():
    session_manager.init(settings.ASYNC_SQLALCHEMY_DATABASE_URI)
    async with session_manager.session() as async_session:
        # Get timestamp of last run
        system_task, last_run = await fetch_last_run_timestamp(
            async_session, SYSTEM_TASK_ID
        )
        current_run = datetime.now(timezone.utc)

        # Label jobs that were started since the last run but have not finished
        await label_failed_jobs(async_session, current_run)

        # Set last run timestamp to current time
        await update_last_run_timestamp(async_session, system_task, current_run)
    await session_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
