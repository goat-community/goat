import asyncio

import cppimport
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import sessionmaker

from src.crud import isochrone
from src.db.session import async_session
from src.endpoints.deps import get_db
from src.exts.cpp.bind import split_edges_isochrone
from src.schemas.isochrone import IsochroneSingle, IsochroneTypeEnum

isochrone_cpp = cppimport.imp("src.exts.cpp.src.isochrone")


async def get_split_network():
    single_isochrone = {
        "minutes": 20,
        "speed": 3,
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
    (
        edges_network,
        starting_id,
        distance_limits,
        obj_starting_point,
    ) = await isochrone.read_network(db, IsochroneTypeEnum.single.value, obj_in, obj_in_data)
    await db.close()
    split_length = 20

    result = split_edges_isochrone(edges_network, starting_id, distance_limits, split_length)
    return result


a = asyncio.run(get_split_network())
