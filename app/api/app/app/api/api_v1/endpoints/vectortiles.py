from typing import Any, Dict

from fastapi import APIRouter, Depends
from fastapi.param_functions import Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from app import crud
from app.api import deps

router = APIRouter()

TILE_RESPONSE_PARAMS: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": Response,
}


@router.get("/{TileMatrixSetId}/{table}/{z}/{x}/{y}.pbf", response_model=FileResponse)
def get_tile_with_matrix():
    """
    Get a tile from the database
    """
    tile_id = crud.get_tile_id(
        table=deps.get_table_name(request.path[1:]),
        z=request.path_params["z"],
        x=request.path_params["x"],
        y=request.path_params["y"],
    )
    return crud.get_tile(tile_id)


@router.get("/{table}/{z}/{x}/{y}.pbf", response_model=FileResponse)
def get_tile():
    """
    Get a tile from the database
    """
    tile_id = crud.get_tile_id(
        table=deps.get_table_name(request.path[1:]),
        z=request.path_params["z"],
        x=request.path_params["x"],
        y=request.path_params["y"],
    )
    return crud.get_tile(tile_id)


@router.get("/{TileMatrixSetId}/{table}.json")
def get_tile_json(
    session: Session = Depends(deps.get_session),
    table: str = Body(...),
    z: int = Body(...),
    x: int = Body(...),
    y: int = Body(...),
    TileMatrixSetId: str = Body(...),
    tile_response_params: Dict[str, Any] = TILE_RESPONSE_PARAMS,
):
    """
    Get a tile from the database.
    """
    tile = crud.get_tile(
        session=session,
        table=table,
        z=z,
        x=x,
        y=y,
        TileMatrixSetId=TileMatrixSetId,
    )
    return tile, tile_response_params
