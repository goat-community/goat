// cppimport

/*PGR-GNU*****************************************************************
File: isochrone.cpp
Copyright (c) 2020 Vjeran Crnjak
vjeran@crnjak.xyz
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

#ifndef DEBUG
#include <pybind11/pybind11.h>
namespace py = pybind11;
#endif

typedef struct
{
  int64_t id;
  int64_t source;
  int64_t target;
  double cost;
  double reverse_cost;
} pgr_edge_t;

typedef struct
{
  int64_t start_id;
  int64_t edge;
  double start_perc;
  double end_perc;
  double start_cost;
  double end_cost;
} Isochrones_path_element_t;

std::vector<std::vector<const pgr_edge_t *>>
construct_adjacency_matrix(size_t n, const pgr_edge_t *edges,
                           size_t total_edges)
{
  std::vector<std::vector<const pgr_edge_t *>> adj(n);
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
              const std::vector<std::vector<const pgr_edge_t *>> &adj,
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

std::unordered_map<int64_t, int64_t> remap_edges(pgr_edge_t *data_edges,
                                                 size_t total_edges)
{
  std::unordered_map<int64_t, int64_t> mapping;
  int64_t id = 0;
  for (size_t i = 0; i < total_edges; ++i)
  {
    pgr_edge_t *e = data_edges + i;
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

void append_edge_result(const double &cost_at_node, const double &edge_cost,
                        const std::vector<double> &distance_limits,
                        std::vector<Isochrones_path_element_t> *results)
{
  double current_cost = cost_at_node;
  double travel_cost = edge_cost;
  double start_perc = 0.;
  for (auto &dl : distance_limits)
  {
    if (cost_at_node >= dl)
    {
      continue;
    }
    double cost_at_target = current_cost + travel_cost;
    Isochrones_path_element_t r;
    if (cost_at_target < dl)
    {
      r.start_perc = start_perc;
      r.end_perc = 1.;
      r.start_cost = current_cost;
      r.end_cost = cost_at_target;
      results->push_back(r);
      break;
    }
    // cost_at_target is bigger than the limit, partial edge
    travel_cost = cost_at_target - dl; // remaining travel cost
    double partial_travel = dl - current_cost;
    r.start_perc = start_perc;
    r.end_perc = start_perc + partial_travel / edge_cost;
    r.start_cost = current_cost;
    r.end_cost = dl;
    results->push_back(r);

    start_perc = r.end_perc;
    current_cost = dl;
    // A ---------- B
    // 5    7    9  10
  }
}

std::vector<Isochrones_path_element_t>
do_many_dijkstras(pgr_edge_t *data_edges, size_t total_edges,
                  std::vector<int64_t> start_vertices,
                  std::vector<double> distance_limits,
                  bool only_minimum_cover)
{
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
  std::vector<Isochrones_path_element_t> results;

  auto adj =
      construct_adjacency_matrix(mapping.size(), data_edges, total_edges);
  // Storing the result of dijkstra call and reusing the memory for each vertex.
  std::vector<double> distances(nodes_count);
  std::vector<int64_t> predecessors(nodes_count);
  for (int64_t start_v : start_vertices)
  {
    auto it = mapping.find(start_v);
    // If start_v did not appear in edges then it has no particular mapping but
    // pgr_drivingDistance result includes one row for this node.
    if (it == mapping.end())
    {
      Isochrones_path_element_t r;
      r.start_id = start_v;
      // -2 tags the unmapped starting vertex and won't use the reverse_mapping
      // because mapping does not exist. -2 is changed to -1 later.
      r.edge = -1;
      r.start_perc = 0.0;
      r.end_perc = 0.0;
      results.push_back(r);
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
      const pgr_edge_t &e = *(data_edges + i);
      double scost = distances[e.source];
      double tcost = distances[e.target];
      bool s_reached = !(std::isinf(scost) || scost > max_dist_cutoff);
      bool t_reached = !(std::isinf(tcost) || tcost > max_dist_cutoff);
      if (!s_reached && !t_reached)
      {
        continue;
      }
      size_t r_i = results.size();
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
        append_edge_result(tcost, e.reverse_cost, distance_limits, &results);
        for (size_t rev_i = r_i; rev_i < results.size(); ++rev_i)
        {
          // reversing the percentage
          double nstart_perc = 1. - results[rev_i].end_perc;
          results[rev_i].end_perc = 1. - results[rev_i].start_perc;
          results[rev_i].start_perc = nstart_perc;
          // reversing the cost
          std::swap(results[rev_i].start_cost, results[rev_i].end_cost);
          // results[r_i].start_cost  -- filled in append_edge_result
          // results[r_i].end_cost  -- filled in append_edge_result
          // results[r_i].start_perc -- filled in append_edge_result
          // results[r_i].end_perc - filled in append_edge_result
        }
      }
      if (!skip_st && s_reached && predecessors[e.source] != e.target)
      {
        append_edge_result(scost, e.cost, distance_limits, &results);
      }
      for (; r_i < results.size(); ++r_i)
      {
        results[r_i].edge = e.id;
        results[r_i].start_id = start_v;
        // results[r_i].start_cost  -- filled in append_edge_result
        // results[r_i].end_cost  -- filled in append_edge_result
        // results[r_i].start_perc -- filled in append_edge_result
        // results[r_i].end_perc - filled in append_edge_result
      }
    }
  }
  // sorting by cutoffs.
  std::sort(results.begin(), results.end(),
            [](Isochrones_path_element_t &a, Isochrones_path_element_t &b)
            {
              return std::tie(a.start_id, a.end_cost) <
                     std::tie(b.start_id, b.end_cost);
            });
  return results;
}

void do_pgr_many_to_isochrones(pgr_edge_t *data_edges, size_t total_edges,
                               int64_t *start_vertex, size_t s_len,
                               double *distance_cutoffs, size_t d_len,
                               bool only_minimum_cover,
                               Isochrones_path_element_t **return_tuples,
                               size_t *return_count, char **log_msg,
                               char **notice_msg, char **err_msg)
{
  std::ostringstream log;
  std::ostringstream err;
  std::ostringstream notice;

  std::vector<int64_t> start_vertices(start_vertex, start_vertex + s_len);
  std::vector<double> distances(distance_cutoffs, distance_cutoffs + d_len);
  auto results = do_many_dijkstras(data_edges, total_edges, start_vertices,
                                   distances, only_minimum_cover);

  size_t count(results.size());
  if (count == 0)
  {
    log << "\nNo return values were found";
    // *notice_msg = pgr_msg(log.str().c_str());
    return;
  }
  // *return_tuples = pgr_alloc(count, (*return_tuples));
  *return_count = count;

  // Moving results to allocated return_tuples array.
  for (size_t i = 0; i < count; ++i)
  {
    (*return_tuples)[i] = results[i];
  }

  // *log_msg = log.str().empty() ? *log_msg : log.str().c_str();
  // *notice_msg =
  //     notice.str().empty() ? *notice_msg : notice.str().c_str();
}

int main()
{
  std::cout << "Hello World!";
  return 0;
}

#ifndef DEBUG
int square(int x)
{
  return x * x;
}

PYBIND11_MODULE(isochrone, m)
{
  m.def("square", &square);
}
/*
<%
setup_pybind11(cfg)
%>
*/
#endif