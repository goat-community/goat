import os
from math import exp
from time import time

import numpy as np
from numba import njit

from src.utils import delete_file

ii32 = np.iinfo(np.int32)
example_weights_max = np.array([ii32.max], dtype=np.float32)


def sort_and_unique_by_grid_ids(grid_ids, travel_times):
    """
    Sort grid_ids in order to do calculations on travel times faster.
    Also find the uniques which used as ids (h3 index)
    """

    table_ = np.vstack((grid_ids, travel_times))
    table = table_.transpose()
    sorted_table = table[table[:, 0].argsort()]
    unique = np.unique(sorted_table[:, 0], return_index=True)
    return sorted_table, unique


@njit()
def medians(travel_times, unique, weights):
    """
    Example:
    travel_times:
        [1,2,3,4,5,6,7,8,9,10,11,12]]
    unique:
        [[0,1,2,3], [0,3,5,8,10]]
    medians:
        [2,4,6,9]

    Consider unique is touples of (unique, index)
    """
    if not travel_times.size:
        return None
    travel_times = travel_times * weights

    # Add the last index to the unique index:
    unique_index = np.append(unique[1], travel_times.shape[0])
    medians = np.empty(unique[1].shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        j = i + 1
        travel_time = travel_times[unique_index[i] : unique_index[j]]
        medians[i] = np.median(travel_time)

    return medians


@njit()
def mins(travel_times, unique, weights):
    """
    Example:
    travel_times:
        [1,2,3,4,5,6,7,8,9,10,11,12]]
    unique:
        [[0,1,2,3], [0,3,5,8,10]]
    mins:
        [1,2,3,4]

    Consider unique is touples of (unique, index)
    """
    if not travel_times.size:
        return None
    travel_times = travel_times * weights

    # Add the last index to the unique index:
    unique_index = np.append(unique[1], travel_times.shape[0])
    mins = np.empty(unique[1].shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        mins[i] = np.min(travel_time)

    return mins


@njit()
def counts(travel_times, unique, weights):
    """
    Example:
    travel_times:
        [1,2,3,4,5,6,7,8,9,10,11,12]]
    unique:
        [[0,1,2,3], [0,3,5,8,10]]
    counts:
        [3,2,3,3]

    Consider unique is touples of (unique, index)
    """
    if not travel_times.size:
        return None
    weights = np.ones(travel_times.shape[0], dtype=np.float32)

    # Add the last index to the unique index:
    unique_index = np.append(unique[1], travel_times.shape[0])
    counts = np.empty(unique[1].shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        # travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        # counts[i] = travel_time.shape[0]
        counts[i] = np.sum(weights[unique_index[i] : unique_index[i + 1]])

    return counts


@njit()
def averages(travel_times, unique, weights):
    """
    Example:
    travel_times:
        [1,2,3,4,5,6,7,8,9,10,11,12]]
    unique:
        [[0,1,2,3], [0,3,5,8,10]]
    averages:
        [2,5,7,10]

    Consider unique is touples of (unique, index)
    """
    if not travel_times.size:
        return None
    travel_times = travel_times * weights

    # Add the last index to the unique index:
    unique_index = np.append(unique[1], travel_times.shape[0])

    averages = np.empty(unique[1].shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        averages[i] = np.average(travel_time)

    return averages


@njit
def combined_modified_gaussian_per_grid(
    travel_times, unique, sensitivity, cutoff, static_traveltime, weights
):
    if not travel_times.size:
        return None

    sensitivity_ = sensitivity / (60 * 60)  # convert sensitivity to minutes
    # Add the last index to the unique index:
    unique_index = np.append(unique[1], travel_times.shape[0])
    combined_modified_gaussian_per_grids = np.empty(unique[1].shape[0], np.float64)
    counter = -1
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        sum = 0.0
        for t in travel_time:
            counter += 1
            if t > cutoff:
                # Assume result is 0
                continue
            if t <= static_traveltime:
                f = 1
            else:
                t = t - static_traveltime
                f = exp(-t * t / sensitivity_)
            sum += f * weights[counter]
        else:
            # Add the sum to the result after loop finished
            combined_modified_gaussian_per_grids[i] = sum

    return combined_modified_gaussian_per_grids


@njit
def modified_gaussian_per_grid(travel_times, unique, sensitivity, cutoff, weights):
    if not travel_times.size:
        return None

    sensitivity_ = sensitivity / (60 * 60)  # convert sensitivity to minutes

    # Add the last index to the unique index:
    unique_index = np.append(unique[1], travel_times.shape[0])
    modified_gaussian_per_grids = np.empty(unique[1].shape[0], np.float64)
    counter = -1
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        sum = 0
        for t in travel_time:
            counter += 1
            if t > cutoff:
                # Assume result is 0
                continue
            f = exp(-t * t / sensitivity_)
            sum += f * weights[counter]
        else:
            modified_gaussian_per_grids[i] = sum

    return modified_gaussian_per_grids


def quantile_borders(a, NQ=5):
    """
    Classify the array into NQ quantiles and returns the borders.
    example:
    a = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    borders is:
        array([ 4.8,  8.6, 12.4, 16.2])
    """
    if a is None:
        return None
    if not a.size:
        return a.copy()

    greater_zero = a > 0

    # Fix for when all values are 0
    if not sum(greater_zero):
        return np.zeros(a.shape, np.int8)

    q = np.arange(1 / NQ, 1, 1 / NQ)
    quantiles = np.quantile(a[greater_zero], q)

    return quantiles


def quantile_classify(a, borders=None, NQ=5):
    """
    Classify the array into NQ quantiles.
    example:
    a = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    borders = np.array([ 4.8,  8.6, 12.4, 16.2])
    quantile is:
        np.array([1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5])
    """
    if a is None:
        return None
    if not a.size:
        return a.copy()

    greater_zero = a > 0

    # Fix for when all values are 0
    if not sum(greater_zero):
        return np.zeros(a.shape, np.int8)

    if borders is None:
        q = np.arange(1 / NQ, 1, 1 / NQ)
        borders = np.quantile(a[greater_zero], q)

    quantiles = borders
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
    out[np.isnan(a)] = 0

    return out


def population_classify(population):
    percentile_population = np.zeros(population.shape)
    percentile_population[population == 0] = 0
    percentile_population[population < -1000] = -5
    percentile_population[(population >= -1000) & (population < -500)] = -4
    percentile_population[(population >= -500) & (population < -200)] = -3
    percentile_population[(population >= -200) & (population < -80)] = -2
    percentile_population[(population >= -80) & (population < 0)] = -1
    percentile_population[(population > 0) & (population <= 80)] = 1
    percentile_population[(population > 80) & (population <= 200)] = 2
    percentile_population[(population > 200) & (population <= 500)] = 3
    percentile_population[(population > 500) & (population <= 1000)] = 4
    percentile_population[population > 1000] = 5
    return percentile_population


def test_quantile_new():
    # Values from 1 to 20
    a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    # other values then a
    b = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40])

    borders = quantile_borders(a)
    results = quantile_classify(b, borders, 5)
    return results


def test_quantile(n):
    NQ = 5
    a = np.random.random(n) * 120
    a[a < 10] = 0

    b = np.random.random(n) * 120
    b[b < 10] = 0

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


def save_traveltime_matrix(bulk_id: int, traveltimeobjs: dict, output_dir: str):
    # Convert to numpy arrays
    for key in traveltimeobjs.keys():
        # Check if str then obj type
        if isinstance(traveltimeobjs[key][0], str):
            traveltimeobjs[key] = np.array(traveltimeobjs[key])
        else:
            traveltimeobjs[key] = np.array(traveltimeobjs[key], dtype=object)

    # Save files into cache folder
    file_name = f"{bulk_id}.npz"
    # Create directory if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_dir = os.path.join(output_dir, file_name)
    delete_file(file_dir)
    # Save to file
    np.savez_compressed(
        file_dir,
        **traveltimeobjs,
    )


def read_population_modified_sql(scenario_id: int):
    sql = f"""
    WITH pop AS
    (
        SELECT p.id, p.population, p.demography, p.geom, sub_study_area_id, building_id
        FROM basic.population p, UNNEST(basic.modified_buildings({scenario_id})) m
        WHERE p.building_id = m.m
    )
    SELECT p.id, CASE WHEN b.edit_type = 'd' THEN -p.population ELSE p.population END AS population,
    p.geom, demography, sub_study_area_id, b.edit_type
    FROM pop p, customer.building_modified b
    WHERE p.building_id = b.building_id
    UNION ALL
    SELECT p.id, p.population, p.geom, NULL, sub_study_area_id, 'n'
    FROM customer.population_modified p
    WHERE p.scenario_id = {scenario_id};
    """

    return sql



