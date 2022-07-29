from typing import List

import geopandas
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.db.models.config_validation import *
from src.db.session import legacy_engine
from src.endpoints import deps
from src.schemas.data_frame import validate_data_frame
from src.utils import (
    convert_postgist_to_4326,
    delete_file,
    generate_static_layer_table_name,
    geopandas_read_file,
    return_geojson_or_geobuf,
)

router = APIRouter()


@router.get("/static/{layer_name}")
async def static_vector_layer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    layer_name: str,
    return_type: str,
):
    """Return selected layers in different vector formats"""
    layer_to_return = await crud.layer.static_vector_layer(
        db, current_user, layer_name, return_type
    )
    return return_geojson_or_geobuf(layer_to_return, return_type)


router2 = APIRouter()


@router2.post("/static")
async def upload_static_layer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    upload_file: UploadFile,
):

    try:
        data_frame = geopandas_read_file(upload_file)
    except HTTPException as e:
        # It's HTTP exception, so raise it to the endpoint.
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Could not parse the uploaded file.")

    validate_data_frame(data_frame)
    convert_postgist_to_4326(data_frame)
    assert data_frame.crs.srs == "epsg:4326"

    static_layer = models.StaticLayer(
        user_id=current_user.id,
        table_name=generate_static_layer_table_name(prefix=upload_file.filename),
    )

    # Save Data Frame to Database
    data_frame.to_postgis(
        name=static_layer.table_name,
        con=legacy_engine.connect(),
        schema="extra",
        if_exists="fail",
        index=True,
    )
    # Create Static Layer DB Object
    static_layer = await crud.static_layer.create(db, obj_in=static_layer)
    return static_layer


@router2.get("/static/", response_model=List[models.StaticLayer])
async def list_static_layers(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    static_layers = await crud.static_layer.get_multi(db, skip=skip, limit=limit)
    if not static_layers:
        raise HTTPException(status_code=404, detail="there is no (more) static layers.")
    return static_layers


@router2.get("/static/{layer_id:int}")
async def get_static_layer_data(
    *,
    layer_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    static_layer = await crud.static_layer.get(db, id=layer_id)
    if not static_layer:
        raise HTTPException(status_code=404, detail="static layer not found.")

    return static_layer


@router2.put("/static/{layer_id:int}")
async def update_static_layer_data(
    *,
    layer_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    upload_file: UploadFile,
):

    static_layer = await crud.static_layer.get(db, id=layer_id)
    if not static_layer:
        raise HTTPException(status_code=404, detail="static layer not found.")

    try:
        data_frame = geopandas_read_file(upload_file)
    except HTTPException as e:
        # It's HTTP exception, so raise it to the endpoint.
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Could not parse the uploaded file.")

    validate_data_frame(data_frame)
    convert_postgist_to_4326(data_frame)
    assert data_frame.crs.srs == "epsg:4326"

    # Drop previous PostGIS table
    await crud.static_layer.drop_postgis_table(db, static_layer.table_name)
    static_layer.table_name = generate_static_layer_table_name(prefix=upload_file.filename)
    await crud.static_layer.update(db, db_obj=static_layer, obj_in=static_layer)
    # Create PostGIS table
    data_frame.to_postgis(
        name=static_layer.table_name,
        con=legacy_engine.connect(),
        schema="extra",
        if_exists="fail",
        index=True,
    )

    return static_layer


@router2.delete("/static/{layer_id:int}")
async def update_static_layer_data(
    *,
    layer_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    static_layer = await crud.static_layer.get(db, id=layer_id)
    if not static_layer:
        raise HTTPException(status_code=404, detail="static layer not found.")
    # Drop PostGIS table
    await crud.static_layer.drop_postgis_table(db, static_layer.table_name)
    # Delte Object
    static_layer = await crud.static_layer.remove(db, id=static_layer.id)
    return static_layer
