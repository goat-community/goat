#pragma once

#include "../types.h"

#include <nigiri/timetable.h>

#include "../data/duck.h"
#include <optional>
#include <vector>

namespace routing::pt
{

    // Load street edges around RAPTOR-reachable stops for the egress walk leg.
    // Buffer per stop = min(max_traveltime - transit_cost, egress_max_time)
    // converted to meters via egress speed.  The H3 spatial filter uses the
    // maximum remaining budget across all reachable stops.
    std::vector<Edge> load_egress_edges(
        RequestConfig const &cfg,
        duck::Connection &con,
        nigiri::timetable const &tt,
        std::vector<std::optional<double>> const &transit_costs);

    // Multi-source egress Dijkstra seeded at destination stops.
    // Each stop starts at its transit arrival cost; the Dijkstra budget is
    // max_traveltime so per-stop egress naturally stays within
    // min(max_traveltime - transit_cost, egress_max_time).
    std::vector<double> compute_egress_costs(
        SubNetwork const &net,
        std::vector<Edge> &reusable_edges,
        std::vector<int32_t> const &stop_nodes,
        std::vector<std::optional<double>> const &transit_costs,
        RequestConfig const &cfg);

} // namespace routing::pt
