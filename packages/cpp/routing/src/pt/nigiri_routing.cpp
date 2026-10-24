#include "nigiri_routing.h"

#include <nigiri/clasz.h>
#include <nigiri/common/delta_t.h>
#include <nigiri/routing/clasz_mask.h>
#include <nigiri/routing/one_to_all.h>
#include <nigiri/types.h>

#include <algorithm>
#include <limits>
#include <utility>

namespace routing::pt
{

namespace
{

// Map schema transit mode strings to a nigiri clasz_mask_t bitmask.
// An empty transit_modes list means all modes are allowed.
nigiri::routing::clasz_mask_t build_clasz_mask(
    std::vector<std::string> const &modes)
{
    if (modes.empty())
        return nigiri::routing::all_clasz_allowed();

    nigiri::routing::clasz_mask_t mask = 0;
    for (auto const &m : modes)
    {
        if (m == "bus")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kBus);
        else if (m == "tram")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kTram);
        else if (m == "rail")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kHighSpeed)
                  | nigiri::routing::to_mask(nigiri::clasz::kLongDistance)
                  | nigiri::routing::to_mask(nigiri::clasz::kRegional)
                  | nigiri::routing::to_mask(nigiri::clasz::kSuburban);
        else if (m == "subway")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kSubway);
        else if (m == "ferry")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kShip);
        else if (m == "cable_car" || m == "gondola")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kAerialLift);
        else if (m == "funicular")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kFunicular);
        else if (m == "coach")
            mask |= nigiri::routing::to_mask(nigiri::clasz::kCoach);
        // Unknown strings are silently ignored; callers should validate upstream.
    }
    return mask;
}

// Run a single RAPTOR one-to-all search for the given departure time
// and collect per-location costs.
void run_single_departure(
    nigiri::timetable const &tt,
    std::vector<nigiri::routing::offset> const &seed_stops,
    RequestConfig const &cfg,
    int32_t departure_minute,
    nigiri::routing::clasz_mask_t clasz_mask,
    std::vector<std::optional<double>> &results)
{
    nigiri::routing::query q;
    q.start_time_ = nigiri::unixtime_t{
        nigiri::i32_minutes{departure_minute}};
    q.start_ = seed_stops;
    q.max_travel_time_ = nigiri::duration_t{
        static_cast<int16_t>(cfg.max_cost)};
    q.max_transfers_ = static_cast<std::uint8_t>(cfg.max_transfers);
    q.use_start_footpaths_ = true;
    q.allowed_claszes_ = clasz_mask;

    auto state = nigiri::routing::one_to_all<nigiri::direction::kForward>(
        tt, nullptr, q);

    auto const start_time = nigiri::unixtime_t{
        nigiri::i32_minutes{departure_minute}};

    // Only stops this departure reached: `best_` holds each location's best
    // arrival over all rounds, as in the reverse search below, so the per-round
    // scan of get_fastest runs for reached stops only instead of every location
    // of the timetable, once per minute of the window.
    auto const best = state.get_best<0>();
    constexpr auto kInv =
        nigiri::kInvalidDelta<nigiri::direction::kForward>;
    auto const n_locs = tt.n_locations();
    for (auto i = 0U; i < n_locs; ++i)
    {
        if (best[i][0] == kInv)
            continue;
        auto loc = nigiri::location_idx_t{i};
        auto fastest = nigiri::routing::get_fastest_one_to_all_offsets(
            tt, state,
            nigiri::direction::kForward,
            loc,
            start_time,
            static_cast<std::uint8_t>(cfg.max_transfers));

        if (fastest.k_ == std::numeric_limits<std::uint8_t>::max())
            continue;

        double total_minutes = static_cast<double>(fastest.duration_);
        if (total_minutes <= 0.0 || total_minutes > cfg.max_cost)
            continue;

        if (!results[i].has_value() || total_minutes < *results[i])
            results[i] = total_minutes;
    }
}

} // namespace

    std::vector<std::optional<double>> run_raptor(
        nigiri::timetable const &tt,
        std::vector<nigiri::routing::offset> const &seed_stops,
        RequestConfig const &cfg)
    {
        auto const n_locs = tt.n_locations();
        std::vector<std::optional<double>> results(n_locs, std::nullopt);

        if (seed_stops.empty())
            return results;

        auto const clasz_mask = build_clasz_mask(cfg.transit_modes);
        int const window = std::max(0, cfg.departure_window);

        if (window <= 1)
        {
            // Single departure
            run_single_departure(
                tt, seed_stops, cfg,
                static_cast<int32_t>(cfg.departure_time),
                clasz_mask, results);
        }
        else
        {
            // Sweep: run RAPTOR for each minute in the window,
            // keeping the best (minimum) cost per destination.
            for (int offset = 0; offset < window; ++offset)
            {
                int32_t dep = static_cast<int32_t>(cfg.departure_time) + offset;
                run_single_departure(
                    tt, seed_stops, cfg, dep, clasz_mask, results);
            }
        }

        return results;
    }

    std::vector<std::pair<std::uint32_t, double>> run_reverse_raptor(
        nigiri::timetable const &tt,
        std::vector<nigiri::routing::offset> const &seeds,
        std::int64_t arrival_min,
        int max_travel,
        int max_transfers,
        std::vector<std::string> const &transit_modes)
    {
        using namespace nigiri;
        using namespace nigiri::routing;

        std::vector<std::pair<std::uint32_t, double>> out;
        if (seeds.empty())
            return out;

        auto const clasz_mask = build_clasz_mask(transit_modes);
        auto const start_time =
            unixtime_t{i32_minutes{static_cast<int32_t>(arrival_min)}};

        query q;
        q.start_time_ = start_time;
        q.start_ = seeds;
        q.max_travel_time_ = duration_t{static_cast<int16_t>(max_travel)};
        q.max_transfers_ = static_cast<std::uint8_t>(max_transfers);
        q.use_start_footpaths_ = true;
        q.allowed_claszes_ = clasz_mask;

        auto state = one_to_all<direction::kBackward>(tt, nullptr, q);

        // Reached-set extraction. `best_` holds the cumulative best arrival
        // per location across all rounds, so `best_[j] != invalid` is the
        // reached test — one read per location instead of rescanning all
        // (max_transfers + 2) rounds, and we only call get_fastest for stops
        // that were actually reached. (nigiri's station_mark_ can't be used
        // here: it's a per-round working set, cleared each round, so it only
        // reflects the final round — not the cumulative reached set.)
        // Backward durations are negative (departure earlier than the arrival
        // anchor), so negate to recover the positive travel time.
        auto const best = state.get_best<0>();
        constexpr delta_t kInv = kInvalidDelta<direction::kBackward>;
        auto const n_locs = tt.n_locations();
        out.reserve(1024);
        for (auto j = 0U; j < n_locs; ++j)
        {
            if (best[j][0] == kInv)
                continue;
            auto f = get_fastest_one_to_all_offsets(
                tt, state, direction::kBackward, location_idx_t{j}, start_time,
                static_cast<std::uint8_t>(max_transfers));
            if (f.k_ == std::numeric_limits<std::uint8_t>::max())
                continue;
            double const mins = -static_cast<double>(f.duration_);
            if (mins <= 0.0 || mins > max_travel)
                continue;
            out.emplace_back(j, mins);
        }
        return out;
    }

} // namespace routing::pt
