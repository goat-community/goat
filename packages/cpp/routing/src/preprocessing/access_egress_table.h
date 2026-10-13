#pragma once

#include "../types.h"

#include <string>

namespace routing::preprocessing
{

    // Precompute config for a PT access/egress lookup table (one per mode).
    // For every served stop, finds the H3-res-9 cells reachable within
    // `max_min` minutes in `mode` and the minimum cost in integer minutes.
    // The table is mode-agnostic in schema; the mode's speed is baked in.
    struct AccessEgressConfig
    {
        std::string timetable_path; // nigiri timetable (.bin) — the stop set
        std::string edge_dir;       // street-network edge parquet directory
        std::string node_dir;       // street-network node parquet directory
        std::string output_path;    // parquet:
                                    //   (stop_idx UINTEGER, h3_index UBIGINT,
                                    //    cost_minutes UTINYINT)

        RoutingMode mode = RoutingMode::Walking;
        double max_min = 20.0;      // reachability budget (minutes)
        // Per-mode travel speed (km/h), baked into the table. <= 0 → mode
        // default (walk 5, bicycle 15, pedelec 23, car 50). Car cost actually
        // comes from per-edge OSM maxspeed, so its speed only sizes the
        // network-load buffer.
        double speed_km_h = 0.0;
        // Served stops per batch, used only without an extent bound
        // (chunk_max_span_m <= 0): with one, a chunk is a spatial group and
        // its samples are bounded by fold_samples instead.
        int chunk_size = 4000;
        // Largest ground extent (m) of a chunk's stops, along either axis.
        // A chunk loads the street network around all of its stops, so its
        // memory follows the area its stops cover rather than their number:
        // a sparse regional feed fits 4000 stops into a much larger area than
        // a city does. <= 0 → no extent bound: chunk_size chunks in grid
        // order, as before this setting existed. Wider spans reload less of
        // the network across chunks; at 50 km central Paris, the densest
        // feed measured, peaks at ~1.3 GB.
        double chunk_max_span_m = 50000.0;
        // Samples staged before they are folded into cells, between stops.
        // Bounds what one chunk stages however dense its streets and stops
        // are; the result does not depend on it. <= 0 → the built-in default.
        long long fold_samples = 0;
        double spacing_m = 20.0;    // long-edge interpolation sample spacing
    };

    // Build the access/egress lookup table described by `cfg` and write it as a
    // ZSTD parquet to cfg.output_path (parent dirs created as needed).
    // Returns the output path. Throws std::runtime_error on failure.
    //
    // Reuses the routing engine: street-network load → compute_costs (minutes)
    // → SubNetwork → snap → Dijkstra → reached-subgraph sampling → DuckDB H3
    // binning (same method as the hexagon catchment). Stops are processed in
    // spatially sorted batches, each folded into the result incrementally, so
    // peak memory stays bounded to roughly one chunk of raw samples.
    std::string build_access_egress_table(AccessEgressConfig const &cfg);

} // namespace routing::preprocessing
