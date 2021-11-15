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

#ifdef DEBUG
#include <fstream>
#include <cstring>
#endif

#ifndef DEBUG
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#endif

struct NetworkEdge
{
  int64_t id;
  int64_t source;
  int64_t target;
  double cost;
  double reverse_cost;
};

struct IsochroneEdgeElement
{
  int64_t start_id;
  int64_t edge;
  double start_perc;
  double end_perc;
  double start_cost;
  double end_cost;
};

struct Step
{
  int64_t step;
  std::vector<IsochroneEdgeElement> partial;
  std::vector<IsochroneEdgeElement> full;
  std::vector<IsochroneEdgeElement> death_end;
};

struct Result
{
  int64_t start_point;
  std::vector<Step> steps;
};

std::vector<std::vector<const NetworkEdge *>>
construct_adjacency_list(size_t n, const NetworkEdge *edges,
                         size_t total_edges)
{

  std::vector<std::vector<const NetworkEdge *>> adj(n);
  for (size_t i = 0; i < total_edges; ++i)
  {
    if (edges[i].cost >= 0.)
    {
      adj[edges[i].source].push_back(&edges[i]);
    }
    if (edges[i].reverse_cost >= 0.)
    {
      adj[edges[i].target].push_back(&edges[i]);
    }
  }
  return adj;
}

void dijkstra(int64_t start_vertex, double driving_distance,
              const std::vector<std::vector<const NetworkEdge *>> &adj,
              std::vector<int64_t> *predecessors,
              std::vector<double> *distances)
{
  size_t n = adj.size();
  distances->assign(n, std::numeric_limits<double>::infinity());
  predecessors->assign(n, -1);
  typedef std::tuple<double, int64_t> pq_el; // <agg_cost at node, node id>
  std::set<pq_el> q;                         // priority queue
  q.insert({0., start_vertex});
  while (!q.empty())
  {
    double dist;
    int64_t node_id;
    std::tie(dist, node_id) = *q.begin();
    if (dist >= driving_distance)
    {
      break;
    }
    q.erase(q.begin());
    for (auto &&e : adj[node_id])
    {
      int64_t target = e->target == node_id ? e->source : e->target;
      double cost = e->target == node_id ? e->reverse_cost : e->cost;
      double agg_cost = dist + cost;
      if ((*distances)[target] > agg_cost)
      {
        q.erase({(*distances)[target], target});
        (*distances)[target] = agg_cost;
        (*predecessors)[target] = node_id;
        q.emplace((*distances)[target], target);
      }
    }
  }
}

std::unordered_map<int64_t, int64_t> remap_edges(NetworkEdge *data_edges,
                                                 size_t total_edges)
{
  std::unordered_map<int64_t, int64_t> mapping;
  int64_t id = 0;
  for (size_t i = 0; i < total_edges; ++i)
  {
    NetworkEdge *e = data_edges + i;
    int64_t source_id, target_id;
    auto it = mapping.find(e->source);
    // better with if-initialization-statement
    if (it != mapping.end())
    {
      source_id = it->second;
    }
    else
    {
      source_id = id++;
      mapping[e->source] = source_id;
    }
    it = mapping.find(e->target);
    if (it != mapping.end())
    {
      target_id = it->second;
    }
    else
    {
      target_id = id++;
      mapping[e->target] = target_id;
    }
    e->source = source_id;
    e->target = target_id;
  }
  return mapping;
}

void append_edge_result(const int64_t &start_v, const bool &is_target, const double &cost_at_node, const double &edge_cost, const int64_t &edge_id,
                        const std::vector<double> &distance_limits, Result *results)
{

  double current_cost = cost_at_node;
  double travel_cost = edge_cost;
  double start_perc = 0.;

  for (size_t i = 0; i < distance_limits.size(); ++i)
  {
    auto &dl = distance_limits[i];

    if (cost_at_node >= dl)
    {
      continue;
    }
    double cost_at_target = current_cost + travel_cost;
    IsochroneEdgeElement r;
    if (cost_at_target < dl)
    {
      r.start_id = start_v;
      r.edge = edge_id;
      r.start_perc = start_perc;
      r.end_perc = 1.;
      r.start_cost = current_cost;
      r.end_cost = cost_at_target;
      if (is_target)
      {
        double nstart_perc = 1. - r.end_perc;
        r.end_perc = 1. - r.start_perc;
        r.start_perc = nstart_perc;
        std::swap(r.start_cost, r.end_cost); // reversing the cost
      }

      results->steps[i].full.push_back(r);
      break;
    }
    // cost_at_target is bigger than the limit, partial edge
    travel_cost = cost_at_target - dl; // remaining travel cost
    double partial_travel = dl - current_cost;
    r.start_id = start_v;
    r.edge = edge_id;
    r.start_perc = start_perc;
    r.end_perc = start_perc + partial_travel / edge_cost;
    r.start_cost = current_cost;
    r.end_cost = dl;
    if (is_target)
    {
      double nstart_perc = 1. - r.end_perc;
      r.end_perc = 1. - r.start_perc;
      r.start_perc = nstart_perc;
      std::swap(r.start_cost, r.end_cost); // reversing the cost
    }
    results->steps[i].partial.push_back(r);
    start_perc = r.end_perc;
    current_cost = dl;
    // A ---------- B
    // 5    7    9  10
  }
}

std::vector<Result>
do_many_dijkstras(NetworkEdge *data_edges, size_t total_edges,
                  std::vector<int64_t> start_vertices,
                  std::vector<double> distance_limits,
                  bool only_minimum_cover)
{

  // -----
  std::sort(distance_limits.begin(), distance_limits.end());
  // Using max distance limit for a single dijkstra call. After that we will
  // postprocess the results and mark the visited edges.
  double max_dist_cutoff = *distance_limits.rbegin();
  // Extracting vertices and mapping the ids from 0 to N-1. Remapping is done
  // so that data structures used can be simpler (arrays instead of maps).
  std::unordered_map<int64_t, int64_t> mapping =
      // modifying data_edges source/target fields.
      remap_edges(data_edges, total_edges);
  size_t nodes_count = mapping.size();
  std::vector<Result> results(start_vertices.size());

  auto adj =
      construct_adjacency_list(mapping.size(), data_edges, total_edges);
  // Storing the result of dijkstra call and reusing the memory for each vertex.
  std::vector<double> distances(nodes_count);
  std::vector<int64_t> predecessors(nodes_count);

  for (size_t sp = 0; sp < start_vertices.size(); ++sp)
  {
    int64_t start_v = start_vertices[sp];

    results[sp].start_point = start_v;
    results[sp].steps = std::vector<Step>(distance_limits.size());
    for (size_t i = 0; i < distance_limits.size(); ++i)
    {
      auto &dl = distance_limits[i];
      results[sp].steps[i].step = dl;
    }

    auto it = mapping.find(start_v);
    // If start_v did not appear in edges then it has no particular mapping
    if (it == mapping.end())
    {
      continue;
    }
    // Calling the dijkstra algorithm and storing the results in predecessors
    // and distances.
    dijkstra(it->second,
             /* driving_distance */ max_dist_cutoff, adj, &predecessors,
             &distances);
    // Appending the row results.
    for (size_t i = 0; i < total_edges; ++i)
    {
      const NetworkEdge &e = *(data_edges + i);
      double scost = distances[e.source];
      double tcost = distances[e.target];
      bool s_reached = !(std::isinf(scost) || scost > max_dist_cutoff);
      bool t_reached = !(std::isinf(tcost) || tcost > max_dist_cutoff);
      if (!s_reached && !t_reached)
      {
        continue;
      }
      bool skip_st = false;
      bool skip_ts = false;
      if (only_minimum_cover)
      {
        double st_dist = scost + e.cost;
        double ts_dist = tcost + e.reverse_cost;
        bool st_fully_covered = st_dist <= max_dist_cutoff;
        bool ts_fully_covered = ts_dist <= max_dist_cutoff;
        skip_ts = st_fully_covered && ts_fully_covered && st_dist < ts_dist;
        skip_st = st_fully_covered && ts_fully_covered && ts_dist < st_dist;
      }
      if (!skip_ts && t_reached && predecessors[e.target] != e.source)
      {
        append_edge_result(start_v, true, tcost, e.reverse_cost, e.id, distance_limits, &results[sp]);
      }
      if (!skip_st && s_reached && predecessors[e.source] != e.target)
      {
        append_edge_result(start_v, false, scost, e.cost, e.id, distance_limits, &results[sp]);
      }
    }
  }
  return results;
}

#ifdef DEBUG
//Read file. It should come from python (ONLY FOR DEBUGGING)
std::vector<NetworkEdge> read_file(std::string name_file)
{
  std::vector<NetworkEdge> data_edges;
  NetworkEdge edge;
  std::ifstream myfile;
  std::string line;
  myfile.open(name_file, std::ios::in);

  int lineCount = 0;
  std::getline(myfile, line); // ignore header line

  while (std::getline(myfile, line) && !line.empty())
  {
    std::vector<std::string> temp; //read line file
    std::stringstream ss(line);
    std::string temp_str;
    while (std::getline(ss, temp_str, ','))
    { //Split line by ,
      temp.push_back(temp_str);
    }

    edge.id = std::stoll(temp[0]);
    edge.source = std::stoll(temp[1]);
    edge.target = std::stoll(temp[2]);
    edge.cost = std::stod(temp[3]);
    edge.reverse_cost = std::stod(temp[4]);

    data_edges.push_back(edge);
    lineCount++;
  }

  myfile.close();
  return data_edges;
}

int main()
{
  std::cout << "Main function...!";
  // network file location

  std::string network_file = "./data/small_network.csv";
  std::vector<NetworkEdge> data_edges_vector = read_file(network_file);
  static const int64_t total_edges = data_edges_vector.size();
  NetworkEdge *data_edges = new NetworkEdge[total_edges];
  for (int64_t i = 0; i < total_edges; ++i)
  {
    data_edges[i] = data_edges_vector[i];
  }
  data_edges_vector.clear();
  std::vector<double> distance_limits = {20, 30, 40};
  std::vector<int64_t> start_vertices{22731};
  bool only_minimum_cover = true;
  auto results = do_many_dijkstras(data_edges, total_edges, start_vertices,
                                   distance_limits, only_minimum_cover);

  return 0;
}
#endif

#ifndef DEBUG

py::array_t<IsochroneEdgeElement> isochrone(
    py::array_t<NetworkEdge> data_edges_, py::array_t<int64_t> start_vertices_,
    py::array_t<double> distance_limits_, bool only_minimum_cover_)
{
  auto data_edges_c = data_edges_.unchecked<1>();
  auto total_edges = data_edges_.shape(0);

  auto start_vertices_c = start_vertices_.unchecked<1>();
  auto total_start_vertices = start_vertices_.shape(0);

  auto distance_limits_c = distance_limits_.unchecked<1>();
  auto total_distance_limits = distance_limits_.shape(0);

  bool only_minimum_cover = only_minimum_cover_;

  NetworkEdge *data_edges = new NetworkEdge[total_edges];
  for (int64_t i = 0; i < total_edges; ++i)
  {
    data_edges[i] = data_edges_c[i];
  }

  std::vector<int64_t> start_vertices(total_start_vertices);
  for (int64_t i = 0; i < total_start_vertices; ++i)
  {
    start_vertices[i] = start_vertices_c[i];
  }

  std::vector<double> distance_limits(total_distance_limits);
  for (int64_t i = 0; i < total_distance_limits; ++i)
  {
    distance_limits[i] = distance_limits_c[i];
  }

  auto isochrone_points = do_many_dijkstras(data_edges, total_edges, start_vertices,
                                            distance_limits, only_minimum_cover);

  py::array_t<Result> result(isochrone_points.size());
  auto result_ptr = result.mutable_unchecked<1>();
  for (size_t i = 0; i < isochrone_points.size(); i++)
  {
    result_ptr(i) = isochrone_points[i];
  }

  return result;
}

PYBIND11_MODULE(isochrone, m)
{
  m.doc() = "Isochrone Calculation";
  m.def("isochrone", &isochrone, "Isochrone Calculation");

  PYBIND11_NUMPY_DTYPE(Step, step, partial, full, death_end);
  PYBIND11_NUMPY_DTYPE(Result, start_point, steps);
  PYBIND11_NUMPY_DTYPE(NetworkEdge, id, source, target, cost, reverse_cost);
}
/*

*/
#endif