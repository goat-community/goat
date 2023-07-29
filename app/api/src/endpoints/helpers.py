from src.schemas.layer import get_layer_class
from pydantic import BaseModel, Field
from sqlalchemy import select
from src.db.session import sync_session
from src.db.models.layer import Layer


class LayerUpdateHelper(BaseModel):
    def __new__(cls, *args, **kwargs):
        db = sync_session()
        layer = db.execute(select(Layer).where(Layer.content_id == kwargs["id"])).scalar_one()
        layer_update_class = get_layer_class("update", **layer.__dict__)
        return layer_update_class(**kwargs)
