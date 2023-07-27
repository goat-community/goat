from .base import CRUDBase
from src.db.models.content import Content


class CRUDContent(CRUDBase):
    async def create(self, db, *, obj_in, content_type):
        content = Content(**obj_in.dict())
        content.content_type = content_type
        content = await super().create(db, obj_in=content)
        return content


content = CRUDContent(Content)
