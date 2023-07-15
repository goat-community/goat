from .base import CRUDBase
from src.db.models.layer import Layer
from .crud_content import content as crud_content
from src.schemas.layer import LayerRead


class CRUDLayer(CRUDBase):
    async def create(self, db, *, obj_in):
        content = await crud_content.create(db, obj_in=obj_in, content_type="layer")
        obj_in = Layer(**obj_in.dict())
        obj_in.content_id = content.id
        layer = await super().create(db, obj_in=obj_in)
        layer = layer.__dict__
        layer.update(content.__dict__)
        layer = LayerRead(**layer)
        return layer


layer = CRUDLayer(Layer)
