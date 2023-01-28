from math import exp
from time import time

import numpy as np
from numba import njit


def merge_heatmap_traveltime_objects(traveltimeobjs):
    merged_traveltime_obj = {}
    arr_west = []
    arr_north = []
    arr_zoom = []
    arr_width = []
    arr_height = []
    arr_travel_times = []
    arr_grid_ids = []

    for obj in traveltimeobjs:
        arr_west.extend(obj["west"])
        arr_north.extend(obj["north"])
        arr_zoom.extend(obj["zoom"])
        arr_width.extend(obj["width"])
        arr_height.extend(obj["height"])
        arr_grid_ids.extend(obj["grid_ids"])
        arr_travel_times.extend(obj["travel_times"])

    merged_traveltime_obj["west"] = np.array(arr_west)
    merged_traveltime_obj["north"] = np.array(arr_north)
    merged_traveltime_obj["zoom"] = np.array(arr_zoom)
    merged_traveltime_obj["width"] = np.array(arr_width)
    merged_traveltime_obj["height"] = np.array(arr_height)
    merged_traveltime_obj["grid_ids"] = np.array(arr_grid_ids)
    merged_traveltime_obj["travel_times"] = np.array(arr_travel_times, dtype=object)

    return merged_traveltime_obj


def sort_and_unique_by_grid_ids(grid_ids, travel_times):
    table_ = np.vstack((grid_ids, travel_times))
    table = table_.transpose()
    sorted_table = table[table[:, 0].argsort()]
    unique = np.unique(sorted_table[:, 0], return_index=True)
    return sorted_table, unique


@njit()
def medians(sorted_table, unique):
    if not sorted_table.size:
        return None
    travel_times = sorted_table.transpose()[1]
    unique_index = unique[1]
    medians = np.empty(unique_index.shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        j = i + 1
        travel_time = travel_times[unique_index[i] : unique_index[j]]
        medians[i] = np.median(travel_time)
    else:
        travel_time = travel_times[unique_index[i + 1] :]
        medians[i + 1] = np.median(travel_time)
    return medians


@njit()
def mins(sorted_table, unique):
    if not sorted_table.size:
        return None
    travel_times = sorted_table.transpose()[1]
    unique_index = unique[1]
    mins = np.empty(unique_index.shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        mins[i] = np.min(travel_time)
    else:
        travel_time = travel_times[unique_index[i + 1] :]
        mins[i + 1] = np.min(travel_time)
    return mins


@njit()
def counts(sorted_table, unique):
    if not sorted_table.size:
        return None
    travel_times = sorted_table.transpose()[1]
    unique_index = unique[1]
    counts = np.empty(unique_index.shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        counts[i] = travel_time.shape[0]
    else:
        travel_time = travel_times[unique_index[i + 1] :]
        counts[i + 1] = travel_time.shape[0]
    return counts


@njit()
def averages(sorted_table, unique):
    if not sorted_table.size:
        return None
    travel_times = sorted_table.transpose()[1]
    unique_index = unique[1]
    averages = np.empty(unique_index.shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        averages[i] = np.average(travel_time)
    else:
        travel_time = travel_times[unique_index[i + 1] :]
        averages[i + 1] = np.average(travel_time)
    return averages


@njit
def modified_gaussian_per_grid(sorted_table, unique, sensitivity, cutoff):
    if not sorted_table.size:
        return None
    travel_times = sorted_table.transpose()[1]
    unique_index = unique[1]
    modified_gaussian_per_grids = np.empty(unique_index.shape[0], np.float64)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        sum = 0
        for t in travel_time:
            f = exp(-t * t / sensitivity)
            sum += f
            if sum >= cutoff:
                modified_gaussian_per_grids[i] = 0
                break
        else:
            modified_gaussian_per_grids[i] = sum

    else:
        travel_time = travel_times[unique_index[i + 1] :]
        sum = 0
        for t in travel_time:
            f = exp(-t * t / sensitivity)
            sum += f
            if sum >= cutoff:
                modified_gaussian_per_grids[i] = 0
                break
        else:
            modified_gaussian_per_grids[i] = sum
    return modified_gaussian_per_grids


def quantile_classify(a, NQ=5):
    if a is None:
        return None
    if not a.size:
        return a.copy()
    q = np.arange(1 / NQ, 1, 1 / NQ)
    quantiles = np.quantile(a[a > 0], q)
    out = np.empty(a.size, np.int8)
    out[np.where(a == 0)] = 0
    out[np.where(np.logical_and(np.greater(a, 0), np.less(a, quantiles[0])))] = 1
    out[np.where(a >= quantiles[-1])] = NQ
    for i in range(NQ - 2):
        out[
            np.where(
                np.logical_and(np.greater_equal(a, quantiles[i]), np.less(a, quantiles[i + 1]))
            )
        ] = (i + 2)
    out[np.isnan(a)] = -1

    return out


def test_quantile(n):
    NQ = 5
    a = np.random.random(n) * 120
    a[a < 10] = 0

    start_time = time()
    out = quantile_classify(a, 5)
    end_time = time()
    print(f"quantile for {a.size} elements is: {int((end_time-start_time)*1000)} ms")
    if n <= 100:
        print("Example of output:")
        print(out)
    else:
        for i in range(NQ + 1):
            print(f"count {i}: {np.where(out==i)[0].size}")
            # print(i,np.where(out==i)[0].size)


if __name__ == "__main__":
    test_quantile(10000)
    test_quantile(20)