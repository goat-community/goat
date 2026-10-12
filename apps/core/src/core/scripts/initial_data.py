import asyncio
import logging

import core._dotenv  # noqa: E402, F401, I001
from core.core.config import settings
from core.db.seed_default import seed_default_user_org
from core.db.seed_roles import seed_roles
from core.db.seed_templates import seed_templates
from core.db.session import session_manager
from core.db.sql.init_functions import init_functions
from core.db.sql.init_triggers import init_triggers

logger = logging.getLogger("initial_data")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def main() -> None:
    """Install/refresh DB functions, triggers and authorization seed data.

    Idempotent — safe to re-run on every deploy; changed definitions are
    re-applied. Run after `alembic upgrade head`.
    """
    logger.info("Starting initial data setup...")
    session_manager.init(settings.ASYNC_SQLALCHEMY_DATABASE_URI)
    try:
        await init_functions()
        await init_triggers()
        async with session_manager.session() as session:
            await seed_roles(session)
        if settings.AUTH is False:
            async with session_manager.session() as session:
                await seed_default_user_org(session)
            logger.info("Default user/organization ensured (AUTH disabled).")
        # Runs after the AUTH=False block above, whose default user owns the
        # starters when AUTH is off and no organization is configured.
        async with session_manager.session() as session:
            await seed_templates(session)
        logger.info("Initial data setup completed.")
    finally:
        await session_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
