#include "h3_util.h"

#include <algorithm>
#include <cmath>
#include <duckdb.hpp>
#include <iomanip>
#include <set>
#include <sstream>
#include <stdexcept>

namespace routing::data
{

    // ── Mercator → WGS 84 ──────────────────────────────────────────────────

    static constexpr double kEarthRadius = 6378137.0;
    static constexpr double kH3Res6EdgeLengthM = 3724.5; // average edge length

    static double to_longitude(double x)
    {
        return x / kEarthRadius * (180.0 / M_PI);
    }

    static double to_latitude(double y)
    {
        return (2.0 * std::atan(std::exp(y / kEarthRadius)) - M_PI / 2.0) *
               (180.0 / M_PI);
    }

    double ground_to_mercator(double ground_meters, double y_3857)
    {
        double const lat_rad = to_latitude(y_3857) * M_PI / 180.0;
        double const scale = std::max(std::cos(lat_rad), 0.05);
        return ground_meters / scale;
    }

    // ── H3 cell resolver ───────────────────────────────────────────────────

    SpatialFilter compute_spatial_filter(duckdb::Connection &con,
                                   std::vector<Point3857> const &points,
                                   double buffer_meters)
    {
        if (points.empty())
            return {};

        // k = number of hex rings needed to cover the buffer distance
        int k = static_cast<int>(std::ceil(buffer_meters / kH3Res6EdgeLengthM)) + 1;
        if (k < 1)
            k = 1;

        // The bbox equivalent of the cell cover, for datasets without H3
        // columns. One res-6 edge length of slack keeps it from being tighter
        // than the cell disk, which rounds k up and adds a ring.
        Bbox3857 box{points[0].x, points[0].y, points[0].x, points[0].y};
        for (auto const &pt : points)
        {
            box.min_x = std::min(box.min_x, pt.x);
            box.min_y = std::min(box.min_y, pt.y);
            box.max_x = std::max(box.max_x, pt.x);
            box.max_y = std::max(box.max_y, pt.y);
        }
        double const furthest_y =
            std::abs(box.max_y) > std::abs(box.min_y) ? box.max_y : box.min_y;
        double const margin =
            ground_to_mercator(buffer_meters + kH3Res6EdgeLengthM, furthest_y);
        box.min_x -= margin;
        box.min_y -= margin;
        box.max_x += margin;
        box.max_y += margin;

        // Build a VALUES clause with all starting points as (lat, lng)
        std::ostringstream values;
        values << std::setprecision(17);
        for (size_t i = 0; i < points.size(); ++i)
        {
            if (i)
                values << ",";
            double lat = to_latitude(points[i].y);
            double lon = to_longitude(points[i].x);
            values << "(" << lat << "," << lon << ")";
        }

        // Bit masks for short H3 encoding (matching PostgreSQL basic.to_short_h3_*)
        // to_short_h3_3: (val & 0x000ffff000000000) >> 36
        // to_short_h3_6: (val & 0x000fffffff000000) >> 24
        constexpr uint64_t kMaskH3_3 = 0x000ffff000000000ULL;
        constexpr uint64_t kMaskH3_6 = 0x000fffffff000000ULL;

        std::ostringstream sql;
        sql << "WITH pts(lat, lng) AS (VALUES " << values.str() << "), "
            << "cells AS ("
            << "  SELECT DISTINCT unnest("
            << "    h3_grid_disk(h3_latlng_to_cell(lat, lng, 6), " << k << ")"
            << "  ) AS cell FROM pts"
            << ") "
            << "SELECT "
            << "  ((cell::bigint & " << kMaskH3_3 << ") >> 36)::int AS h3_3, "
            << "  ((cell::bigint & " << kMaskH3_6 << ") >> 24)::int AS h3_6 "
            << "FROM cells";

        auto result = con.Query(sql.str());
        if (result->HasError())
        {
            throw std::runtime_error(
                "H3 cell computation failed: " + result->GetError() +
                " | SQL: " + sql.str());
        }

        SpatialFilter filter;
        std::set<int32_t> h3_3_set, h3_6_set;

        for (size_t row = 0; row < result->RowCount(); ++row)
        {
            auto v3 = result->GetValue(0, row).GetValue<int32_t>();
            auto v6 = result->GetValue(1, row).GetValue<int32_t>();
            h3_3_set.insert(v3);
            h3_6_set.insert(v6);
        }

        filter.h3_3_cells.assign(h3_3_set.begin(), h3_3_set.end());
        filter.h3_6_cells.assign(h3_6_set.begin(), h3_6_set.end());
        filter.bbox = box;
        return filter;
    }

    SpatialFilter compute_spatial_filter_bbox(duckdb::Connection &con,
                                              double min_x, double min_y,
                                              double max_x, double max_y,
                                              double margin_meters)
    {
        // Expand by the margin, in projected units so it is the ground distance
        // the caller asked for.
        double const furthest_y =
            std::abs(max_y) > std::abs(min_y) ? max_y : min_y;
        double const margin = ground_to_mercator(margin_meters, furthest_y);
        min_x -= margin;
        min_y -= margin;
        max_x += margin;
        max_y += margin;

        // Convert corners to WGS84
        double lon0 = to_longitude(min_x);
        double lat0 = to_latitude(min_y);
        double lon1 = to_longitude(max_x);
        double lat1 = to_latitude(max_y);

        // Build WKT polygon for the bbox
        std::ostringstream wkt;
        wkt << std::setprecision(17)
            << "POLYGON((" << lon0 << " " << lat0 << ","
            << lon1 << " " << lat0 << ","
            << lon1 << " " << lat1 << ","
            << lon0 << " " << lat1 << ","
            << lon0 << " " << lat0 << "))";

        constexpr uint64_t kMaskH3_3 = 0x000ffff000000000ULL;
        constexpr uint64_t kMaskH3_6 = 0x000fffffff000000ULL;

        std::ostringstream sql;
        sql << "WITH cells AS ("
            << "  SELECT DISTINCT unnest("
            << "    h3_polygon_wkt_to_cells('" << wkt.str() << "', 6::integer)"
            << "  ) AS cell"
            << ") "
            << "SELECT "
            << "  ((cell::bigint & " << kMaskH3_3 << ") >> 36)::int AS h3_3, "
            << "  ((cell::bigint & " << kMaskH3_6 << ") >> 24)::int AS h3_6 "
            << "FROM cells";

        auto result = con.Query(sql.str());
        if (result->HasError())
        {
            throw std::runtime_error(
                "H3 bbox cell computation failed: " + result->GetError());
        }

        SpatialFilter filter;
        std::set<int32_t> h3_3_set, h3_6_set;

        for (size_t row = 0; row < result->RowCount(); ++row)
        {
            auto v3 = result->GetValue(0, row).GetValue<int32_t>();
            auto v6 = result->GetValue(1, row).GetValue<int32_t>();
            h3_3_set.insert(v3);
            h3_6_set.insert(v6);
        }

        filter.h3_3_cells.assign(h3_3_set.begin(), h3_3_set.end());
        filter.h3_6_cells.assign(h3_6_set.begin(), h3_6_set.end());
        filter.bbox = Bbox3857{min_x, min_y, max_x, max_y};
        return filter;
    }

    SpatialFilter compute_spatial_filter_polygon(duckdb::Connection &con,
                                                 std::vector<Point3857> const &ring,
                                                 int ring_k)
    {
        if (ring.empty())
            return {};

        Bbox3857 box{ring[0].x, ring[0].y, ring[0].x, ring[0].y};
        std::ostringstream vertices;
        vertices << std::setprecision(17);
        for (size_t i = 0; i < ring.size(); ++i)
        {
            box.min_x = std::min(box.min_x, ring[i].x);
            box.min_y = std::min(box.min_y, ring[i].y);
            box.max_x = std::max(box.max_x, ring[i].x);
            box.max_y = std::max(box.max_y, ring[i].y);
            if (i)
                vertices << ",";
            vertices << "(" << to_latitude(ring[i].y) << ","
                     << to_longitude(ring[i].x) << ")";
        }

        std::ostringstream sql;
        sql << std::setprecision(17)
            << "WITH pts(lat, lng) AS (VALUES " << vertices.str() << "), "
            << "seed AS (SELECT h3_latlng_to_cell(lat, lng, 6) AS c FROM pts";
        // A ring of fewer than three points has no interior.
        if (ring.size() >= 3)
        {
            sql << " UNION SELECT unnest(h3_polygon_wkt_to_cells_experimental('POLYGON((";
            for (size_t i = 0; i <= ring.size(); ++i)
            {
                auto const &p = ring[i % ring.size()];
                if (i)
                    sql << ",";
                sql << to_longitude(p.x) << " " << to_latitude(p.y);
            }
            sql << "))', 6, 'CONTAINMENT_OVERLAPPING'))";
        }
        constexpr uint64_t kMaskH3_3 = 0x000ffff000000000ULL;
        constexpr uint64_t kMaskH3_6 = 0x000fffffff000000ULL;
        sql << "), cells AS (SELECT DISTINCT unnest(h3_grid_disk(c, " << ring_k
            << ")) AS cell FROM seed) "
            << "SELECT ((cell::bigint & " << kMaskH3_3 << ") >> 36)::int AS h3_3, "
            << "((cell::bigint & " << kMaskH3_6 << ") >> 24)::int AS h3_6 "
            << "FROM cells";

        auto result = con.Query(sql.str());
        if (result->HasError())
            throw std::runtime_error(
                "H3 polygon cell computation failed: " + result->GetError());

        SpatialFilter filter;
        std::set<int32_t> h3_3_set, h3_6_set;
        for (size_t row = 0; row < result->RowCount(); ++row)
        {
            h3_3_set.insert(result->GetValue(0, row).GetValue<int32_t>());
            h3_6_set.insert(result->GetValue(1, row).GetValue<int32_t>());
        }
        filter.h3_3_cells.assign(h3_3_set.begin(), h3_3_set.end());
        filter.h3_6_cells.assign(h3_6_set.begin(), h3_6_set.end());

        // The bbox equivalent, for datasets without H3 columns: as wide as the
        // ring growth, plus one edge length because overlapping cells reach
        // past the polygon.
        double const furthest_y =
            std::abs(box.max_y) > std::abs(box.min_y) ? box.max_y : box.min_y;
        double const margin =
            ground_to_mercator((ring_k + 1) * kH3Res6EdgeLengthM, furthest_y);
        filter.bbox = Bbox3857{box.min_x - margin, box.min_y - margin,
                               box.max_x + margin, box.max_y + margin};
        return filter;
    }

} // namespace routing::data
