#include "duckdb_setup.h"

#include "duck.h"
#include <stdexcept>

namespace routing::data
{

    void ensure_required_extensions_loaded(duck::Connection &con)
    {
        auto install_h3 = con.Query("INSTALL h3 FROM community");
        if (install_h3.HasError())
            throw std::runtime_error("Failed to install DuckDB H3 extension: " +
                                     install_h3.GetError());
        auto load_h3 = con.Query("LOAD h3");
        if (load_h3.HasError())
            throw std::runtime_error("Failed to load DuckDB H3 extension: " +
                                     load_h3.GetError());

        auto install_spatial = con.Query("INSTALL spatial");
        if (install_spatial.HasError())
            throw std::runtime_error("Failed to install DuckDB spatial extension: " +
                                     install_spatial.GetError());
        auto load_spatial = con.Query("LOAD spatial");
        if (load_spatial.HasError())
            throw std::runtime_error("Failed to load DuckDB spatial extension: " +
                                     load_spatial.GetError());

        // DuckDB 2.0 spatial refuses ST_Transform (and friends) until the axis
        // order is stated. False is the pre-2.0 behaviour and matches the
        // Python side (goatlib.storage.ducklake.GEOMETRY_ALWAYS_XY); the
        // EPSG:3857 -> CRS84 transforms used here come out the same either way.
        auto set_xy = con.Query("SET geometry_always_xy = false");
        if (set_xy.HasError())
            throw std::runtime_error("Failed to set geometry_always_xy: " +
                                     set_xy.GetError());
    }

} // namespace routing::data
