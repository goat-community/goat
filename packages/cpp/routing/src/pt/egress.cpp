#include "egress.h"
#include "stop_finder.h"

#include "../data/street_network_loader.h"
#include "../input/request_config.h"
#include "../kernel/dijkstra.h"
#include "../kernel/mode_selector.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace routing::pt
{

    std::vector<Edge> load_egress_edges(
        RequestConfig const &cfg,
        duck::Connection &con,
        nigiri::timetable const &tt,
        std::vector<std::optional<double>> const &transit_costs)
    {
        // Car has no user-supplied speed (per-edge OSM maxspeed governs the
        // routing cost); active modes use the user's speed for distance-to-time
        // conversions and as the off-network walking speed.
        double const egress_speed =
            (cfg.egress_mode == RoutingMode::Car)
                ? input::kCarBufferSpeedKmH
                : ((cfg.egress_speed_km_h > 0.0)
                       ? cfg.egress_speed_km_h
                       : cfg.speed_km_h);
        double egress_max;
        if (cfg.egress_max_cost > 0.0)
        {
            if (cfg.egress_cost_type == CostType::Distance)
                egress_max = cfg.egress_max_cost / (egress_speed * 1000.0 / 60.0);
            else
                egress_max = cfg.egress_max_cost;
        }
        else
        {
            egress_max = cfg.max_cost;
        }

        // Collect reachable stop coordinates and determine the maximum remaining
        // budget across all stops for the spatial buffer.
        std::vector<Point3857> stop_coords;
        double max_remaining_min = 0.0;

        for (auto i = 0U; i < transit_costs.size(); ++i)
        {
            if (!transit_costs[i].has_value())
                continue;
            double const transit_min = *transit_costs[i];
            if (transit_min >= cfg.max_cost)
                continue;

            double const remaining = std::min(
                cfg.max_cost - transit_min, egress_max);
            if (remaining <= 0.0)
                continue;

            max_remaining_min = std::max(max_remaining_min, remaining);

            auto const &coords =
                tt.locations_.coordinates_[nigiri::location_idx_t{i}];
            stop_coords.push_back(
                latlng_to_3857(coords.lat_, coords.lng_));
        }

        if (stop_coords.empty())
            return {};

        // Buffer speed mirrors buffer_distance() in request_config.cpp:
        //   - Car: fixed kCarBufferSpeedKmH (per-edge OSM maxspeed dominates
        //     routing cost, so user speed is meaningless for sizing the load).
        //   - Active modes: user egress_speed × kActiveBufferSpeedMultiplier.
        double const buffer_speed_km_h =
            (cfg.egress_mode == RoutingMode::Car)
                ? input::kCarBufferSpeedKmH
                : egress_speed * input::kActiveBufferSpeedMultiplier;
        double const buffer_m =
            max_remaining_min * (buffer_speed_km_h * 1000.0 / 60.0);
        auto egress_classes = input::valid_classes(cfg.egress_mode);

        bool load_geom = (cfg.catchment_type == CatchmentType::Network) ||
                         (cfg.catchment_type == CatchmentType::Polygon &&
                          cfg.egress_mode != RoutingMode::Car);
        return data::load_edges(
            con, cfg.edge_dir, cfg.node_dir, stop_coords,
            buffer_m, egress_classes, cfg.egress_mode, load_geom);
    }

    std::vector<double> compute_egress_costs(
        SubNetwork const &net,
        std::vector<Edge> &reusable_edges,
        std::vector<int32_t> const &stop_nodes,
        std::vector<std::optional<double>> const &transit_costs,
        RequestConfig const &cfg)
    {
        double const egress_speed_local =
            (cfg.egress_mode == RoutingMode::Car)
                ? input::kCarBufferSpeedKmH
                : ((cfg.egress_speed_km_h > 0.0)
                       ? cfg.egress_speed_km_h
                       : cfg.speed_km_h);
        double egress_max;
        if (cfg.egress_max_cost > 0.0)
        {
            if (cfg.egress_cost_type == CostType::Distance)
                egress_max = cfg.egress_max_cost / (egress_speed_local * 1000.0 / 60.0);
            else
                egress_max = cfg.egress_max_cost;
        }
        else
        {
            egress_max = cfg.max_cost;
        }

        // Build Dijkstra sources: each reachable stop seeded at its transit cost
        // plus the transit→egress transfer penalty.
        // Per-stop egress is capped at min(max_cost - transit, egress_max).
        double const transfer_penalty = cfg.transfer_cost;
        std::vector<std::pair<int32_t, double>> sources;
        sources.reserve(transit_costs.size());

        for (auto i = 0U; i < transit_costs.size(); ++i)
        {
            if (!transit_costs[i].has_value())
                continue;
            int32_t node = (i < stop_nodes.size()) ? stop_nodes[i] : -1;
            if (node < 0 || node >= net.node_count)
                continue;
            double const transit_min = *transit_costs[i] + transfer_penalty;
            double const remaining = std::min(
                cfg.max_cost - transit_min, egress_max);
            if (remaining <= 0.0)
                continue;

            sources.emplace_back(node, transit_min);
        }

        if (sources.empty())
        {
            return std::vector<double>(
                net.node_count, std::numeric_limits<double>::infinity());
        }

        // The overall Dijkstra budget is max_traveltime. Each source starts at
        // its transit cost, so egress walk naturally stays within the remaining
        // budget. The per-stop cap (egress_max_cost) is already enforced by
        // filtering sources above — stops with no remaining budget are excluded.
        double const egress_budget = cfg.max_cost;

        // If egress mode or speed differs from the network's costing, recompute.
        bool const needs_recompute =
            (cfg.egress_mode != cfg.access_mode) ||
            (cfg.egress_speed_km_h > 0.0 &&
             cfg.egress_speed_km_h != cfg.speed_km_h);

        if (needs_recompute && !reusable_edges.empty())
        {
            RequestConfig egress_cfg = cfg;
            egress_cfg.mode = cfg.egress_mode;
            if (cfg.egress_speed_km_h > 0.0)
                egress_cfg.speed_km_h = cfg.egress_speed_km_h;

            // Recompute costs in-place — no copy needed. compute_costs
            // only reads length_m/class_/impedance and overwrites cost/reverse_cost.
            kernel::compute_costs(reusable_edges, egress_cfg);

            std::vector<std::vector<AdjEntry>> adj(net.node_count);
            // Recosted edges from the original load
            for (size_t i = 0; i < reusable_edges.size() && i < net.source.size(); ++i)
            {
                double const c  = reusable_edges[i].cost;
                double const rc = reusable_edges[i].reverse_cost;
                if (c >= 0.0 && c < 99999.0)
                    adj[net.source[i]].push_back({net.target[i], c});
                if (rc >= 0.0 && rc < 99999.0)
                    adj[net.target[i]].push_back({net.source[i], rc});
            }
            // Connector edges added by snap (not in reusable_edges)
            for (size_t i = reusable_edges.size(); i < net.source.size(); ++i)
            {
                double const c  = net.cost[i];
                double const rc = net.reverse_cost[i];
                if (c >= 0.0 && c < 99999.0)
                    adj[net.source[i]].push_back({net.target[i], c});
                if (rc >= 0.0 && rc < 99999.0)
                    adj[net.target[i]].push_back({net.source[i], rc});
            }

            return kernel::dijkstra(adj, sources, egress_budget, /*use_distance=*/false);
        }

        auto adj = kernel::build_adjacency_list(net);
        return kernel::dijkstra(adj, sources, egress_budget, /*use_distance=*/false);
    }

} // namespace routing::pt
