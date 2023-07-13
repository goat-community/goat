from typing import Generator
from src.db.session import async_session
from src.db.models.content import Content
from src.crud.crud_user import user as crud_user
from src.crud.crud_content import content as crud_content
import uuid
from fastapi import Depends
from src.db.session import AsyncSession


async def get_db() -> Generator:
    async with async_session() as session:
        yield session


async def create_content(db: AsyncSession = Depends(get_db)) -> Content:
    user = await crud_user.get_first_user(db) or await crud_user.create(db, id=uuid.uuid4())

    content = Content(
        content_type="layer",
        name="test",
        user_id=str(user.id),
    )
    content = await crud_content.create(db, obj_in=content)
    return content
