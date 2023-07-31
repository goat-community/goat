from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import UUID4
from src.db.models.layer import Layer

from src.crud.crud_layer import layer as crud_layer
from src.crud.crud_user import user as crud_user
from src.crud.crud_content import content as crud_content
from src.db.models.user import User
from src.db.session import AsyncSession
from src.endpoints.deps import get_current_user, get_db
from src.schemas.layer import request_examples
from src.schemas.layer_v2 import LayerRead, request_examples_allient
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

########################Get########################
@router.get("/get_layer/{layer_id}")
async def get_layer(
    layer_id: Annotated[UUID4, Path(title="The ID of the layer to get")],
) -> LayerRead:

    layer = await crud_layer.get_layer(id=layer_id)
    return layer

########################Update########################

@router.put("/update_layer/{layer_id}")
async def update_layer(
    layer_id: Annotated[UUID4, Path(title="The ID of the layer to get")],
    layer_in: Annotated[dict, Body(..., examples=request_examples_allient["update"])] = None 
) -> LayerRead:
    
    updated_user = await crud_user.get(id=str(layer_in["user_id"]))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User does not exist") 

    current_layer = await crud_layer.get_layer(id=str(layer_id))
    if not current_layer:
        raise HTTPException(status_code=404, detail="Layer not found")
        
    
    await crud_layer.update_content_layer(current_layer=current_layer, layer_in=layer_in)
    layer_updated = await crud_layer.update(db_obj=current_layer, obj_in=Layer(**layer_in))

    return layer_updated




@router.delete("/delete_layer/{layer_id}")
async def delete_layer(
    layer_id: Annotated[UUID4, Path(title="The ID of the layer to get")],
) -> LayerRead:
    current_layer = await crud_layer.get_layer(id=str(layer_id))

    if not current_layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    layer = await crud_layer.remove(id=str(layer_id))

    return layer
