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
        # Convert UploadFile to Data frame
        data_frame = geopandas.read_file(upload_file.file)
    except:
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


@router2.get("/static/{layer_id:int}")
async def get_static_layer_data(
    *,
    layer_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    static_layer = await crud.static_layer.get(db, id=layer_id)
    data_frame = geopandas.GeoDataFrame.from_postgis(
        sql=static_layer.data_frame_raw_sql(), con=legacy_engine.connect(), geom_col="geometry"
    )

    return {"data_frame": data_frame.values.tolist()}


@router2.put("/static/{layer_id:int}")
async def update_static_layer_data(
    *,
    layer_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    upload_file: UploadFile,
):
    try:
        # Convert UploadFile to Data frame
        data_frame = geopandas.read_file(upload_file.file)
    except:
        raise HTTPException(status_code=400, detail="Could not parse the uploaded file.")

    validate_data_frame(data_frame)
    convert_postgist_to_4326(data_frame)
    assert data_frame.crs.srs == "epsg:4326"

    static_layer = await crud.static_layer.get(db, id=layer_id)
    crud.static_layer.drop_postgis_table(db,static_layer.table_name)
    # Update Data Frame to Database
    data_frame.to_postgis(
        name=static_layer.table_name,
        con=legacy_engine.connect(),
        schema="extra",
        if_exists="fail",
        index=True,
    )

    return static_layer
