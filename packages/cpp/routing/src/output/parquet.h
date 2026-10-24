#pragma once

#include "../types.h"

#include "grid_contour_common.h"

#include <string>
#include <vector>

namespace routing::duck { class Connection; }

namespace routing::output
{

// Write Parquet output from a reachability field according to catchment type.
void write_parquet_output(std::vector<ReachabilityField> const &fields,
                          RequestConfig const &cfg,
                          duck::Connection &con);

// SQL/encoding step of the grid-contour parquet pipeline. Lets a caller
// stream per-origin features (built via `append_field_grid_features`)
// without keeping every reachability field in memory at once.
void write_grid_contour_parquet_from_features(
    std::vector<TaggedFeature> const &features,
    RequestConfig const &cfg,
    duck::Connection &con,
    std::string const &output_path);

} // namespace routing::output
