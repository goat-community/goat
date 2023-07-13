from src.schemas.layer import request_examples, LayerCreate, LayerRead
from src.db.models.layer import Layer
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from src.crud.crud_layer import layer as crud_layer
from pydantic import ValidationError
from src.endpoints.deps import create_content, get_db
from src.db.models.content import Content
from src.db.session import AsyncSession

router = APIRouter()


@router.post("", response_model=LayerRead, status_code=201)
async def create_layer(
    async_session: AsyncSession = Depends(get_db),
    content: Content = Depends(create_content),
    *,
    layer_in: LayerCreate = Body(..., examples=request_examples["create"]),
):
    layer = Layer(**layer_in.dict())
    layer.content_id = str(content.id)
    layer = await crud_layer.create(async_session, obj_in=layer)
    return layer
