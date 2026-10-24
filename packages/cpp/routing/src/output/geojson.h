#pragma once

#include "../types.h"

#include "grid_contour_common.h"

#include <string>
#include <vector>

namespace routing::duck { class Connection; }

namespace routing::output
{

// Build GeoJSON output from a reachability field according to catchment type.
std::string build_geojson_output(std::vector<ReachabilityField> const &fields,
                                 RequestConfig const &cfg,
                                 duck::Connection &con);

// SQL/encoding step of the grid-contour pipeline. Lets a caller stream
// per-origin features (built via `append_field_grid_features`) without
// keeping every reachability field in memory at once.
std::string build_grid_contour_geojson_from_features(
    std::vector<TaggedFeature> const &features,
    RequestConfig const &cfg,
    duck::Connection &con);

} // namespace routing::output
