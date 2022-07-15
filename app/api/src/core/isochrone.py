"""
Translated from: https://github.com/goat-community/goat/blob/6b1dcbf592b5f59958998ae787059c26d29e19db/app/api/src/exts/cpp/src/isochrone.cpp
PGR-GNU*****************************************************************
File: isochrone.cpp
Copyright (c) 2021 Majk Shkurti, <majk.shkurti@plan4better.de>
Copyright (c) 2020 Vjeran Crnjak, <vjeran@crnjak.xyz>
------
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 ********************************************************************PGR-GNU*
"""

from collections import defaultdict, deque
from math import sqrt

import numpy as np

from src.exts.python import concaveman


class Mapping(defaultdict):
    """
    Return key of founded value.
    Ref: https:#stackoverflow.com/a/8023337/1951027
    """

    def find_value(self, search_value):
        for key, value in self.items():
            if value == search_value:
                return value
        return None

    def find_key(self, search_key):
        for key, value in self.items():
            if key == search_key:
                return key
        return None

    def find_key_by_value(self, search_value):
        for key, value in self.items():
            if value == search_value:
                return key
        return None

    def size(self):
        return len(self)


class Isochrone:
    def construct_adjustancy_list(self):
        adj = Mapping(list)
        for index, edge in enumerate(self.data_edges):
            if edge["cost"] >= 0:
                adj[edge["source"]].append(index)

            if edge["reverse_cost"] >= 0:
                adj[edge["target"]].append(index)
        self.adj = adj
        return adj

    def dijkstra(self, start_vertex, driving_distance):
        """
        Dijkstra's algorithm one-to-all shortest path search
        """
        distances = np.array(np.ones(len(self.adj)) * np.inf, dtype=np.double)
        predecessors = np.array(np.ones(len(self.adj)) * -1, dtype=np.int64)
        q = deque()
        q.append((0, start_vertex))
        while q:
            dist, node_id = q.popleft()
            if dist >= driving_distance:
                break

            for edge in self.adj[node_id]:
                if edge["target"] == node_id:
                    target = edge["source"]
                    cost = edge["reverse_cost"]
                else:
                    target = edge["target"]
                    cost = edge["cost"]
                agg_cost = dist + cost
                if distances[target] > agg_cost:
                    q.remove((distances[target], target))
                    distances[target] = agg_cost
                    predecessors[target] = node_id
                    q.append((distances[target], target))
        return distances, predecessors

    def remap_edges(self):
        mapping = Mapping()
        for edge in self.data_edges:
            it = mapping.find_value(edge["source"])

            if it:
                source_id = it
            else:
                id += 1
                source_id = id
                mapping[edge["source"]] = source_id

            it = mapping.find_value(edge["target"])
            if it:
                target_id = it
            else:
                id += 1
                target_id = id
                mapping[edge["target"]] = target_id

            edge["source"] = source_id
            edge["target"] = target_id
        self.mapping = mapping
        return mapping

    def cross(self, O, A, B):
        """
        Returns a positive value, if OAB makes a counter-clockwise turn,
        negative for clockwise turn, and zero if the points are collinear.
        """
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    def custom_less(self, pt1, pt2):
        return pt1[0] < pt2[0] or (pt1[0] == pt2[0] and pt1[1] < pt2[1])

    def convexhull(self, P):
        """
        ---------------------------------------------------------------------------------------------------------------------
        CONVEX HULL ALGORITHM
        ---------------------------------------------------------------------------------------------------------------------
        Implementation of Andrew's monotone chain 2D convex hull algorithm.

        Returns a list of points on the convex hull in counter-clockwise order.
        Note: the last point in the returned list is the same as the first one.
        """
        n = len(P)
        if n < 3:
            raise AttributeError("Number of points must be 3 or morenot ")
        H = np.empty([2 * n, 2], dtype=np.double)
        H_indices = np.empty(
            [
                2 * n,
            ],
            dtype=np.int32,
        )

        # Sort points lexicographically
        P_python_list = P.tolist()
        P_python_list.sort(cpm=self.custom_less)
        P = np.array(P_python_list, dtype=np.double)
        del P_python_list
        k = 0
        # Build lower hull
        for i, P_ in enumerate(P):
            while k >= 2 and self.cross(H[k - 2], H[k - 1], P_) <= 0:
                k -= 1
            k += 1
            H[k] = P_
            H_indices[k - 1] = i

        # Build upper hull
        t = k + 1
        for i in range(n - 1, 0, -1):
            while k >= t and self.cross(H[k - 2], H[k - 1], P[i - 1]) <= 0:
                k -= 1
            k += 1
            H[k] = P[i - 1]
            H_indices[k - 1] = i - 1

        H.resize(k - 1)
        H_indices.resize(k - 1)
        return {"shape": H, "indices": H_indices}

    def line_substring(start_perc, end_perc, geometry, total_length):
        """
        LINE SUBSTRING ALGORITHM
        """
        # Start percentage must be smaller than end percentage.
        start_perc_ = start_perc
        end_perc_ = end_perc
        line_substring = []
        if start_perc_ > end_perc_:
            start_perc_, end_perc_ = end_perc_, start_perc_

        start_dist = start_perc_ * total_length
        end_dist = end_perc_ * total_length
        size = geometry.size()

        start_reached = False
        accumulated_dist = 0.0

        for i in range(size - 1):
            # Edge cases check.
            if start_perc_ == 1:

                line_substring.append(geometry[size - 1])
                break

            if end_perc_ == 0:

                line_substring.append(geometry[0])
                break

            # Find segment distance (sqrt((x1-x2)^2 + (y1-y2)^2))
            x1 = geometry[i][0]
            y1 = geometry[i][1]
            x2 = geometry[i + 1][0]
            y2 = geometry[i + 1][1]
            dx = x1 - x2
            dy = y1 - y2
            segment_dist = sqrt(pow(dx, 2) + pow(dy, 2))
            dist_at_coord = accumulated_dist
            accumulated_dist += segment_dist
            if i == 0 and start_perc_ == 0:

                line_substring.push_back(geometry[0])
                start_reached = True

            # Interpolate at start percentage and push to line_substring
            if accumulated_dist >= start_dist and not start_reached:

                d2 = start_dist - dist_at_coord
                x = x1 - ((d2 * dx) / segment_dist)
                y = y1 - ((d2 * dy) / segment_dist)
                line_substring.push_back(x, y)
                start_reached = True

            if i == size - 2 and end_perc_ == 1:

                line_substring.push_back(geometry[size - 1])
                break

            # Interpolate at end percentage, push to line_substring and break
            if accumulated_dist >= end_dist:

                d2 = end_dist - dist_at_coord
                x = x1 - ((d2 * dx) / segment_dist)
                y = y1 - ((d2 * dy) / segment_dist)
                line_substring.push_back(x, y)
                break

            # Push midpoints to line_substring
            if start_reached:

                line_substring.push_back(geometry[i + 1])

        return line_substring

    def reverse_isochrone_path(isochrone_path):
        # reverse the percantage
        nstart_perc = 1.0 - isochrone_path.end_perc
        isochrone_path.end_perc = 1.0 - isochrone_path.start_perc
        isochrone_path.start_perc = nstart_perc
        # reversing the cost
        isochrone_path.start_cost, isochrone_path.end_cost = (
            isochrone_path.end_cost,
            isochrone_path.start_cost,
        )
        return isochrone_path

    def append_edge_result(
        self,
        start_v,
        edge_id,
        cost_at_node,
        edge_cost,
        edge_length,
        geometry,
        distance_limits,
        coordinates,
        is_reverse,
    ):

        current_cost = cost_at_node
        travel_cost = edge_cost
        start_perc = 0.0

        for dl in distance_limits:
            if cost_at_node >= dl:
                continue

            cost_at_target = current_cost + travel_cost
            r = {}
            r["start_id"] = start_v
            r["edge"] = edge_id
            # Full edge
            if cost_at_target < dl:

                r["start_perc"] = start_perc
                r["end_perc"] = 1.0
                r["start_cost"] = current_cost
                r["end_cost"] = cost_at_target
                r["geometry"] = geometry
                if is_reverse:
                    r = self.reverse_isochrone_path(r)
                self.isochrone_network.append(r)
                coordinates[dl] = r["geometry"]
                break
            # Partial Edge: (cost_at_target is bigger than the limit, partial edge)
            travel_cost = cost_at_target - dl  # remaining travel cost
            partial_travel = dl - current_cost
            r["start_perc"] = start_perc
            r["end_perc"] = start_perc + partial_travel / edge_cost
            r["start_cost"] = current_cost
            r["end_cost"] = dl
            start_perc = r["end_perc"]
            current_cost = dl
            if is_reverse:
                r = self.reverse_isochrone_path(r)
            r["geometry"] = self.line_substring(
                r["start_perc"], r["end_perc"], geometry, edge_length
            )
            self.isochrone_network.append(r)
            coordinates[dl] = r["geometry"]
            # A ---------- B
            # 5    7    9  10

    def compute_isochrone(self, only_minimum_cover=False):
        self.distance_limits.sort()
        # Using max distance limit for a single dijkstra call. After that we will
        # postprocess the results and mark the visited edges.
        max_dist_cutoff = self.distance_limits[-1]
        # Extracting vertices and mapping the ids from 0 to N-1. Remapping is done
        # so that data structures used can be simpler (arrays instead of maps).
        # modifying data_edges source/target fields.
        mapping = self.remap_edges()

        # std::unordered_map<int64_t, int64_t> mapping_reversed

        # for (i = mapping.begin() i not = mapping.end() ++i)
        #     mapping_reversed[i->second] = i->first

        # coordinates for the network edges for each distance limit to be used in constructing the isochrone shape
        coordinates = Mapping(list)
        nodes_count = mapping.size()
        isochrone_network = []
        isochrone_start_point = []
        # for (&dl : distance_limits)
        # {
        #     coordinates.emplace(dl, std::vector<std::array<double, 2>>())
        # }
        adj = self.construct_adjacency_list()
        # Storing the result of dijkstra call and reusing the memory for each vertex.
        self.distances = np.empty(nodes_count, dtype=np.double)
        self.predecessors = np.empty(nodes_count, dtype=np.int64)
        for start_v in self.start_vertices:
            it = mapping.get(start_v)
            # If start_v did not appear in edges then it has no particular mapping
            if not it:
                r = {}
                r["start_id"] = start_v
                # -2 tags the unmapped starting vertex and won't use the reverse_mapping
                # because mapping does not exist. -2 is changed to -1 later.
                r["edge"] = -1
                r["start_perc"] = 0.0
                r["end_perc"] = 0.0
                r["geometry"] = {{0, 0}, {0, 0}}
                isochrone_network.append(r)
                continue
            # Calling the dijkstra algorithm and storing the results in predecessors
            # and distances.

            distances, predecessors = self.dijkstra(it, max_dist_cutoff, adj)
            # Appending the row results.
            total_edges = len(self.data_edges)
            for i, e in enumerate(self.data_edges):
                scost = distances[e["source"]]
                tcost = distances[e["target"]]
                s_reached = not (np.isinf(scost) or scost > max_dist_cutoff)
                t_reached = not (np.isinf(tcost) or tcost > max_dist_cutoff)
                if not s_reached and not t_reached:
                    continue

                skip_st = False
                skip_ts = False
                if only_minimum_cover:
                    st_dist = scost + e["cost"]
                    ts_dist = tcost + e["reverse_cost"]
                    st_fully_covered = st_dist <= max_dist_cutoff
                    ts_fully_covered = ts_dist <= max_dist_cutoff
                    skip_ts = st_fully_covered and ts_fully_covered and st_dist < ts_dist
                    skip_st = st_fully_covered and ts_fully_covered and ts_dist < st_dist

                if start_v == mapping.find_key_by_value(e["source"]):
                    self.append_edge_result(
                        start_v,
                        e.id,
                        0,
                        e.cost,
                        e.length,
                        e.geometry,
                        self.distance_limits,
                        isochrone_network,
                        coordinates,
                        True,
                    )
                if start_v == mapping.find_key_by_value(e["target"]):

                    self.append_edge_result(
                        start_v,
                        e.id,
                        0,
                        e.reverse_cost,
                        e.length,
                        e.geometry,
                        self.distance_limits,
                        isochrone_network,
                        coordinates,
                        True,
                    )

                if not skip_ts and t_reached and predecessors[e.target] != e.source:

                    self.append_edge_result(
                        start_v,
                        e.id,
                        tcost,
                        e.reverse_cost,
                        e.length,
                        e.geometry,
                        self.distance_limits,
                        isochrone_network,
                        coordinates,
                        True,
                    )

                if not skip_st and s_reached and predecessors[e.source] != e.target:

                    self.append_edge_result(
                        start_v,
                        e.id,
                        scost,
                        e.cost,
                        e.length,
                        e.geometry,
                        self.distance_limits,
                        isochrone_network,
                        coordinates,
                        False,
                    )

            # Calculating the isochrone shape for the current starting vertex.

            isochrone_start_point = {}
            isochrone_start_point.start_id = start_v
            for dl in self.distance_limits:

                if coordinates[dl].size() > 1:

                    points_ = coordinates[dl]
                    isochrone_path = []
                    if points_.size() > 3:

                        hull = self.convexhull(points_)
                        isochrone_path = concaveman.concaveman2d(points_, hull)

                    else:

                        isochrone_path = {{0, 0}}

                    coordinates[dl].clear()
                    isochrone_start_point.shape.emplace(dl, isochrone_path)

            isochrone_start_point.push_back(isochrone_start_point)

        return {"isochrone": isochrone_start_point, "network": isochrone_network}

    def __init__(
        self, data_edges, start_vertecies, distance_limits, only_minimum_cover=False
    ) -> None:
        self.data_edges = data_edges
        self.start_vertecies = start_vertecies
        self.distance_limits = distance_limits
        self.only_minimum_cover = only_minimum_cover
