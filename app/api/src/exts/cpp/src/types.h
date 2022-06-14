// cppimport

/*PGR-GNU*****************************************************************
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
 ********************************************************************PGR-GNU*/

#include <iostream>
#include <algorithm>
#include <cmath>
#include <limits>
#include <set>
#include <sstream>
#include <unordered_map>
#include <vector>
#include <string>
#include <cstring>
#include <exception>
#include "concaveman.h"
#include <map>

#ifdef DEBUG
#include <fstream>
#include <regex>
#include <iterator>
#endif

#ifndef DEBUG
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;
#endif

// ---------------------------------------------------------------------------------------------------------------------
// ***************************************** ISOCHRONE COMPUTATION *****************************************************
// ---------------------------------------------------------------------------------------------------------------------

typedef struct
{
    int64_t id;
    int64_t source;
    int64_t target;
    double cost;
    double reverse_cost;
    double length;
    std::vector<std::array<double, 2>> geometry;
} Edge;

typedef struct
{
    int64_t start_id;
    int64_t edge;
    double start_perc;
    double end_perc;
    double start_cost;
    double end_cost;
    std::vector<std::array<double, 2>> geometry;
} IsochroneNetworkEdge;

typedef struct
{
    int64_t start_id;
    std::unordered_map<int32_t, std::vector<std::array<double, 2>>> shape; // steps, geometry
} IsochroneStartPoint;

typedef struct
{
    std::vector<IsochroneStartPoint> isochrone;
    std::vector<IsochroneNetworkEdge> network;
} Result;

// Adjacency list for the isochrone network (for each node, the edges that are connected to it)
std::vector<std::vector<const Edge *>>
construct_adjacency_list(size_t n, const Edge *edges,
                         size_t total_edges);

// Dijkstra's algorithm one-to-all shortest path search

void dijkstra(int64_t start_vertex, double driving_distance,
              const std::vector<std::vector<const Edge *>> &adj,
              std::vector<int64_t> *predecessors,
              std::vector<double> *distances);

std::unordered_map<int64_t, int64_t> remap_edges(Edge *data_edges,
                                                 size_t total_edges);

// Returns a positive value, if OAB makes a counter-clockwise turn,
// negative for clockwise turn, and zero if the points are collinear.
double cross(const std::array<double, 2> &O, const std::array<double, 2> &A, const std::array<double, 2> &B);

struct ConvexhullResult
{
    std::vector<std::array<double, 2>> shape;
    std::vector<int32_t> indices;
};

ConvexhullResult convexhull(std::vector<std::array<double, 2>> &P);

std::vector<std::array<double, 2>> line_substring(const double &start_perc, const double &end_perc, const std::vector<std::array<double, 2>> &geometry, const double &total_length);

void reverse_isochrone_path(IsochroneNetworkEdge &isochrone_path);

void append_edge_result(const int64_t &start_v, const int64_t &edge_id, const double &cost_at_node, const double &edge_cost, const double &edge_length, const std::vector<std::array<double, 2>> &geometry,
                        const std::vector<double> &distance_limits,
                        std::vector<IsochroneNetworkEdge> *isochrone_network, std::unordered_map<double, std::vector<std::array<double, 2>>> &coordinates, const bool &is_reverse);

void append_edge_result(const int64_t &start_v, const int64_t &edge_id, const double &cost_at_node, const double &edge_cost, const double &edge_length, const std::vector<std::array<double, 2>> &geometry,
                        const std::vector<double> &distance_limits,
                        std::vector<IsochroneNetworkEdge> *isochrone_network, std::unordered_map<double, std::vector<std::array<double, 2>>> &coordinates, const bool &is_reverse);

Result compute_isochrone(Edge *data_edges, size_t total_edges,
                         std::vector<int64_t> start_vertices,
                         std::vector<double> distance_limits,
                         bool only_minimum_cover);