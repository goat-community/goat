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

    // Split points into spatially compact groups, for a computation whose
    // points are independent and can be run one group at a time.
    //
    // A network load covers the area around all of its points, so its memory
    // follows the area they span, not how many there are: one load for points
    // scattered across a region holds most of the region. Points are binned
    // by H3 res-6 cell, the cells are taken in H3 index order (which keeps
    // neighbours together), and a group is closed when the next cell would
    // stretch its points beyond `max_span_m` of ground along either axis. A
    // cell is never split. `max_span_m <= 0` returns a single group.
    //
    // Returns indices into `points`, every index exactly once; within a cell
    // the input order is kept. Uses the DuckDB H3 community extension (INSTALL
    // + LOAD is the caller's responsibility).
    std::vector<std::vector<size_t>> group_points_by_extent(
        duckdb::Connection &con,
        std::vector<Point3857> const &points,
        double max_span_m);

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
