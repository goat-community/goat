from fastapi import APIRouter, Body, Depends

from src.crud.crud_layer import layer as crud_layer
from src.db.models.content import Content
from src.db.models.layer import Layer
from src.db.models.user import User
from src.db.session import AsyncSession
from src.endpoints.deps import get_current_user, get_db
from src.schemas.layer import LayerCreate, LayerRead, request_examples

router = APIRouter()


@router.post("", response_model=LayerRead, status_code=201)
async def create_layer(
    async_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    *,
    layer_in: LayerCreate = Body(..., examples=request_examples["create"]),
):
    layer_in.user_id = current_user.id
    layer = await crud_layer.create(async_session, obj_in=layer_in)
    return layer
