from src.schemas.isochrone import IsochroneMultiCountPois
from src.db.session import AsyncSession
from src import crud
from src.schemas.isochrone import isochrone_poi_count_limit


class POIExceededException(ValueError):
    pass


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


def get_poi_limit_for_speed(speed):
    for limitation in isochrone_poi_count_limit:
        if speed <= limitation["speed_limit"]:
            return limitation["poi_count_limit"]
    return 0


async def validate_poi_limit_multi_isochrone(
    isochrone_in: IsochroneMultiCountPois, db: AsyncSession
):
    poi_count = await crud.isochrone.count_opportunity(db=db, obj_in=isochrone_in)
    poi_limit = get_poi_limit_for_speed(isochrone_in.speed)

    if poi_count > poi_limit:
        raise POIExceededException(
            f"Exceeded POI limit for this speed and POI count. Number of POIs: {poi_count}. POI count limit for this speed: {poi_limit}"
        )
