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
#pragma once
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

typedef struct
{
    std::vector<std::array<double, 2>> shape;
    std::vector<int32_t> indices;
} ConvexhullResult;

// // Adjacency list for the isochrone network (for each node, the edges that are connected to it)
// std::vector<std::vector<const Edge *>>
// construct_adjacency_list(size_t n, const Edge *edges,
//                          size_t total_edges);

// // Dijkstra's algorithm one-to-all shortest path search

// void dijkstra(int64_t start_vertex, double driving_distance,
//               const std::vector<std::vector<const Edge *>> &adj,
//               std::vector<int64_t> *predecessors,
//               std::vector<double> *distances);

// std::unordered_map<int64_t, int64_t> remap_edges(Edge *data_edges,
//                                                  size_t total_edges);

// // Returns a positive value, if OAB makes a counter-clockwise turn,
// // negative for clockwise turn, and zero if the points are collinear.
// double cross(const std::array<double, 2> &O, const std::array<double, 2> &A, const std::array<double, 2> &B);

// ConvexhullResult convexhull(std::vector<std::array<double, 2>> &P);

// std::vector<std::array<double, 2>> line_substring(const double &start_perc, const double &end_perc, const std::vector<std::array<double, 2>> &geometry, const double &total_length);

// void reverse_isochrone_path(IsochroneNetworkEdge &isochrone_path);

// void append_edge_result(const int64_t &start_v, const int64_t &edge_id, const double &cost_at_node, const double &edge_cost, const double &edge_length, const std::vector<std::array<double, 2>> &geometry,
//                         const std::vector<double> &distance_limits,
//                         std::vector<IsochroneNetworkEdge> *isochrone_network, std::unordered_map<double, std::vector<std::array<double, 2>>> &coordinates, const bool &is_reverse);

// Result compute_isochrone(Edge *data_edges, size_t total_edges,
//                          std::vector<int64_t> start_vertices,
//                          std::vector<double> distance_limits,
//                          bool only_minimum_cover);

typedef struct
{
    double max_x = std::numeric_limits<double>::min();
    double max_y = std::numeric_limits<double>::min();
    double min_x = std::numeric_limits<double>::max();
    double min_y = std::numeric_limits<double>::max();
} Boundry;

typedef struct
{
    std::vector<std::array<double, 2>> points;
    std::vector<float> costs;
    Boundry boundry;
} CostResult;

typedef struct
{
    std::array<double, 2> start_point;
    std::array<double, 2> end_point;
} Line;

typedef struct
{
    float x;
    float y;
} XY;

typedef struct
{
    int64_t start_id;
    int64_t edge;
    double start_perc;
    double end_perc;
    double start_cost;
    double end_cost;
    double length;
    std::vector<std::array<double, 2>> geometry;
} IsochroneNetworkEdge2;

typedef struct
{
    std::vector<IsochroneStartPoint> isochrone;
    std::vector<IsochroneNetworkEdge2> network;
} Result2;

// void append_edge_result(const int64_t &start_v, const int64_t &edge_id, const double &cost_at_node, const double &edge_cost, const double &edge_length, const std::vector<std::array<double, 2>> &geometry,
//                         const std::vector<double> &distance_limits,
//                         std::vector<IsochroneNetworkEdge2> *isochrone_network, std::unordered_map<double, std::vector<std::array<double, 2>>> &coordinates, const bool &is_reverse);

// void reverse_isochrone_path(IsochroneNetworkEdge2 &isochrone_path);

// Result2 calculate2(
//     py::array_t<int64_t> &edge_ids_, py::array_t<int64_t> &sources_,
//     py::array_t<int64_t> &targets_, py::array_t<double> &costs_,
//     py::array_t<double> &reverse_costs_, py::array_t<double> &length_, std::vector<std::vector<std::array<double, 2>>> &geometry,
//     py::array_t<int64_t> start_vertices_,
//     py::array_t<double> distance_limits_,
//     bool only_minimum_cover_);

void append_edge_result2(const int64_t &start_v, const int64_t &edge_id, const double &cost_at_node, const double &edge_cost, const double &edge_length, const std::vector<std::array<double, 2>> &geometry,
                         const std::vector<double> &distance_limits,
                         std::vector<IsochroneNetworkEdge2> *isochrone_network, std::unordered_map<double, std::vector<std::array<double, 2>>> &coordinates, const bool &is_reverse);

void reverse_isochrone_path2(IsochroneNetworkEdge2 &isochrone_path);