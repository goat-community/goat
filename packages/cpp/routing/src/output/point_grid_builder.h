#pragma once

#include "../types.h"

#include <cstdint>
#include <string>

namespace routing::duck { class Connection; }

namespace routing::output
{

std::string const &point_grid_features_table_name();

// Materialize a temp table of grid points snapped to the reachable street
// network.  Each input point is assigned the cost of the nearest reached
// edge (within snap_distance) plus a walking penalty for the gap.
// The input points are read from cfg.grid_points_path (parquet with columns
// id, x_3857, y_3857).
int64_t materialize_point_grid_features_table(ReachabilityField const &field,
                                              RequestConfig const &cfg,
                                              duck::Connection &con);

} // namespace routing::output
