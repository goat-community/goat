from fastapi import APIRouter, Body, Depends, Path
from pydantic import UUID4

from src.crud.crud_layer import layer as crud_layer
from src.crud.crud_content import content as crud_content
from src.db.models.content import Content
from src.db.models.layer import Layer
from src.db.models.user import User
from src.db.session import AsyncSession
from src.endpoints.deps import get_current_user, get_db
from src.schemas.layer import LayerCreate, request_examples, LayerRead2
from src.schemas.layer_v2 import LayerRead
from src.endpoints.helpers import LayerUpdateHelper
from typing import Annotated
from src.schemas.content import ContentCreate

router = APIRouter()


@router.get("/by_id/{layer_id}", response_model=LayerRead)
async def read_layer(
    async_session: AsyncSession = Depends(get_db), 
    layer_id: UUID4 = None,
):
    layer = await crud_layer.get(async_session, id=layer_id)
    return layer


@router.get("", response_model=list[LayerRead])
async def read_layers(
    async_session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    ordering: str = None,
    q: str = None,
):
    layers = await crud_layer.get_multi(
        async_session,
        skip=skip,
        limit=limit,
        ordering=ordering,
        query=q,
    )
    return layers


@router.put("/", response_model=LayerRead)
async def update_layer(
    async_session: AsyncSession = Depends(get_db),
    layer_in: LayerUpdateHelper = Body(..., examples=request_examples["update"]),
):
    db_obj = await crud_layer.get(async_session, id=str(layer_in.content_id))
    layer = await crud_layer.update(async_session, db_obj=db_obj, obj_in=layer_in)
    return layer


@router.get("/get_example")
async def read_layer_allient() -> LayerRead2:
    content_id = UUID4('06b0ca35-c041-479a-a1ee-1cf6bbc81be2')
    layer = await crud_layer.get_layer(id=content_id)
    return layer


@router.get("/get_example2")
async def read_layer_allient() -> LayerRead:
    content_id = UUID4('06b0ca35-c041-479a-a1ee-1cf6bbc81be2')
    layer = await crud_layer.get_layer(id=content_id)

    layer_dict = layer.__dict__
    layer_dict.update(layer.content.__dict__)

    return layer_dict


########################Create########################


@router.post("/create_layer")
async def create_layer(
    current_user: User = Depends(get_current_user),
    layer_in: Annotated[dict, Body(..., examples=request_examples["create"])] = None
 ) -> LayerRead: 
   
    data_raw = { "user_id": current_user.id, "content_type": "layer", **layer_in}
    content_raw = ContentCreate.parse_obj(data_raw)
    content = await crud_content.create(obj_in=content_raw)
    new_layer = await crud_layer.create_layer(layer_in=layer_in, content_id=content.id)

    print('layer', new_layer)
    return new_layer


@router.get("/get_layer/{layer_id}")
async def get_layer(
    layer_id: Annotated[UUID4, Path(title="The ID of the layer to get")],
) -> LayerRead:

    layer = await crud_layer.get_layer(id=layer_id)
    return layer



