#pragma once

#include "../types.h"

#include <cstdint>
#include <optional>
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

    // Cover a bounding box (EPSG:3857) expanded by margin.
    SpatialFilter compute_spatial_filter_bbox(duckdb::Connection &con,
                                              double min_x, double min_y,
                                              double max_x, double max_y,
                                              double margin_meters);

    // Cover a polygon (EPSG:3857 ring, open): the res-6 cells overlapping it
    // or holding a vertex, grown by `ring_k` rings, plus the equivalent bbox.
    SpatialFilter compute_spatial_filter_polygon(duckdb::Connection &con,
                                                 std::vector<Point3857> const &ring,
                                                 int ring_k);

} // namespace routing::data
