import uuid
from typing import Generator

from fastapi import Depends

from src.crud.crud_content import content as crud_content
from src.crud.crud_user import user as crud_user
from src.db.models.content import Content
from src.db.models.user import User
from src.db.session import AsyncSession, async_session, session_manager


async def get_db() -> Generator:
    async with async_session() as session:
        yield session


async def get_db_session() -> AsyncSession:
    async with session_manager.session() as session:
        yield session


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    user = await crud_user.get_first_user(db) or await crud_user.create(db, id=uuid.uuid4())
    return user
