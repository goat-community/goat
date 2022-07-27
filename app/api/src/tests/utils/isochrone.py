import asyncio
import time

from fastapi.encoders import jsonable_encoder

from src.crud import isochrone as crud_isochrone
from src.db.session import async_session
from src.schemas.isochrone import IsochroneSingle, IsochroneTypeEnum


def get_sample_network(speed=5, minutes=10):
    single_isochrone = {
        "minutes": minutes,
        "speed": speed,
        "n": 2,
        "modus": "default",
        "x": 11.5696284,
        "y": 48.1502132,
        "routing_profile": "walking_standard",
        "scenario_id": 0,
        "user_id": 119,
    }
    obj_in = IsochroneSingle(**single_isochrone)
    obj_in_data = jsonable_encoder(obj_in)

    db = async_session()
    read_network_start = time.time()
    (edges_network, starting_id, distance_limits, obj_starting_point,) = asyncio.run(
        crud_isochrone.read_network(db, IsochroneTypeEnum.single.value, obj_in, obj_in_data)
    )
    read_network_stop = time.time()
    print("Read network took ", (read_network_stop - read_network_start), " seconds.")
    # asyncio.run(db.close())

    return edges_network, starting_id, distance_limits
