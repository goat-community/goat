import geopandas

from src import crud
from src.db import models
from src.db.session import legacy_engine
from src.utils import generate_static_layer_table_name


async def create_static_layer(db):
    data_frame = geopandas.read_file("/app/src/tests/data/sample.zip")
    users = await crud.user.get_all(db)
    static_layer = models.StaticLayer(
        user_id=users[0].id, table_name=generate_static_layer_table_name(prefix="sample.zip")
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
