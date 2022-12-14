import asyncio
import heapq
import json
import math
from time import time

import numpy as np
from numba import int64, njit, uint, vectorize
from numba.experimental import jitclass
from numba.pycc import CC
from numba.typed import List
from scipy.interpolate import LinearNDInterpolator

from src.utils import (
    coordinate_to_pixel,
    web_mercator_x_to_pixel_x,
    web_mercator_y_to_pixel_y,
)

# cc = CC("isochrone")
# cc.verbose = True


# @cc.export(
#     "construct_adjacency_list_",
#     ListType(ListType(ListType(float64)))(
#         int64,
#         Array(int64, 1, "C"),
#         Array(int64, 1, "C"),
#         Array(float64, 1, "C"),
#         Array(float64, 1, "C"),
#     ),
# )
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


# @cc.export(
#     "dijkstra_", float64[:](Array(int64, 1, "C"), ListType(ListType(ListType(float64))), int64)
# )
@njit
def dijkstra_(start_vertices, adj_list, travel_time):
    """
    Dijkstra's algorithm one-to-all shortest path search
    :param start_vertices: List of start vertices
    :param adj_list: Adjacency list
    :param travel_time: Travel time matrix
    :return: List of shortest paths and costs
    """
    n = len(adj_list)
    # distances = [np.Inf for _ in range(n)]
    distances = np.full(n, np.Inf, np.double)
    # loop over all start vertices
    for start_vertex in start_vertices:
        distances[start_vertex] = 0.0
        # visited = [False for _ in range(n)]
        visited = np.full(n, False, np.bool8)
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


spec = [
    ("pointer", int64),  # a simple scalar field
    ("unordered_map", int64[:, :]),  # an array field
    ("reverced_map", int64[:, :]),  # an array field
]


@jitclass(spec)
class UnorderedMap:
    def __init__(self, map_size) -> None:
        self.pointer = 0
        self.unordered_map = np.empty((map_size, 2), np.int64)

    def set(self, first, second):
        if self.get(first) is None:
            self.unordered_map[self.pointer] = (first, second)
            self.pointer += 1
            # self.sort()

    def get(self, first):
        return self.search_sorted(first)

    def get_by_list(self, v):
        unordered_map_t = self.unordered_map.transpose()
        search = np.searchsorted(unordered_map_t[0, 0 : self.pointer], v)
        values = self.unordered_map[0 : self.pointer, 1]
        return values[search]

    def sort(self):
        i = 1
        while i < self.pointer:
            x = self.unordered_map[i].copy()
            j = i - 1
            while j >= 0 and self.unordered_map[j][0] > x[0]:
                self.unordered_map[j + 1] = self.unordered_map[j]
                j = j - 1
            self.unordered_map[j + 1] = x
            i = i + 1

    def search_sorted(self, first):
        for i in range(self.pointer):
            if first == self.unordered_map[i][0]:
                return self.unordered_map[i][1]
            # elif first < self.unordered_map[i][0]:
            #     return None
        return None

    @property
    def len(self):
        return self.pointer


@njit
def array_equals(vertex, array):
    pointer = 0
    found = np.empty(100, np.int64)
    for i, value in enumerate(array):
        if value == vertex:
            found[pointer] = i
            pointer += 1
    return found[:pointer]


@njit
def get_adj_list(vertex, edge_source, edge_target):
    forward_adjacency = array_equals(vertex, edge_source)
    backward_adjacency = array_equals(vertex, edge_target)
    return forward_adjacency, backward_adjacency


@njit
def get_adj_count(edge_source, edge_target):
    concat = np.concatenate((edge_source, edge_target))
    unique = np.unique(concat)
    return len(unique)


@njit
def dijkstra2(
    start_vertices,
    edges_source,
    edges_target,
    edges_cost,
    edges_reverse_cost,
    travel_time,
):
    """
    Dijkstra's algorithm one-to-all shortest path search
    :param start_vertices: List of start vertices
    :param adj_list: Adjacency list
    :param travel_time: Travel time matrix
    :return: List of shortest paths and costs
    """
    n = get_adj_count(edges_source, edges_target)
    # distances = [np.Inf for _ in range(n)]
    distances = np.full(n, np.Inf, np.double)
    # loop over all start vertices
    for start_vertex in start_vertices:
        distances[start_vertex] = 0.0
        # visited = [False for _ in range(n)]
        visited = np.full(n, False, np.bool8)
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

            forward_adj, reversed_adj = get_adj_list(u, edges_source, edges_target)
            for adj_id in forward_adj:
                v = edges_target[adj_id]
                l = edges_cost[adj_id] / 60.0  # convert cost to minutes
                # if the current node's distance + distance to the node we're visiting
                # is less than the distance of the node we're visiting on file
                # replace that distance and push the node we're visiting into the priority queue
                if distances[u] + l < distances[v]:
                    distances[v] = distances[u] + l
                    heapq.heappush(pq, (distances[v], v))

            for adj_id in reversed_adj:
                v = edges_source[adj_id]
                l = edges_reverse_cost[adj_id] / 60.0  # convert cost to minutes
                # if the current node's distance + distance to the node we're visiting
                # is less than the distance of the node we're visiting on file
                # replace that distance and push the node we're visiting into the priority queue
                if distances[u] + l < distances[v]:
                    distances[v] = distances[u] + l
                    heapq.heappush(pq, (distances[v], v))
    return distances


@njit
def filter_nodes(node_coords_list, node_costs_list, zoom, width, west, north):
    """
    Filter out nodes that fall inside the same pixel (keep the one with the lowest cost)
    :param node_coords_list: List of node coordinates
    :param node_costs_list: List of node costs
    :param zoom: Zoom level
    :param width: Width of the grid
    :param west: West coordinate of the grid
    :param north: North coordinate of the grid
    :return: List of filtered nodes and costs
    """
    index_cost = {}
    for idx, node_coord in enumerate(node_coords_list):
        node_coord_pixel = [
            round(web_mercator_x_to_pixel_x(node_coord[0], zoom)),
            round(web_mercator_y_to_pixel_y(node_coord[1], zoom)),
        ]
        pixel_x = node_coord_pixel[0]
        pixel_y = node_coord_pixel[1]
        x = pixel_x - west
        y = pixel_y - north
        index = y * width + x
        if node_costs_list[idx] != np.inf and (
            index not in index_cost or node_costs_list[idx] < index_cost[index]
        ):
            index_cost[index] = idx
    node_coords_list = [node_coords_list[idx] for idx in index_cost.values()]
    node_costs_list = [node_costs_list[idx] for idx in index_cost.values()]
    return node_coords_list, node_costs_list


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


def get_extent(geom_array):
    extent = np.empty((2, 2), np.double)  # [min_x, min_y, max_x, max_y]
    geom_array.min(0, extent[0])
    geom_array.max(0, extent[1])
    return extent.flat


@njit
def remap_edges(edge_source, edge_target, geom_address, geom_array):
    """
    Remap edges to start from 0
    :param edge_source: List of source nodes
    :param edge_target: List of target nodes
    :param edge_geom: List of edge geometries
    """
    # start_time = time()
    unordered_map = UnorderedMap(len(edge_source))
    node_coords = np.empty((len(edge_source), 2), np.double)
    id = 0
    for i in range(len(edge_source)):
        edge_geom = geom_array[geom_address[i] : geom_address[i + 1], :]
        # source
        if unordered_map.get(edge_source[i]) is None:
            unordered_map.set(edge_source[i], id)
            edge_source[i] = id
            node_coords[id] = edge_geom[0]
            id += 1
        else:
            edge_source[i] = unordered_map.get(edge_source[i])
        # target
        if unordered_map.get(edge_target[i]) is None:
            unordered_map.set(edge_target[i], id)
            edge_target[i] = id
            node_coords[id] = edge_geom[-1]
            id += 1
        else:
            edge_target[i] = unordered_map.get(edge_target[i])

    # end_time = time()
    # print(f"Remap edges time: {end_time - start_time}s")
    return unordered_map, node_coords[: unordered_map.len]


@njit
def estimate_split_edges_size(edge_length, geom_array, split_distance):
    full_edge_length = np.sum(edge_length)
    number_of_geoms = len(geom_array) - 2 * len(edge_length)
    minimum_size = full_edge_length / split_distance + 1
    maximum_size = minimum_size + number_of_geoms
    return int(maximum_size)


@njit
def split_edges(
    edge_source, edge_target, edge_length, geom_address, geom_array, agg_costs, split_distance
):
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
    # start_time = time()
    est_size = estimate_split_edges_size(edge_length, geom_array, split_distance)
    coords = np.empty((est_size, 2), np.double)
    costs = np.empty(est_size, np.double)

    counter = -1
    for i in range(len(edge_source)):
        source_id = edge_source[i]
        target_id = edge_target[i]
        source_cost = agg_costs[source_id]
        target_cost = agg_costs[target_id]
        total_length = edge_length[i]
        geom = geom_array[geom_address[i] : geom_address[i + 1], :]
        if np.inf not in [source_cost, target_cost]:
            if total_length > split_distance or len(geom) > 2:
                # split edge into multiple edges
                previous_agg_dist = 0.0
                for idx, coord in enumerate(geom[:-1]):
                    # find distance between current and next point
                    next_coord = geom[idx + 1]
                    dist = math.sqrt(
                        (coord[0] - next_coord[0]) ** 2 + ((coord[1] - next_coord[1])) ** 2
                    )
                    agg_dist = previous_agg_dist + dist

                    n_splits = math.floor(dist / split_distance)
                    for n in range(1, n_splits + 1):
                        counter += 1
                        distance_to_next = n * split_distance
                        x = coord[0] - ((distance_to_next * (coord[0] - next_coord[0])) / dist)
                        y = coord[1] - ((distance_to_next * (coord[1] - next_coord[1])) / dist)
                        coords[counter] = [x, y]
                        cost = source_cost + (
                            (previous_agg_dist + distance_to_next) / total_length
                        ) * (target_cost - source_cost)
                        costs[counter] = cost
                    # if next point is vertex, add it and update previous
                    if idx + 1 <= len(geom) - 2:
                        counter += 1
                        coords[counter] = geom[idx + 1]
                        cost = source_cost + (agg_dist / total_length) * (
                            target_cost - source_cost
                        )
                        costs[counter] = cost
                        previous_agg_dist = agg_dist

    print(f"estimated size: {est_size}, calculated size: {counter}")
    # end_time = time()
    # print(f"Split Edges time: {end_time - start_time}s")

    return coords[:counter, :], costs[:counter]


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
    Z = np.rint(Z)
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


def get_geom_array(edges_geom):
    geom_count = np.empty(len(edges_geom) + 1, dtype=np.intc)
    geom_count[0] = 0
    address = 1
    for geom in edges_geom:
        geom_count[address] = len(geom)
        address += 1

    all_geom_count = np.sum(geom_count)
    geom_array = np.empty([all_geom_count, 2], dtype=np.double)
    address = 0
    for geom in edges_geom:
        for point in geom:
            geom_array[address] = point
            address += 1

    geom_address = np.cumsum(geom_count)

    return geom_address, geom_array


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
    return np.flip(Z, 0)


def compute_isochrone(edge_network, start_vertices, travel_time, zoom: int = 10):
    """
    Compute isochrone for a given start vertices

    :param edge_network: Edge Network DataFrame
    :param start_vertices: List of start vertices
    :param travel_time: Travel time in minutes
    :return: R5 Grid
    """
    isochrone_start_time = time()
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
    # edges_geom = np.array(edge_network["geom"])
    start_time = time()
    geom_address, geom_array = get_geom_array(edge_network["geom"])
    end_time = time()
    print(f"Convert geom array time: \t {end_time - start_time} s")
    edges_length = np.array(edge_network["length"])
    start_time = time()
    unordered_map, node_coords = remap_edges(edges_source, edges_target, geom_address, geom_array)
    end_time = time()
    print(f"Remap edges time: \t\t {end_time-start_time} s")

    extent = get_extent(geom_array)

    # add buffer of 200 meters to extent
    extent[0] -= 200
    extent[1] -= 200
    extent[2] += 200
    extent[3] += 200

    # construct adjacency list
    # adj_list = construct_adjacency_list_(
    #     unordered_map.len, edges_source, edges_target, edges_cost, edges_reverse_cost
    # )

    # run dijkstra
    # start_vertices_ids = np.array([unordered_map[v] for v in start_vertices])
    start_vertices_ids = unordered_map.get_by_list(start_vertices)
    start_time = time()
    distances = dijkstra2(
        start_vertices_ids,
        edges_source,
        edges_target,
        edges_cost,
        edges_reverse_cost,
        travel_time,
    )
    end_time = time()
    print(f"Dijkstra time: \t\t {end_time - start_time}s")

    # minx, miny, maxx, maxy
    width_meter = extent[2] - extent[0]
    height_meter = extent[3] - extent[1]

    # get corners in pixel
    # Pixel coordinates origin is at the top left corner of the image. (y of top right/left corner is smaller than y of bottom right/left corner)
    xy_bottom_left = [
        math.floor(x)
        for x in coordinate_to_pixel(
            [extent[0], extent[1]], zoom=zoom, return_dict=False, web_mercator=True
        )
    ]
    xy_top_right = [
        math.floor(x)
        for x in coordinate_to_pixel(
            [extent[2], extent[3]], zoom=zoom, return_dict=False, web_mercator=True
        )
    ]

    # pixel x, y distances
    width_pixel = xy_top_right[0] - xy_bottom_left[0]
    height_pixel = xy_bottom_left[1] - xy_top_right[1]

    # calculate step in web mercator size
    web_mercator_x_step = width_meter / width_pixel
    web_mercator_y_step = height_meter / height_pixel

    # split edges based on resolution
    interpolated_coords = []
    interpolated_costs = []
    start_time = time()
    interpolated_coords, interpolated_costs = split_edges(
        edges_source,
        edges_target,
        edges_length,
        geom_address,
        geom_array,
        distances,
        min([web_mercator_x_step, web_mercator_y_step]),
    )
    end_time = time()
    print(f"Split Edges took \t\t {end_time - start_time} s")

    # node_coords_list = list(node_coords) + interpolated_coords
    start_time = time()
    node_coords_list = np.concatenate((node_coords, interpolated_coords))
    node_costs_list = np.concatenate((distances, interpolated_costs))
    end_time = time()
    print(f"Coords concatenations time: \t {end_time - start_time} s")

    start_time = time()
    node_coords_list, node_costs_list = filter_nodes(
        node_coords_list, node_costs_list, zoom, width_pixel, xy_bottom_left[0], xy_top_right[1]
    )
    end_time = time()
    print(f"Filter nodes time: \t\t {end_time - start_time} s")

    edges_length = range(len(edges_source))
    start_time = time()
    network = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": geom_array[geom_address[idx] : geom_address[idx + 1], :],
                },
                "properties": {"cost": distances[edges_target[idx]]},
            }
            for idx in edges_length
            if distances[edges_target[idx]] != np.inf
        ],
    }
    end_time = time()
    print(f"Build network time: \t\t {end_time - start_time} s")
    # write geojson
    # with open("isochrone.geojson", "w") as f:
    #     json.dump(geojson, f)

    # build grid
    start_time = time()
    Z = build_grid_interpolate_(
        node_coords_list,
        node_costs_list,
        extent,
        step_x=web_mercator_x_step,
        step_y=web_mercator_y_step,
    )
    end_time = time()
    print(f"Grid interpolate time: \t\t {end_time - start_time} s")

    # build grid data (single depth)
    start_time = time()
    grid_data = get_single_depth_grid_(zoom, xy_bottom_left[0], xy_top_right[1], Z)
    end_time = time()
    print(f"Single Depth grid time: \t\t {end_time - start_time} s")

    isochrone_end_time = time()
    print(f"Compute Isochrone time: \t {isochrone_end_time - isochrone_start_time}s")
    return grid_data, network


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
