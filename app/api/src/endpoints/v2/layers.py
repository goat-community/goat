from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import UUID4
from src.db.models.layer import Layer
from fastapi_pagination import Params, Page, paginate
from src.crud.crud_layer import layer as crud_layer
from src.crud.crud_user import user as crud_user
from src.crud.crud_content import content as crud_content
from src.db.models.user import User
from src.endpoints.deps import get_current_user
from src.schemas.layer import LayerRead, request_examples_update, request_examples
from src.endpoints.helpers import LayerUpdateHelper
from typing import Annotated
from src.schemas.content import ContentCreate

from src.schemas.response import (
    IPaginatedResponse
)

router = APIRouter()

########################Create########################

@router.get("")
async def get_layer_list(
    params: Params = Depends(),
) -> IPaginatedResponse[LayerRead]:
    """
    Gets a paginated list of layers
    """
    layers = await crud_layer.get_multi_paginated(params=params)
    return layers

@router.post("/create_layer")
async def create_layer(
    current_user: User = Depends(get_current_user),
    layer_in: Annotated[dict, Body(..., examples=request_examples["create"])] = None
 ) -> LayerRead: 
   
    data_raw = { "user_id": current_user.id, "content_type": "layer", **layer_in}
    content_raw = ContentCreate.parse_obj(data_raw)
    content = await crud_content.create(obj_in=content_raw)
    new_layer = await crud_layer.create_layer(layer_in=layer_in, content_id=content.id)

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
    layer_in: Annotated[dict, Body(..., examples=request_examples_update["update"])] = None 
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
