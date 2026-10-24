#include "network_builder.h"

#include "reached_edges.h"

#include <cmath>
#include "../data/duck.h"
#include <iomanip>
#include <sstream>
#include <stdexcept>

namespace routing::output
{

namespace
{
static constexpr char kNetworkFeaturesTempTable[] = "routing_network_features_tmp";

int64_t count_rows(duck::Connection &con, std::string const &table)
{
    auto result = con.Query("SELECT count(*) FROM " + table);
    if (result.HasError())
        throw std::runtime_error("Failed to count rows in " + table + ": " +
                                 result.GetError());
    return result.scalar<int64_t>();
}

// Clip geometry to budget fraction and build WGS84 WKT linestring.
// Returns empty string if the edge should be excluded.
std::string build_clipped_wkt(
    std::vector<Point3857> const &geom,
    double source_cost, double target_cost, double budget)
{
    if (geom.size() < 2)
        return "";

    // Compute total length
    double total_length = 0.0;
    for (size_t i = 0; i + 1 < geom.size(); ++i)
    {
        double dx = geom[i + 1].x - geom[i].x;
        double dy = geom[i + 1].y - geom[i].y;
        total_length += std::sqrt(dx * dx + dy * dy);
    }
    if (total_length <= 0.0)
        return "";

    // Determine clip fraction
    double clip_frac = 1.0;
    bool needs_clip = false;
    if (source_cost <= budget && target_cost > budget && target_cost != source_cost)
    {
        clip_frac = (budget - source_cost) / (target_cost - source_cost);
        needs_clip = true;
    }
    else if (target_cost <= budget && source_cost > budget && source_cost != target_cost)
    {
        // Reverse clip — from the target end
        clip_frac = 1.0 - (budget - target_cost) / (source_cost - target_cost);
        needs_clip = true;
    }
    else if (source_cost > budget && target_cost > budget)
    {
        return "";
    }

    // Walk along geometry, collect EPSG:3857 points up to clip.
    // DuckDB handles the final transform to WGS84.
    double clip_dist = needs_clip ? clip_frac * total_length : total_length;
    bool clip_from_start = (source_cost <= target_cost) || !needs_clip;

    std::ostringstream wkt;
    wkt << std::setprecision(10) << "LINESTRING(";
    bool first = true;
    double agg = 0.0;

    if (clip_from_start)
    {
        // Emit points from start until clip distance
        wkt << geom[0].x << " " << geom[0].y;
        first = false;

        for (size_t i = 0; i + 1 < geom.size(); ++i)
        {
            double dx = geom[i + 1].x - geom[i].x;
            double dy = geom[i + 1].y - geom[i].y;
            double seg_len = std::sqrt(dx * dx + dy * dy);

            if (agg + seg_len >= clip_dist && needs_clip)
            {
                // Interpolate clip point
                double remain = clip_dist - agg;
                double frac = remain / seg_len;
                double cx = geom[i].x + frac * dx;
                double cy = geom[i].y + frac * dy;
                wkt << "," << cx << " " << cy;
                break;
            }

            agg += seg_len;
            wkt << "," << geom[i + 1].x << " " << geom[i + 1].y;
        }
    }
    else
    {
        // Emit points from clip distance to end (reverse direction clip)
        double start_dist = clip_frac * total_length;
        bool started = false;

        for (size_t i = 0; i + 1 < geom.size(); ++i)
        {
            double dx = geom[i + 1].x - geom[i].x;
            double dy = geom[i + 1].y - geom[i].y;
            double seg_len = std::sqrt(dx * dx + dy * dy);

            if (!started && agg + seg_len >= start_dist)
            {
                double remain = start_dist - agg;
                double frac = remain / seg_len;
                double cx = geom[i].x + frac * dx;
                double cy = geom[i].y + frac * dy;
                wkt << cx << " " << cy;
                first = false;
                started = true;
            }

            agg += seg_len;

            if (started)
            {
                wkt << "," << geom[i + 1].x << " " << geom[i + 1].y;
            }
        }
    }

    if (first)
        return ""; // No points emitted

    wkt << ")";
    return wkt.str();
}

} // namespace

std::string const &network_features_table_name()
{
    static std::string const table_name = kNetworkFeaturesTempTable;
    return table_name;
}

int64_t materialize_network_features_table(ReachabilityField const &field,
                                           RequestConfig const &cfg,
                                           duck::Connection &con)
{
    if (!field.network)
        return 0;

    auto const &net = *field.network;
    double budget = cfg.cost_budget();

    con.Query(std::string("DROP TABLE IF EXISTS ") + kNetworkFeaturesTempTable);
    con.Query(std::string("CREATE TEMP TABLE ") + kNetworkFeaturesTempTable +
              " (edge_id BIGINT, step_cost DOUBLE, wkt TEXT)");

    int64_t count = 0;
    {
        duck::Appender appender(con, kNetworkFeaturesTempTable);

        for (size_t i = 0; i < net.source.size(); ++i)
        {
            int32_t s = net.source[i];
            int32_t t = net.target[i];
            if (s < 0 || t < 0 ||
                s >= static_cast<int32_t>(field.costs.size()) ||
                t >= static_cast<int32_t>(field.costs.size()))
                continue;

            double sc = field.costs[s];
            double tc = field.costs[t];
            if (!std::isfinite(sc) && !std::isfinite(tc))
                continue;
            if (std::min(sc, tc) > budget)
                continue;

            // Use edge geometry if available, else straight line between nodes
            auto const &geom = net.edges[i].geometry;
            std::vector<Point3857> const *pts = &geom;
            std::vector<Point3857> fallback;
            if (geom.size() < 2)
            {
                fallback = {net.node_coords[s], net.node_coords[t]};
                pts = &fallback;
            }

            double step_cost = compute_step_cost(std::min(sc, tc), cfg);
            std::string wkt = build_clipped_wkt(*pts, sc, tc, budget);
            if (wkt.empty())
                continue;

            appender.begin_row();
            appender.append(net.edges[i].id);
            appender.append(step_cost);
            appender.append(wkt);
            appender.end_row();
            ++count;
        }
        appender.close();
    }

    if (count == 0)
        return 0;

    // Convert WKT (EPSG:3857) to geometry and transform to WGS84
    std::string upgrade_sql =
        std::string("CREATE TEMP TABLE routing_network_geom AS "
        "SELECT edge_id, step_cost, "
        "ST_Transform(ST_GeomFromText(wkt), 'EPSG:3857', 'OGC:CRS84') AS geometry "
        "FROM ") + kNetworkFeaturesTempTable;

    con.Query("DROP TABLE IF EXISTS routing_network_geom");
    auto result = con.Query(upgrade_sql);
    if (result.HasError())
        throw std::runtime_error("Network geometry conversion failed: " +
                                 result.GetError());

    con.Query(std::string("DROP TABLE ") + kNetworkFeaturesTempTable);
    con.Query(std::string("ALTER TABLE routing_network_geom RENAME TO ") +
              kNetworkFeaturesTempTable);

    return count;
}

} // namespace routing::output
