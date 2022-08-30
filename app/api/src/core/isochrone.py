import asyncio
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
    """
    Check and update extent
    :param extent: Extent
    :param coord: Coordinate
    """
    if coord[0] < extent[0]:
        extent[0] = coord[0]

    if coord[1] < extent[1]:
        extent[1] = coord[1]

    if coord[0] > extent[2]:
        extent[2] = coord[0]

    if coord[1] > extent[3]:
        extent[3] = coord[1]


def remap_edges(edge_source, edge_target, edge_geom):
    """
    Remap edges to start from 0
    :param edge_source: List of source nodes
    :param edge_target: List of target nodes
    :param edge_geom: List of edge geometries
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
            if len(edge_geom[i]) > 2:
                # loop from first element to one before last
                for coord in edge_geom[i][0:-1]:
                    check_extent(extent, coord)
            else:
                check_extent(extent, edge_geom[i][0])
            id += 1
        else:
            edge_source[i] = unordered_map.get(edge_source[i])
        # target
        if unordered_map.get(edge_target[i]) is None:
            unordered_map[edge_target[i]] = id
            edge_target[i] = id
            node_coords[id] = edge_geom[i][-1]
            if len(edge_geom[i]) > 2:
                for coord in edge_geom[i][1:]:
                    check_extent(extent, coord)
            else:
                check_extent(extent, edge_geom[i][-1])
            id += 1
        else:
            edge_target[i] = unordered_map.get(edge_target[i])

    return unordered_map, node_coords, extent


def split_edges(edge_source, edge_target, edge_length, edge_geom, agg_costs, split_distance):
    """
    Split edges into multiple edges
    :param edge_source: List of source nodes
    :param edge_target: List of target nodes
    :param edge_length: List of edge lengths
    :param edge_geom: List of edge geometries
    :param agg_costs: List of aggregated costs from dijkstra algorithm
    :param split_distance: Distance to split edges in meters
    :return: List of interpolated coordinates and costs along the line every x meters, including vertices
    """
    coords = []
    costs = []
    for i in range(len(edge_source)):
        source_id = edge_source[i]
        target_id = edge_target[i]
        source_cost = agg_costs[source_id]
        target_cost = agg_costs[target_id]
        length_m = edge_length[i]
        geom = edge_geom[i]
        if np.inf not in [source_cost, target_cost]:
            if length_m > split_distance or len(geom) > 2:
                # split edge into multiple edges
                previous_agg = source_cost
                for idx, coord in enumerate(geom[:-1]):
                    # find distance between current and next point
                    next_coord = geom[idx + 1]
                    dist_m = math.sqrt(
                        (coord[0] - next_coord[0]) ** 2 + ((coord[1] - next_coord[1])) ** 2
                    )
                    n_splits = math.floor(dist_m / split_distance)
                    for n in range(1, n_splits + 1):
                        distance_to_next = n * split_distance
                        x = coord[0] - ((distance_to_next * (coord[0] - next_coord[0])) / dist_m)
                        y = coord[1] - ((distance_to_next * (coord[1] - next_coord[1])) / dist_m)
                        coords.append([x, y])
                        cost = previous_agg + (distance_to_next / length_m) * (
                            target_cost - source_cost
                        )
                        costs.append(cost)
                    # if next point is vertex, add it and update previous
                    if idx + 1 <= len(geom) - 2:
                        coords.append(geom[idx + 1])
                        cost = source_cost + (dist_m / length_m) * (target_cost - source_cost)
                        costs.append(cost)
                        previous_agg = cost

    return coords, costs


def web_mercator_to_pixel(x, y, zoom):
    """
    Convert web mercator to pixel coordinates
    :param x: Web mercator x coordinate
    :param y: Web mercator y coordinate
    :param zoom: Zoom level
    :return: Pixel coordinates
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


@njit
def construct_adjacency_list_(n, edge_source, edge_target, edge_cost, edge_reverse_cost):
    """
    Construct adjacency list from edges
    :param n: Number of nodes
    :param edge_source: List of edge source nodes
    :param edge_target: List of edge target nodes
    :param edge_cost: List of edge costs
    :param edge_reverse_cost: List of edge reverse costs
    :return: Adjacency list
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


def dijkstra_(start_vertices, adj_list, travel_time):
    """
    Dijkstra's algorithm one-to-all shortest path search
    :param start_vertices: List of start vertices
    :param adj_list: Adjacency list
    :param travel_time: Travel time matrix
    :return: List of shortest paths and costs
    """
    n = len(adj_list)
    distances = [np.Inf for _ in range(n)]
    # loop over all start vertices
    for start_vertex in start_vertices:
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


def get_single_depth_grid_(zoom, west, north, data):
    """
    Get single depth grid
    :param zoom: Zoom level
    :param west: West coordinate
    :param north: North coordinate
    :param data: Data to be gridded
    :return: Gridded data
    """
    grid_data = {}
    Z = np.ravel(data)
    Z = np.ceil(Z)
    Z = np.nan_to_num(Z, nan=np.iinfo(np.intc).max, posinf=np.iinfo(np.intc).max)
    grid_data["version"] = 0
    grid_data["zoom"] = zoom
    grid_data["west"] = west
    grid_data["north"] = north
    grid_data["width"] = data.shape[1]
    grid_data["height"] = data.shape[0]
    grid_data["depth"] = 1
    grid_data["data"] = Z
    return grid_data


def build_grid_interpolate_(points, costs, extent, step_x, step_y):
    """
    Build grid interpolate
    :param points: List of points
    :param costs: List of costs
    :param extent: Extent of the grid
    :param step_x: Step size in x direction
    :param step_y: Step size in y direction
    :return: Grid interpolate
    """
    X = np.arange(start=extent[0], stop=extent[2], step=step_x)
    Y = np.arange(start=extent[1], stop=extent[3], step=step_y)
    X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation
    interpolate_function = LinearNDInterpolator(points, costs)

    Z = interpolate_function(X, Y)
    plt.figure().clear()
    plt.pcolormesh(X, Y, Z, shading="auto")
    plt.legend()
    plt.colorbar()
    plt.axis("equal")
    plt.savefig("isochrone.png")
    return np.flip(Z, 0)


def compute_isochrone(edge_network, start_vertices, travel_time, zoom: int = 10):
    """
    Compute isochrone for a given start vertices

    :param edge_network: Edge Network DataFrame
    :param start_vertices: List of start vertices
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
    edges_length = np.array(edge_network["length"])
    unordered_map, node_coords, extent = remap_edges(edges_source, edges_target, edges_geom)

    # add buffer of 200 meters to extent
    extent[0] -= 200
    extent[1] -= 200
    extent[2] += 200
    extent[3] += 200

    # construct adjacency list
    adj_list = construct_adjacency_list_(
        len(unordered_map), edges_source, edges_target, edges_cost, edges_reverse_cost
    )

    # run dijkstra
    start_vertices_ids = np.array([unordered_map[v] for v in start_vertices])
    distances = dijkstra_(start_vertices_ids, adj_list, travel_time)

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

    # split edges based on resolution
    interpolated_coords = []
    interpolated_costs = []
    interpolated_coords, interpolated_costs = split_edges(
        edges_source,
        edges_target,
        edges_length,
        edges_geom,
        distances,
        min([web_mercator_x_step, web_mercator_y_step]),
    )

    # build grid
    Z = build_grid_interpolate_(
        list(node_coords.values()) + interpolated_coords,
        distances + interpolated_costs,
        extent,
        step_x=web_mercator_x_step,
        step_y=web_mercator_y_step,
    )

    # build grid data (single depth)
    grid_data = get_single_depth_grid_(zoom, xy_bottom_left[0], xy_top_right[1], Z)
    return grid_data


async def main():
    edges_network, starting_ids, obj_in = await get_sample_network(minutes=5)
    grid_data = compute_isochrone(
        edges_network,
        starting_ids,
        travel_time=5,
        zoom=12,
    )
    print()


if __name__ == "__main__":
    from src.tests.utils.isochrone import get_sample_network

    asyncio.run(main())
