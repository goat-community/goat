import asyncio
import time

from fastapi.encoders import jsonable_encoder

from src import crud
from src.core.config import settings
from src.crud import isochrone as crud_isochrone
from src.db.session import async_session
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneStartingPointCoord,
    IsochroneTypeEnum,
    request_examples,
)


async def get_sample_network(speed=5, minutes=10):
    obj_in = IsochroneDTO(**request_examples["isochrone"]["single_walking_default"]["value"])
    obj_in.settings.travel_time = minutes
    obj_in.settings.speed = speed
    db = async_session()
    read_network_start = time.time()
    if len(obj_in.starting_point.input) == 1 and isinstance(
        obj_in.starting_point.input[0], IsochroneStartingPointCoord
    ):
        isochrone_type = IsochroneTypeEnum.single.value
    else:
        isochrone_type = IsochroneTypeEnum.multi.value
    superuser = await crud.user.get_by_key(db, key="email", value=settings.FIRST_SUPERUSER_EMAIL)
    network, starting_ids = await crud_isochrone.read_network(
        db, obj_in, superuser[0], isochrone_type
    )

    read_network_stop = time.time()
    print("Read network took ", (read_network_stop - read_network_start), " seconds.")
    # asyncio.run(db.close())

    return network, starting_ids
