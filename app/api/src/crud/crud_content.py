
from .base import CRUDBase
from src.db.models.content import Content
from src.schemas.content import ContentCreate, ContentUpdate
from sqlmodel.ext.asyncio.session import AsyncSession

class CRUDContent(CRUDBase[Content, ContentCreate, ContentUpdate]):
    pass

content = CRUDContent(Content)
