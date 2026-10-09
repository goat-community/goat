#pragma once

#include "../types.h"

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace duckdb
{
    class Connection;
}

namespace routing::data
{

    // Bounding box in EPSG:3857, already expanded by the query's buffer.
    struct Bbox3857
    {
        double min_x;
        double min_y;
        double max_x;
        double max_y;
    };

    // How the loader narrows a network to the area a query can reach. H3 cells
    // prune the hive-partitioned global network; the bbox covers the same area
    // for datasets without H3 columns, such as an uploaded street network.
    struct SpatialFilter
    {
        std::vector<int32_t> h3_3_cells;
        std::vector<int32_t> h3_6_cells;
        std::optional<Bbox3857> bbox;
        // Whether h3_6_cells cover each point's own buffer (point filter),
        // rather than approximating a rectangle (bbox filter). Only then may
        // a network without H3 columns be narrowed by the same cells, derived
        // from its node coordinates — a rectangle's cells cut its border.
        bool cells_cover_points = false;
    };

    // Convert a distance in ground metres to EPSG:3857 units. Mercator is conformal
    // but not equidistant — one unit equals cos(latitude) ground metres — so a
    // ground-metre distance applied straight to a projected coordinate falls short
    // by a third at 48°N and by half at 60°N. ``y_3857`` selects the latitude;
    // pass the coordinate furthest from the equator to err towards a wider margin.
    double ground_to_mercator(double ground_meters, double y_3857);

    // Cover all starting points within the given buffer distance: the short H3
    // cell IDs (res 3 + res 6) plus the equivalent bbox. Uses the DuckDB H3
    // community extension (INSTALL + LOAD is the caller's responsibility).
    SpatialFilter compute_spatial_filter(duckdb::Connection &con,
                                         std::vector<Point3857> const &points,
                                         double buffer_meters);

    // SQL for the short res-6 cell id of a point given as EPSG:3857 x/y
    // expressions — the value the global network stores in its h3_6 column,
    // derived the same way compute_spatial_filter derives its cells.
    std::string short_h3_6_sql(std::string const &x_3857,
                               std::string const &y_3857);

    // Cover a bounding box (EPSG:3857) expanded by margin.
    SpatialFilter compute_spatial_filter_bbox(duckdb::Connection &con,
                                              double min_x, double min_y,
                                              double max_x, double max_y,
                                              double margin_meters);

} // namespace routing::data
