#pragma once

#include "../types.h"

#include <nigiri/timetable.h>

#include "../data/duck.h"

namespace routing::pt
{

    // Run the full PT pipeline and return the merged ReachabilityField.
    // Called from pipeline.cpp when cfg.mode == PublicTransport.
    ReachabilityField run_pt_pipeline(RequestConfig const &cfg,
                                      duck::Connection &con);

    // Same as above, but also snaps extra_points onto the combined network
    // and returns their node IDs. Used by the matrix to read destination costs.
    // When pre_tt is provided, skips timetable loading (for multi-origin matrix).
    struct PtPipelineResult
    {
        ReachabilityField field;
        std::vector<int32_t> extra_node_ids;
    };

    PtPipelineResult run_pt_pipeline_with_destinations(
        RequestConfig const &cfg,
        duck::Connection &con,
        std::vector<Point3857> const &extra_points,
        nigiri::timetable const *pre_tt = nullptr);

} // namespace routing::pt
