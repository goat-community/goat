#include "types.h"

Result2 compute_isochrone2(Edge *data_edges, size_t total_edges,
                           std::vector<int64_t> start_vertices,
                           std::vector<double> distance_limits,
                           bool only_minimum_cover)
{
    Result2 result;
    std::sort(distance_limits.begin(), distance_limits.end());
    // Using max distance limit for a single dijkstra call. After that we will
    // postprocess the results and mark the visited edges.
    double max_dist_cutoff = *distance_limits.rbegin();
    // Extracting vertices and mapping the ids from 0 to N-1. Remapping is done
    // so that data structures used can be simpler (arrays instead of maps).
    // modifying data_edges source/target fields.
    std::unordered_map<int64_t, int64_t> mapping = remap_edges(data_edges, total_edges);

    std::unordered_map<int64_t, int64_t> mapping_reversed;

    for (auto i = mapping.begin(); i != mapping.end(); ++i)
        mapping_reversed[i->second] = i->first;

    // coordinates for the network edges for each distance limit to be used in constructing the isochrone shape
    std::unordered_map<double, std::vector<std::array<double, 2>>> coordinates;
    size_t nodes_count = mapping.size();
    std::vector<IsochroneNetworkEdge2> isochrone_network;
    std::vector<IsochroneStartPoint> isochrone_start_point;
    for (auto &dl : distance_limits)
    {
        coordinates.emplace(dl, std::vector<std::array<double, 2>>());
    }
    auto adj =
        construct_adjacency_list(mapping.size(), data_edges, total_edges);
    // Storing the result of dijkstra call and reusing the memory for each vertex.
    std::vector<double> distances(nodes_count);
    std::vector<int64_t> predecessors(nodes_count);
    for (int64_t start_v : start_vertices)
    {
        auto it = mapping.find(start_v);
        // If start_v did not appear in edges then it has no particular mapping
        if (it == mapping.end())
        {
            IsochroneNetworkEdge2 r;
            r.start_id = start_v;
            // -2 tags the unmapped starting vertex and won't use the reverse_mapping
            // because mapping does not exist. -2 is changed to -1 later.
            r.edge = -1;
            r.start_perc = 0.0;
            r.end_perc = 0.0;
            r.geometry = {{0, 0}, {0, 0}};
            isochrone_network.push_back(r);
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
            const Edge &e = *(data_edges + i);
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

            if (start_v == mapping_reversed.find(e.source)->second)
            {
                append_edge_result(start_v, e.id, 0, e.cost, e.length, e.geometry, distance_limits, &isochrone_network, coordinates, true);
            }
            if (start_v == mapping_reversed.find(e.target)->second)
            {
                append_edge_result(start_v, e.id, 0, e.reverse_cost, e.length, e.geometry, distance_limits, &isochrone_network, coordinates, true);
            }
            if (!skip_ts && t_reached && predecessors[e.target] != e.source)
            {
                append_edge_result(start_v, e.id, tcost, e.reverse_cost, e.length, e.geometry, distance_limits, &isochrone_network, coordinates, true);
            }
            if (!skip_st && s_reached && predecessors[e.source] != e.target)
            {
                append_edge_result(start_v, e.id, scost, e.cost, e.length, e.geometry, distance_limits, &isochrone_network, coordinates, false);
            }
        }
        // Calculating the isochrone shape for the current starting vertex.

        IsochroneStartPoint isp;
        isp.start_id = start_v;
        for (auto &dl : distance_limits)
        {

            if (coordinates[dl].size() > 1)
            {
                auto &points_ = coordinates[dl];
                std::vector<std::array<double, 2>> isochrone_path;
                if (points_.size() > 3)
                {
                    ConvexhullResult hull = convexhull(points_);
                    isochrone_path = concaveman<double, 16>(points_, hull.indices);
                }
                else
                {
                    isochrone_path = {{0, 0}};
                }
                coordinates[dl].clear();
                isp.shape.emplace(dl, isochrone_path);
            }
        }
        isochrone_start_point.push_back(isp);
    }

    result.isochrone = isochrone_start_point;
    result.network = isochrone_network;
    return result;
}

void append_edge_result2(const int64_t &start_v, const int64_t &edge_id, const double &cost_at_node, const double &edge_cost, const double &edge_length, const std::vector<std::array<double, 2>> &geometry,
                         const std::vector<double> &distance_limits,
                         std::vector<IsochroneNetworkEdge2> *isochrone_network, std::unordered_map<double, std::vector<std::array<double, 2>>> &coordinates, const bool &is_reverse)
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
        IsochroneNetworkEdge2 r;
        r.start_id = start_v;
        r.edge = edge_id;
        r.length = edge_length;
        // Full edge
        if (cost_at_target < dl)
        {

            r.start_perc = start_perc;
            r.end_perc = 1.;
            r.start_cost = current_cost;
            r.end_cost = cost_at_target;
            r.geometry = geometry;
            if (is_reverse)
            {
                reverse_isochrone_path(r);
            }
            isochrone_network->push_back(r);
            std::copy(r.geometry.begin(), r.geometry.end(), std::back_inserter(coordinates[dl]));
            break;
        }
        // Partial Edge: (cost_at_target is bigger than the limit, partial edge)
        travel_cost = cost_at_target - dl; // remaining travel cost
        double partial_travel = dl - current_cost;
        r.start_perc = start_perc;
        r.end_perc = start_perc + partial_travel / edge_cost;
        r.start_cost = current_cost;
        r.end_cost = dl;
        start_perc = r.end_perc;
        current_cost = dl;
        if (is_reverse)
        {
            reverse_isochrone_path(r);
        }
        r.geometry = line_substring(r.start_perc, r.end_perc, geometry, edge_length);
        isochrone_network->push_back(r);
        std::copy(r.geometry.begin(), r.geometry.end(), std::back_inserter(coordinates[dl]));
        // A ---------- B
        // 5    7    9  10
    }
}

void reverse_isochrone_path(IsochroneNetworkEdge2 &isochrone_path)
{
    // reverse the percantage
    double nstart_perc = 1. - isochrone_path.end_perc;
    isochrone_path.end_perc = 1. - isochrone_path.start_perc;
    isochrone_path.start_perc = nstart_perc;
    // reversing the cost
    std::swap(isochrone_path.start_cost, isochrone_path.end_cost);
}

Result2 calculate2(
    py::array_t<int64_t> &edge_ids_, py::array_t<int64_t> &sources_,
    py::array_t<int64_t> &targets_, py::array_t<double> &costs_,
    py::array_t<double> &reverse_costs_, py::array_t<double> &length_, std::vector<std::vector<std::array<double, 2>>> &geometry,
    py::array_t<int64_t> start_vertices_,
    py::array_t<double> distance_limits_,
    bool only_minimum_cover_)
{
    auto total_edges = edge_ids_.shape(0);

    auto edge_ids_c = edge_ids_.unchecked<1>();
    auto sources_c = sources_.unchecked<1>();
    auto targets_c = targets_.unchecked<1>();
    auto costs_c = costs_.unchecked<1>();
    auto reverse_costs_c = reverse_costs_.unchecked<1>();
    auto length_c = length_.unchecked<1>();

    auto start_vertices_c = start_vertices_.unchecked<1>();
    auto total_start_vertices = start_vertices_.shape(0);

    auto distance_limits_c = distance_limits_.unchecked<1>();
    auto total_distance_limits = distance_limits_.shape(0);

    bool only_minimum_cover = only_minimum_cover_;
    Edge *data_edges = new Edge[total_edges];

    for (int64_t i = 0; i < total_edges; ++i)
    {
        data_edges[i].id = edge_ids_c(i);
        data_edges[i].source = sources_c(i);
        data_edges[i].target = targets_c(i);
        data_edges[i].cost = costs_c(i);
        data_edges[i].reverse_cost = reverse_costs_c(i);
        data_edges[i].length = length_c(i);
        data_edges[i].geometry = geometry[i];
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
    auto isochrone_points = compute_isochrone2(data_edges, total_edges, start_vertices,
                                               distance_limits, only_minimum_cover);
    return isochrone_points;
}