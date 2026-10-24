#pragma once

#include "../types.h"
#include "../input/request_config.h"

#include <nigiri/routing/query.h>
#include <nigiri/timetable.h>

#include "../data/duck.h"
#include <vector>

namespace routing::pt
{

    struct AccessResult
    {
        SubNetwork net;
        std::vector<double> costs;                     // per-node walk cost (minutes)
        std::vector<nigiri::routing::offset> seeds;    // transit seed stops
        std::vector<int32_t> stop_nodes;               // network node per timetable location
        std::vector<Edge> raw_edges;                   // pre-remapped edges for later merging
    };

    // Build the street network, run access Dijkstra, snap timetable stops,
    // and produce RAPTOR seed stops — everything before the transit search.
    AccessResult compute_access(
        RequestConfig const &cfg,
        duck::Connection &con,
        nigiri::timetable const &tt);

} // namespace routing::pt
