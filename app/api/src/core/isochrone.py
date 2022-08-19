import heapq
import math

import matplotlib.pyplot as plt
import numpy as np
import pyproj
from numba import njit
from numba.typed import List
from scipy.interpolate import LinearNDInterpolator
from shapely.geometry import Point
from shapely.ops import transform

from src.utils import coordinate_to_pixel


def check_extent(extent, coord):
    if coord[0] < extent[0]:
        extent[0] = coord[0]

    if coord[1] < extent[1]:
        extent[1] = coord[1]

    if coord[0] > extent[2]:
        extent[2] = coord[0]

    if coord[1] > extent[3]:
        extent[3] = coord[1]


def remap_edges_(edge_source, edge_target, edge_geom):
    """
    Remap edges to start from 0
    """
    unordered_map = {}
    node_coords = {}
    id = 0
    extent = [np.inf, np.inf, -np.inf, -np.inf]  # [min_x, min_y, max_x, max_y]
    for i in range(len(edge_source)):
        # source
        if unordered_map.get(edge_source[i]) is None:
            unordered_map[edge_source[i]] = id
            edge_source[i] = id
            node_coords[id] = edge_geom[i][0]
            check_extent(extent, edge_geom[i][0])
            id += 1
        else:
            edge_source[i] = unordered_map.get(edge_source[i])
        # target
        if unordered_map.get(edge_target[i]) is None:
            unordered_map[edge_target[i]] = id
            edge_target[i] = id
            node_coords[id] = edge_geom[i][-1]
            check_extent(extent, edge_geom[i][0])
            id += 1
        else:
            edge_target[i] = unordered_map.get(edge_target[i])
    return unordered_map, node_coords, extent


def web_mercator_to_pixel(x, y, zoom):
    """
    Convert web mercator to pixel coordinates
    """
    project = pyproj.Transformer.from_crs(
        pyproj.CRS("EPSG:3857"), pyproj.CRS("EPSG:4326"), always_xy=True
    ).transform
    point = Point(x, y)
    lon_lat_point = transform(project, point)
    point_pixel = coordinate_to_pixel([lon_lat_point.x, lon_lat_point.y], zoom=zoom)
    x_ = math.floor(point_pixel["x"])
    y_ = math.floor(point_pixel["y"])
    return [x_, y_]


def get_single_depth_grid_(zoom, west, north, data):
    grid_data = {}
    Z = np.ravel(data)
    Z = np.ceil(Z)
    Z = np.nan_to_num(Z, nan=np.iinfo(np.intc).max, posinf=np.iinfo(np.intc).max)
    grid_data["version"] = 0
    grid_data["zoom"] = zoom
    grid_data["west"] = west
    grid_data["north"] = north
    grid_data["width"] = data.shape[0]
    grid_data["height"] = data.shape[1]
    grid_data["depth"] = 1
    grid_data["data"] = Z
    return grid_data


@njit
def construct_adjacency_list_(n, edge_source, edge_target, edge_cost, edge_reverse_cost):
    """
    Construct adjacency list from edges
    """
    adj_list = List([List([List([-1.001, -1.001])])] * n)
    for i in range(len(edge_source)):
        if edge_cost[i] >= 0.0:
            if adj_list[edge_source[i]][0][0] == -1.001:
                adj_list[edge_source[i]] = List([List([edge_target[i], edge_cost[i]])])
            else:
                adj_list[edge_source[i]].append(List([edge_target[i], edge_cost[i]]))
        if edge_reverse_cost[i] >= 0.0:
            if adj_list[edge_target[i]][0][0] == -1.001:
                adj_list[edge_target[i]] = List([List([edge_source[i], edge_reverse_cost[i]])])
            else:
                adj_list[edge_target[i]].append(List([edge_source[i], edge_reverse_cost[i]]))
    return adj_list


@njit
def dijkstra_(start_vertex, adj_list, travel_time):
    """
    Dijkstra's algorithm one-to-all shortest path search
    """
    n = len(adj_list)
    distances = [np.Inf for _ in range(n)]
    distances[start_vertex] = 0.0
    visited = [False for _ in range(n)]
    # set up priority queue
    pq = [(0.0, start_vertex)]
    while len(pq) > 0:
        if pq[0][0] >= travel_time:
            break
        # get the root, discard current distance (!!!distances in the data are in seconds)
        _, u = heapq.heappop(pq)
        # if the node is visited, skip
        if visited[u]:
            continue
        # set the node to visited
        visited[u] = True
        # check the distance and node and distance
        for v, l in adj_list[u]:
            v = int(v)
            l = l / 60.0  # convert cost to minutes
            # if the current node's distance + distance to the node we're visiting
            # is less than the distance of the node we're visiting on file
            # replace that distance and push the node we're visiting into the priority queue
            if distances[u] + l < distances[v]:
                distances[v] = distances[u] + l
                heapq.heappush(pq, (distances[v], v))
    return distances


def build_grid_interpolate_(points, costs, extent, step_x, step_y):
    X = np.arange(start=extent[0], stop=extent[2], step=step_x)
    Y = np.arange(start=extent[1], stop=extent[3], step=step_y)
    X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation
    interpolate_function = LinearNDInterpolator(list(points), costs)

    Z = interpolate_function(X, Y)
    plt.figure().clear()
    plt.pcolormesh(X, Y, Z, shading="auto")
    plt.legend()
    plt.colorbar()
    plt.axis("equal")
    plt.savefig("isochrone.png")
    return np.array(Z)


def compute_isochrone(edge_network, start_vertexes, travel_time, zoom: int = 10):
    """
    Compute isochrone for a given start vertexes

    :param edge_network: Edge Network DataFrame
    :param start_vertexes: List of start vertexes
    :param travel_time: Travel time in minutes
    :return: R5 Grid
    """
    edge_network = edge_network.iloc[1:, :]  # TODO: Fix this
    edge_network.astype(
        {
            "id": np.int64,
            "source": np.int64,
            "target": np.int64,
            "cost": np.double,
            "reverse_cost": np.double,
            "length": np.double,
        }
    )
    # remap edges
    edges_source = edge_network["source"].to_numpy()
    edges_target = edge_network["target"].to_numpy()
    edges_cost = edge_network["cost"].to_numpy()
    edges_reverse_cost = edge_network["reverse_cost"].to_numpy()
    edges_geom = np.array(edge_network["geom"])
    unordered_map, node_coords, extent = remap_edges_(edges_source, edges_target, edges_geom)

    # construct adjacency list
    adj_list = construct_adjacency_list_(
        len(unordered_map), edges_source, edges_target, edges_cost, edges_reverse_cost
    )

    # run dijkstra
    distances = dijkstra_(
        unordered_map[start_vertexes[0]], adj_list, travel_time
    )  # TODO: Fix starting point

    # minx, miny, maxx, maxy
    web_mercator_x_distance = extent[2] - extent[0]
    web_mercator_y_distance = extent[3] - extent[1]

    # get corners in pixel
    # Pixel coordinates origin is at the top left corner of the image. (y of top right/left corner is smaller than y of bottom right/left corner)
    xy_bottom_left = web_mercator_to_pixel(extent[0], extent[1], zoom=zoom)
    xy_top_right = web_mercator_to_pixel(extent[2], extent[3], zoom=zoom)

    # pixel x, y distances
    pixel_x_distance = xy_top_right[0] - xy_bottom_left[0]
    pixel_y_distance = xy_bottom_left[1] - xy_top_right[1]

    # calculate step in web mercator size
    web_mercator_x_step = web_mercator_x_distance / pixel_x_distance
    web_mercator_y_step = web_mercator_y_distance / pixel_y_distance

    # build grid
    Z = build_grid_interpolate_(
        node_coords.values(),
        distances,
        extent,
        step_x=web_mercator_x_step,
        step_y=web_mercator_y_step,
    )

    # build grid data (single depth)
    grid_data = get_single_depth_grid_(zoom, xy_bottom_left[0], xy_top_right[1], Z)
    return grid_data


if __name__ == "__main__":
    from src.tests.utils.isochrone import get_sample_network

    edges_network, starting_id, distance_limits = get_sample_network(minutes=2)

    grid_data = compute_isochrone(edges_network, starting_id, travel_time=2, zoom=10)
    print()
