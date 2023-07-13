from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.db.models.legacy.config_validation import *
from src.db.session import legacy_engine
from src.endpoints.legacy import deps
from src.schemas.data_frame import validate_data_frame
from src.utils import (
    convert_postgist_to_4326,
    generate_static_layer_table_name,
    geopandas_read_file,
)

router = APIRouter()


@router.post("/static")
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
        table_name=await crud.static_layer.uniquify_static_layer_name(
            db, file_name=upload_file.filename
        ),
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


@router.get("/static/", response_model=List[models.StaticLayer])
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


@router.get("/static/{layer_id:int}")
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


@router.put("/static/{layer_id:int}")
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


@router.delete("/static/")
async def delete_static_layer_data(
    *,
    id: List[int] = Query(default=None, gt=0),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete multiple static layers at the same time.
    """
    layer_ids = id
    for layer_id in layer_ids:
        static_layer = await crud.static_layer.get(db, id=layer_id)
        if static_layer:
            # Drop PostGIS table
            await crud.static_layer.drop_postgis_table(db, static_layer.table_name)

    # Delete Objects
    return await crud.static_layer.remove_multi(db, ids=layer_ids)
