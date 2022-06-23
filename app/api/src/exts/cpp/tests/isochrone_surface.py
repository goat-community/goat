import asyncio
import time

import cppimport
import matplotlib.pyplot as plt
import numpy as np
from fastapi.encoders import jsonable_encoder
from scipy.interpolate import NearestNDInterpolator

from src.crud import isochrone
from src.db.session import async_session
from src.exts.cpp.bind import split_edges_isochrone
from src.schemas.isochrone import IsochroneSingle, IsochroneTypeEnum

isochrone_cpp = cppimport.imp("src.exts.cpp.src.isochrone")


async def get_split_network():
    single_isochrone = {
        "minutes": 20,
        "speed": 5,
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
    (
        edges_network,
        starting_id,
        distance_limits,
        obj_starting_point,
    ) = await isochrone.read_network(db, IsochroneTypeEnum.single.value, obj_in, obj_in_data)
    read_network_stop = time.time()
    print("Read network took ", (read_network_stop - read_network_start), " seconds.")
    await db.close()

    split_length = 20

    result = split_edges_isochrone(edges_network, starting_id, distance_limits, split_length)

    return result


async def interpolate():
    start = time.time()
    a = await get_split_network()
    X = np.arange(start=int(a.boundry.min_x), stop=int(a.boundry.max_x), step=20)
    Y = np.arange(start=int(a.boundry.min_y), stop=int(a.boundry.max_y), step=20)
    X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation
    points = np.array(a.points)
    transposed = points.transpose()
    x = transposed[0]
    y = transposed[1]
    z = np.array(a.costs)
    interpolate_start = time.time()
    interpolate_function = NearestNDInterpolator(list(zip(x, y)), z)
    Z = interpolate_function(X, Y)
    interpolate_stop = time.time()
    print("Inter polate time is ", (interpolate_stop - interpolate_start), " seconds.")
    end = time.time()
    print("Took ", (end - start), " seconds.")
    plt.pcolormesh(X, Y, Z, shading="nearest")
    # plt.plot(x, y, "ok", label="input point")
    plt.legend()
    plt.colorbar()
    plt.axis("equal")
    plt.savefig("NearestNDInterpolate.png")
    return Z, a.boundry


# interpolate()


def encode_costs():

    grid_type = "ACCESSGR"
    grid_type_binary = str.encode(grid_type)
    z, boundry = asyncio.run(interpolate())
    version = 1
    zoom = 10
    west = boundry.min_x
    north = boundry.max_y
    width = z.shape[0]
    height = z.shape[1]
    nsamples = 1
    array = np.array([version, zoom, west, north, width, height, nsamples], dtype=np.int32)
    header_bin = array.tobytes()
    scaled_z = z * 100000
    z_1d = np.ravel(scaled_z)
    z_1d_byte = z_1d.astype(np.int32)
    z_diff = np.diff(z_1d_byte, prepend=z_1d[0])
    with open("costs.bin", "wb") as binary_out:
        binary_out.write(grid_type_binary)
        binary_out.write(header_bin)
        binary_out.write(z_diff)

    print(array)


encode_costs()
