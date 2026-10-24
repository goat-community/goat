#pragma once

namespace routing::duck { class Connection; }

namespace routing::data
{

    // Install + load the DuckDB extensions every pipeline relies on: the h3
    // community extension and spatial, and state the spatial axis order
    // DuckDB 2.0 insists on. Idempotent; throws on failure.
    void ensure_required_extensions_loaded(duck::Connection &con);

} // namespace routing::data
