from .base import CRUDBase
from src.db.models.content import Content
from sqlmodel.ext.asyncio.session import AsyncSession

class CRUDContent(CRUDBase):
    async def create(self, db, *, obj_in, content_type):
        content = Content(**obj_in.dict())
        content.content_type = content_type
        content = await super().create(db, obj_in=content)
        return content

    async def create_content(self, *, obj_in, content_type, user_id: str, db: AsyncSession | None = None) -> Content:
        db = db or self.db.session
        content = Content(**obj_in.dict())
        content.user_id = user_id
        content.content_type = content_type
        content = await super().create(obj_in = content)
        return content

content = CRUDContent(Content)
