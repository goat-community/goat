from typing import Any, List
from sqlmodel.ext.asyncio.session import AsyncSession
from .base import CRUDBase
from src.schemas.content import ContentUpdate
from src.db.models.layer import Layer
from src.db.models.content import Content
from .crud_content import content as crud_content


from sqlalchemy import select


class CRUDLayer(CRUDBase):
    async def get_layer(self, *, db: AsyncSession | None = None, id) -> Layer | None:
        db = db or super().get_db().session
        query = select(Layer).where(Layer.content_id == str(id))
        response = await db.execute(query)
        layer = response.scalar_one_or_none()
        return layer
    
    async def create_layer(self, *, layer_in: dict, content_id: str, db: AsyncSession | None = None) -> Layer:
        db = db or super().get_db().session
        new_layer = Layer(**layer_in)
        new_layer.content_id = content_id
        layer = await super().create(obj_in=new_layer)
        return layer
    
    async def update_content_layer(self, *, current_layer: Layer, layer_in: dict, db: AsyncSession | None = None) -> Layer | None:
        db = db or super().get_db().session

        content_raw = { "content_type": "layer", **layer_in}
        current_content = await crud_content.get(id=current_layer.content_id)
        await crud_content.update(db_obj=current_content, obj_in=ContentUpdate.parse_obj(content_raw))



layer = CRUDLayer(Layer)
