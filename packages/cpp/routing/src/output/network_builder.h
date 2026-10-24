#pragma once

#include "../types.h"

#include <cstdint>
#include <string>

namespace routing::duck { class Connection; }

namespace routing::output
{

std::string const &network_features_table_name();

int64_t materialize_network_features_table(ReachabilityField const &field,
                                           RequestConfig const &cfg,
                                           duck::Connection &con);

} // namespace routing::output
