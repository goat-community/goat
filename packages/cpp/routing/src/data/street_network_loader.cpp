#include "street_network_loader.h"
#include "h3_util.h"

#include "../output/sql_export.h"

#include <cmath>
#include <cstdlib>
#include "duck.h"
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <stdexcept>

namespace routing::data
{

    using routing::output::sql_escape;

    // First column of a DESCRIBE result: the column names of the relation.
    static std::vector<std::string> column_names(duck::Result &describe)
    {
        std::vector<std::string> names;
        while (auto chunk = describe.Fetch())
        {
            auto const col = chunk.column(0);
            for (duck::idx_t row = 0; row < chunk.size(); ++row)
                names.push_back(col.get<std::string>(row));
        }
        return names;
    }

    static bool is_glob_or_file_path(std::string const &path)
    {
        if (path.find('*') != std::string::npos ||
            path.find('?') != std::string::npos)
        {
            return true;
        }
        auto pos = path.rfind(".parquet");
        return pos != std::string::npos && pos + 8 == path.size();
    }

    // A hive-partitioned network names only the considered h3_3 folders: a glob
    // over the whole directory lists every file before pruning, which on a world
    // network over NFS costs tens of seconds per query. Cells without a folder
    // have no data; if none has one, the layout is not partitioned by h3_3.
    static std::string scan_relation(
        std::string const &dir, std::vector<int32_t> const &h3_3_cells)
    {
        std::ostringstream rel;
        if (is_glob_or_file_path(dir))
        {
            rel << "read_parquet('" << sql_escape(dir) << "', hive_partitioning=true)";
            return rel.str();
        }

        std::vector<std::string> parts;
        for (auto cell : h3_3_cells)
        {
            auto part = std::filesystem::path(dir) / ("h3_3=" + std::to_string(cell));
            if (!std::filesystem::is_directory(part))
                continue;
            for (auto const &f : std::filesystem::directory_iterator(part))
            {
                if (f.path().extension() == ".parquet")
                {
                    parts.push_back(sql_escape(part.string()) + "/*.parquet");
                    break;
                }
            }
        }
        if (parts.empty())
        {
            // Use a recursive glob so flat and partitioned layouts are both matched.
            rel << "read_parquet('" << sql_escape(dir) << "/**/*.parquet', hive_partitioning=true)";
            return rel.str();
        }
        rel << "read_parquet([";
        for (size_t i = 0; i < parts.size(); ++i)
            rel << (i ? ", '" : "'") << parts[i] << "'";
        rel << "], hive_partitioning=true)";
        return rel.str();
    }

    static std::string sql_in_list(std::vector<std::string> const &vals)
    {
        std::ostringstream ss;
        ss << "(";
        for (size_t i = 0; i < vals.size(); ++i)
        {
            if (i)
                ss << ",";
            ss << "'" << vals[i] << "'";
        }
        ss << ")";
        return ss.str();
    }

    static std::string sql_int_list(std::vector<int32_t> const &vals)
    {
        std::ostringstream ss;
        ss << "(";
        for (size_t i = 0; i < vals.size(); ++i)
        {
            if (i)
                ss << ",";
            ss << vals[i];
        }
        ss << ")";
        return ss.str();
    }

    static std::vector<Edge> load_edges_impl(
        duck::Connection &con,
        std::string const &edge_dir,
        std::string const &node_dir,
        SpatialFilter const &filter,
        std::vector<std::string> const &valid_classes,
        RoutingMode mode,
        bool load_geometry)
    {
        auto const &h3_3_cells = filter.h3_3_cells;
        auto const &h3_6_cells = filter.h3_6_cells;

        std::vector<Edge> edges;

        std::string parquet_scan = scan_relation(edge_dir, h3_3_cells);
        std::string node_scan = scan_relation(node_dir, h3_3_cells);

        bool has_node_x_3857 = false;
        bool has_node_y_3857 = false;
        bool has_node_h3_3 = false;
        bool has_node_h3_6 = false;
        auto node_schema = con.Query("DESCRIBE SELECT * FROM " + node_scan + " LIMIT 0");
        if (node_schema.HasError())
        {
            throw std::runtime_error(
                "Failed to read node dataset schema: " + node_schema.GetError());
        }
        for (auto const &col_name : column_names(node_schema))
        {
            if (col_name == "x_3857")
            {
                has_node_x_3857 = true;
            }
            else if (col_name == "y_3857")
            {
                has_node_y_3857 = true;
            }
            else if (col_name == "h3_3")
            {
                has_node_h3_3 = true;
            }
            else if (col_name == "h3_6")
            {
                has_node_h3_6 = true;
            }
        }

        // The H3 columns exist to prune a hive-partitioned dataset. An uploaded
        // street network omits them, so every reference to them has to be
        // conditional, and the bbox below narrows those datasets instead.
        bool has_edge_h3_3 = false;
        bool has_edge_h3_6 = false;
        auto edge_schema =
            con.Query("DESCRIBE SELECT * FROM " + parquet_scan + " LIMIT 0");
        if (edge_schema.HasError())
        {
            throw std::runtime_error(
                "Failed to read edge dataset schema: " + edge_schema.GetError());
        }
        for (auto const &col_name : column_names(edge_schema))
        {
            if (col_name == "h3_3")
            {
                has_edge_h3_3 = true;
            }
            else if (col_name == "h3_6")
            {
                has_edge_h3_6 = true;
            }
        }

        std::string node_x_expr;
        std::string node_y_expr;
        if (has_node_x_3857 && has_node_y_3857)
        {
            node_x_expr = "TRY_CAST(x_3857 AS DOUBLE)";
            node_y_expr = "TRY_CAST(y_3857 AS DOUBLE)";
        }
        else
        {
            // Fallback for existing node dumps that only contain HEXEWKB geom.
            node_x_expr = "ST_X(ST_GeomFromHEXEWKB(geom)) * PI()/180.0 * 6378137.0";
            node_y_expr = "LN(TAN(PI()/4.0 + ST_Y(ST_GeomFromHEXEWKB(geom)) * PI()/360.0)) * 6378137.0";
        }

        // Without H3 columns there is nothing to prune on, so narrow by the
        // query's bbox instead: a node reachable from a starting point cannot lie
        // outside it. Comparing the stored columns rather than the projected
        // aliases lets DuckDB skip row groups on their statistics.
        //
        // One bbox over scattered points also holds everything between them,
        // so a point filter then narrows to its own cells as well, derived
        // from the node's coordinates: the same area the H3 columns select on
        // the global network.
        std::string node_bbox_predicate;
        if (filter.bbox)
        {
            bool const stored = has_node_x_3857 && has_node_y_3857;
            auto const &b = *filter.bbox;
            std::ostringstream pred;
            pred << std::setprecision(17)
                 << (stored ? "x_3857" : node_x_expr)
                 << " BETWEEN " << b.min_x << " AND " << b.max_x << " AND "
                 << (stored ? "y_3857" : node_y_expr)
                 << " BETWEEN " << b.min_y << " AND " << b.max_y;
            if (filter.cells_cover_points && !h3_6_cells.empty())
            {
                pred << " AND "
                     << short_h3_6_sql(stored ? "x_3857" : node_x_expr,
                                       stored ? "y_3857" : node_y_expr)
                     << " IN " << sql_int_list(h3_6_cells);
            }
            node_bbox_predicate = pred.str();
        }

        std::ostringstream sql;
        sql << "WITH node_coords AS ("
            << "  SELECT "
            << "    TRY_CAST(id AS BIGINT) AS node_id, "
            << "    " << node_x_expr << " AS x_3857, "
            << "    " << node_y_expr << " AS y_3857 "
            << "  FROM " << node_scan;
        if (has_node_h3_3 && !h3_3_cells.empty())
        {
            sql << " WHERE h3_3 IN " << sql_int_list(h3_3_cells);
            if (has_node_h3_6 && !h3_6_cells.empty())
            {
                sql << " AND h3_6 IN " << sql_int_list(h3_6_cells);
            }
        }
        else if (has_node_h3_6 && !h3_6_cells.empty())
        {
            sql << " WHERE h3_6 IN " << sql_int_list(h3_6_cells);
        }
        else if (!node_bbox_predicate.empty())
        {
            sql << " WHERE " << node_bbox_predicate;
        }
        sql
            << ") "
            // h3_3/h3_6 are deliberately not selected: they are pruning keys, and
            // nothing downstream reads the values.
            << "SELECT e.id, e.source, e.target, e.length_m, e.length_3857, "
            << "class_, impedance_slope, impedance_slope_reverse, "
            << "impedance_surface, maxspeed_forward, maxspeed_backward, "
            << (load_geometry ? "coordinates_3857, " : "")
            << "src_nodes.x_3857 AS source_x, "
            << "src_nodes.y_3857 AS source_y, "
            << "dst_nodes.x_3857 AS target_x, "
            << "dst_nodes.y_3857 AS target_y "
            << "FROM " << parquet_scan << " e "
            << "JOIN node_coords src_nodes ON src_nodes.node_id = e.source "
            << "JOIN node_coords dst_nodes ON dst_nodes.node_id = e.target "
            << "WHERE class_ IN " << sql_in_list(valid_classes);

        if (has_edge_h3_3 && !h3_3_cells.empty())
            sql << " AND h3_3 IN " << sql_int_list(h3_3_cells);
        if (has_edge_h3_6 && !h3_6_cells.empty())
            sql << " AND h3_6 IN " << sql_int_list(h3_6_cells);

        // For active mobility, filter primary roads by speed limit
        if (mode != RoutingMode::Car)
        {
            sql << " AND (class_ != 'primary' OR "
                << "(maxspeed_forward IS NOT NULL AND maxspeed_forward <= 50) OR "
                << "(maxspeed_backward IS NOT NULL AND maxspeed_backward <= 50))";
        }

        auto result = con.Query(sql.str());
        if (result.HasError())
        {
            throw std::runtime_error("DuckDB query failed: " +
                                     result.GetError());
        }

        while (true)
        {
            auto chunk = result.Fetch();
            if (!chunk)
                break;
            if (chunk.size() == 0)
                continue;

            auto const count = chunk.size();
            auto const id_col = chunk.column(0);
            auto const source_col = chunk.column(1);
            auto const target_col = chunk.column(2);
            auto const length_m_col = chunk.column(3);
            auto const length_3857_col = chunk.column(4);
            auto const class_col = chunk.column(5);
            auto const slope_col = chunk.column(6);
            auto const slope_reverse_col = chunk.column(7);
            auto const surface_col = chunk.column(8);
            auto const speed_fwd_col = chunk.column(9);
            auto const speed_back_col = chunk.column(10);
            // coordinates_3857 occupies column 11 when requested, shifting the
            // node coordinates that follow it.
            int col_offset = load_geometry ? 1 : 0;
            auto const source_x_col = chunk.column(11 + col_offset);
            auto const source_y_col = chunk.column(12 + col_offset);
            auto const target_x_col = chunk.column(13 + col_offset);
            auto const target_y_col = chunk.column(14 + col_offset);

            // Typed column pointers (checked against the column's physical type)
            auto const *id_data = id_col.data<int64_t const>();
            auto const *source_data = source_col.data<int64_t const>();
            auto const *target_data = target_col.data<int64_t const>();
            auto const *length_m_data = length_m_col.data<double const>();
            auto const *length_3857_data = length_3857_col.data<double const>();
            auto const *slope_data = slope_col.data<double const>();
            auto const *slope_reverse_data = slope_reverse_col.data<double const>();
            auto const *surface_data = surface_col.data<float const>();
            auto const *speed_fwd_data = speed_fwd_col.data<int16_t const>();
            auto const *speed_back_data = speed_back_col.data<int16_t const>();
            auto const *source_x_data = source_x_col.data<double const>();
            auto const *source_y_data = source_y_col.data<double const>();
            auto const *target_x_data = target_x_col.data<double const>();
            auto const *target_y_data = target_y_col.data<double const>();

            // Geometry: LIST(LIST(DOUBLE)); entries index into the child vector,
            // whose entries index into the grandchild holding the ordinates.
            duck::Vector geom_col;
            duck::Vector geom_pt_col;
            duck::Vector geom_ord_col;
            duckdb_list_entry const *geom_entries = nullptr;
            duckdb_list_entry const *geom_pt_entries = nullptr;
            double const *geom_ord_data = nullptr;
            if (load_geometry)
            {
                geom_col = chunk.column(11);
                geom_entries = geom_col.list_entries();
                geom_pt_col = geom_col.list_child();
                geom_pt_entries = geom_pt_col.list_entries();
                geom_ord_col = geom_pt_col.list_child();
                geom_ord_data = geom_ord_col.data<double const>();
            }

            for (duck::idx_t i = 0; i < count; ++i)
            {
                // An unmeasurable edge is dropped rather than loaded: every
                // cost derived from a non-finite length is non-finite too, and
                // NaN never compares true, so such an edge cannot be traversed
                // anyway — it would only spread NaN through the graph.
                if (!length_m_col.is_valid(i) ||
                    !length_3857_col.is_valid(i) ||
                    !std::isfinite(length_m_data[i]) ||
                    !std::isfinite(length_3857_data[i]))
                    continue;

                Edge e;
                e.id = id_data[i];
                e.source = source_data[i];
                e.target = target_data[i];
                e.length_m = length_m_data[i];
                e.length_3857 = length_3857_data[i];
                e.class_ = std::string(class_col.string_at(i));
                e.impedance_slope = slope_col.is_valid(i) ? slope_data[i] : 0.0;
                e.impedance_slope_reverse = slope_reverse_col.is_valid(i)
                                                ? slope_reverse_data[i]
                                                : 0.0;
                e.impedance_surface = surface_col.is_valid(i)
                                         ? surface_data[i]
                                         : 0.0f;
                e.maxspeed_forward = speed_fwd_col.is_valid(i)
                                        ? speed_fwd_data[i]
                                        : static_cast<int16_t>(0);
                e.maxspeed_backward = speed_back_col.is_valid(i)
                                         ? speed_back_data[i]
                                         : static_cast<int16_t>(0);
                e.source_coord = {source_x_data[i], source_y_data[i]};
                e.target_coord = {target_x_data[i], target_y_data[i]};

                // Parse geometry for active mobility (column 11 when present)
                if (load_geometry && geom_col.is_valid(i))
                {
                    auto const coords = geom_entries[i];
                    e.geometry.reserve(coords.length);
                    for (duck::idx_t k = coords.offset;
                         k < coords.offset + coords.length; ++k)
                    {
                        if (!geom_pt_col.is_valid(k))
                            continue;
                        auto const pt = geom_pt_entries[k];
                        if (pt.length < 2 ||
                            !geom_ord_col.is_valid(pt.offset) ||
                            !geom_ord_col.is_valid(pt.offset + 1))
                            continue;
                        // A single unusable vertex must not fail every
                        // route on the network. A NULL ordinate has no
                        // value to read, and non-finite ordinates poison
                        // every cost computed from the geometry.
                        auto const x = geom_ord_data[pt.offset];
                        auto const y = geom_ord_data[pt.offset + 1];
                        if (!std::isfinite(x) || !std::isfinite(y))
                            continue;
                        e.geometry.push_back({x, y});
                    }
                }
                if (e.geometry.size() < 2)
                    e.geometry = {e.source_coord, e.target_coord};

                e.cost = 0.0;
                e.reverse_cost = 0.0;
                edges.push_back(std::move(e));
            }
        }

        return edges;
    }


    std::vector<Edge> load_edges(
        duck::Connection &con,
        std::string const &edge_dir,
        std::string const &node_dir,
        std::vector<Point3857> const &starting_points,
        double buffer_meters,
        std::vector<std::string> const &valid_classes,
        RoutingMode mode,
        bool load_geometry)
    {
        auto filter = compute_spatial_filter(con, starting_points, buffer_meters);
        return load_edges_impl(con, edge_dir, node_dir, filter,
                               valid_classes, mode, load_geometry);
    }

    std::vector<Edge> load_edges(
        duck::Connection &con,
        std::string const &edge_dir,
        std::string const &node_dir,
        SpatialFilter const &filter,
        std::vector<std::string> const &valid_classes,
        RoutingMode mode,
        bool load_geometry)
    {
        return load_edges_impl(con, edge_dir, node_dir, filter,
                               valid_classes, mode, load_geometry);
    }

} // namespace routing::data
