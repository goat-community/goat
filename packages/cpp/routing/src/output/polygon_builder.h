#pragma once

#include "../types.h"

#include <cstdint>
#include <string>
#include <vector>

namespace routing::duck { class Connection; }

namespace routing::output
{

std::string const &polygon_features_table_name();

int64_t materialize_polygon_features_table(
    std::vector<ReachabilityField> const &fields,
    RequestConfig const &cfg,
    duck::Connection &con);

} // namespace routing::output
