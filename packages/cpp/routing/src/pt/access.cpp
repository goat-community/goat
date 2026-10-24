#include "access.h"
#include "stop_finder.h"

#include "../data/h3_util.h"
#include "../data/street_network_loader.h"
#include "../kernel/dijkstra.h"
#include "../kernel/graph_builder.h"
#include "../kernel/mode_selector.h"
#include "../kernel/snap.h"

#include <cmath>
#include <stdexcept>

namespace routing::pt
{

    AccessResult compute_access(
        RequestConfig const &cfg,
        duck::Connection &con,
        nigiri::timetable const &tt)
    {
        RequestConfig access_cfg = cfg;
        access_cfg.mode = cfg.access_mode;
        if (cfg.access_speed_km_h > 0.0)
            access_cfg.speed_km_h = cfg.access_speed_km_h;

        double access_budget;
        if (cfg.access_max_cost > 0.0)
        {
            if (cfg.access_cost_type == CostType::Distance)
            {
                // Convert distance (meters) to time (minutes). Car has no
                // user speed (per-edge maxspeed governs) so we use the
                // package-level constant; active modes use the user's speed.
                double const speed =
                    (cfg.access_mode == RoutingMode::Car)
                        ? input::kCarBufferSpeedKmH
                        : ((cfg.access_speed_km_h > 0.0)
                               ? cfg.access_speed_km_h
                               : cfg.speed_km_h);
                access_budget = cfg.access_max_cost / (speed * 1000.0 / 60.0);
            }
            else
            {
                access_budget = cfg.access_max_cost;
            }
        }
        else
        {
            access_budget = cfg.max_cost;
        }
        access_cfg.max_cost = access_budget;

        double buffer_m = input::buffer_distance(access_cfg);
        auto access_classes = input::valid_classes(cfg.access_mode);

        bool load_geom = (cfg.catchment_type == CatchmentType::Network) ||
                         (cfg.catchment_type == CatchmentType::Polygon &&
                          cfg.access_mode != RoutingMode::Car);
        auto edges = data::load_edges(
            con, cfg.edge_dir, cfg.node_dir, cfg.starting_points,
            buffer_m, access_classes, cfg.access_mode, load_geom);

        if (edges.empty())
            throw std::runtime_error(
                "PT pipeline: no street edges loaded for access leg.");

        kernel::compute_costs(edges, access_cfg);
        auto net = kernel::build_sub_network(edges);
        // edges remain usable after build_sub_network: geometry was
        // std::move'd into EdgeInfo, but compute_costs only reads
        // length_m/class_/impedance fields which are still intact.

        // Snap user origins onto the network.
        auto start_nodes = kernel::snap_origins(
            net, cfg.starting_points, access_cfg);

        std::vector<int32_t> valid_starts;
        for (auto s : start_nodes)
            if (s >= 0)
                valid_starts.push_back(s);

        if (valid_starts.empty())
            throw std::runtime_error(
                "PT pipeline: starting point(s) disconnected from street network.");

        // Snap timetable stops onto the network (same as origins).
        // Pre-filter to stops within the access network extent to avoid
        // passing thousands of distant stops through snap_origins.
        auto all_stop_coords = get_stop_coords_3857(tt);

        double net_min_x = cfg.starting_points[0].x;
        double net_max_x = net_min_x;
        double net_min_y = cfg.starting_points[0].y;
        double net_max_y = net_min_y;
        for (auto const &p : cfg.starting_points)
        {
            net_min_x = std::min(net_min_x, p.x);
            net_max_x = std::max(net_max_x, p.x);
            net_min_y = std::min(net_min_y, p.y);
            net_max_y = std::max(net_max_y, p.y);
        }
        // Ground metres into projected units, or the window drops stops the access
        // leg can actually reach.
        double const net_margin = data::ground_to_mercator(
            buffer_m, std::abs(net_max_y) > std::abs(net_min_y) ? net_max_y
                                                                : net_min_y);
        net_min_x -= net_margin;
        net_min_y -= net_margin;
        net_max_x += net_margin;
        net_max_y += net_margin;

        std::vector<Point3857> nearby_stop_coords;
        std::vector<size_t> nearby_stop_indices;
        for (size_t i = 0; i < all_stop_coords.size(); ++i)
        {
            auto const &p = all_stop_coords[i];
            if (p.x >= net_min_x && p.x <= net_max_x &&
                p.y >= net_min_y && p.y <= net_max_y)
            {
                nearby_stop_coords.push_back(p);
                nearby_stop_indices.push_back(i);
            }
        }

        std::vector<int32_t> snapped(all_stop_coords.size(), -1);
        if (!nearby_stop_coords.empty())
        {
            auto nearby_snapped = kernel::snap_origins(
                net, nearby_stop_coords, access_cfg, kMaxStopSnapDistanceMeters);
            for (size_t j = 0; j < nearby_snapped.size(); ++j)
                snapped[nearby_stop_indices[j]] = nearby_snapped[j];
        }

        // Access Dijkstra — covers both user origins and stop nodes.
        auto adj = kernel::build_adjacency_list(net);
        auto costs = kernel::dijkstra(
            adj, valid_starts, access_budget, /*use_distance=*/false);

        // Build seed stops: transit stops reachable within the access budget.
        // Add transfer_cost to account for access→transit transition time.
        double const transfer_penalty = cfg.transfer_cost;
        std::vector<nigiri::routing::offset> seeds;
        for (size_t i = 0; i < snapped.size(); ++i)
        {
            int32_t node = snapped[i];
            if (node < 0 || node >= net.node_count)
                continue;
            double access_min = costs[node];
            if (std::isinf(access_min) || access_min >= access_budget)
                continue;

            double seed_cost = access_min + transfer_penalty;
            if (seed_cost >= cfg.max_cost)
                continue;

            seeds.push_back(nigiri::routing::offset{
                nigiri::location_idx_t{static_cast<unsigned>(i)},
                nigiri::duration_t{static_cast<int16_t>(
                    static_cast<int>(seed_cost))},
                0U
            });
        }

        return AccessResult{
            std::move(net),
            std::move(costs),
            std::move(seeds),
            std::move(snapped),
            std::move(edges)};
    }

} // namespace routing::pt
