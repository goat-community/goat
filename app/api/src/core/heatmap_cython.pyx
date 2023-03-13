#cython: language_level=3
import h3
import numpy as np
import cython

def get_h3_parents(h3_array: np.ndarray, int resolution):
    """Get the parent of each H3 index in the array at the given resolution.
    """
    parent: cython.uint64_t
    if h3_array is None:
        return None
    if not h3_array.size:
        return h3_array.copy()
    cache = {}
    out = np.empty(h3_array.size, np.uint64)
    for i , h3_index in enumerate(h3_array):
        parent = cache.get(h3_index, 0)
        if not parent:
            parent = h3._cy.parent(h3_index, resolution)
            cache[h3_index] = parent
        out[i] = parent
        # out[i] = h3._cy.parent(h3_index, resolution)
    return out

def convert_to_parents(h3_array: np.ndarray, int resolution):
    """
    Convert to h3 parent in place.
    """
    if resolution == 10:
        return h3_array
    
    for i in range(h3_array.size):
        h3_array[i] = h3._cy.parent(h3_array[i], resolution)
    return h3_array


def create_grid_pointers(grids_unordered_map:dict, parent_tags:dict):
    """
    Create grid pointers for each grid in the grid map.
    """
    grid_pointers = {}
    get_id = lambda tag: grids_unordered_map.get(tag, -1)
    for key, parent_tag in parent_tags.items():
        parent_tag = parent_tag[0]
        if not parent_tag.size:
            grid_pointers[key] = parent_tag.copy()
            continue
        grid_pointers[key] = np.vectorize(get_id)(parent_tag)
    return grid_pointers


async def read_hexagon(h6_path):
    """
    Read the hexagon file and return the hexagon array.
    """
    hexagon = np.load(h6_path, allow_pickle=True)
    return hexagon

def calculate_areas_from_pixles(travel_time_pixels, max_travel_times):
    areas = np.empty([travel_time_pixels.shape[0], len(max_travel_times)], dtype=np.uint16)
    for i in range(travel_time_pixels.shape[0]):
        for j in range(len(max_travel_times)):
            areas[i, j] = np.sum(travel_time_pixels[i] <= max_travel_times[j])
    
    return areas

# def h3_to_int(h3_array:np.ndarray):
#     """
#     Convert the h3 array to int array.
#     """
#     return np.vectorize(lambda x: h3._cy.stringToH3(x), otypes=['uint64'])(h3_array)


def sort_and_unique_by_grid_ids(grid_ids, travel_times):
    """
    Sort grid_ids in order to do calculations on travel times faster.
    Also find the uniques which used as ids (h3 index)
    """

    sort_index = grid_ids.argsort()
    sorted_data = travel_times[sort_index]
    unique = np.unique(grid_ids[sort_index], return_index=True)
    return sorted_data, unique

# todo: Refactor
def sort_and_unique_by_grid_ids2(grid_ids, travel_times, weights):
    """
    Sort grid_ids in order to do calculations on travel times faster.
    Also find the uniques which used as ids (h3 index)
    """

    sort_index = grid_ids.argsort()
    sorted_travel_times = travel_times[sort_index]
    sorted_weights = weights[sort_index]
    unique = np.unique(grid_ids[sort_index], return_index=True)
    return sorted_travel_times, sorted_weights, unique


def sums(sorted_data, unique):
    """
    Example:
    sorted_data:
        [[0,0,0,1,1,2,2,2,3,3,3,3],
        [1,2,3,4,5,6,7,8,9,10,11,12]]
    unique:
        [0,1,2,3]

    sums:
        [6,10,21,36]

    Consider unique is touples of (unique, index)
    """
    if not sorted_data.size:
        return None
    travel_times = sorted_data
    # Add the last index to the unique index:
    unique_index = np.append(unique[1], sorted_data.shape[0])
    sums = np.empty(unique[1].shape[0], np.float32)
    for i in range(unique_index.shape[0] - 1):
        travel_time = travel_times[unique_index[i] : unique_index[i + 1]]
        sums[i] = np.sum(travel_time)

    return sums

def create_grids_unordered_map(grids: np.ndarray):
    """
    Convert grids to unordered map for fast lookup
    """
    indexes = range(grids.size)
    grids_unordered_map = dict(zip(grids, indexes))
    return grids_unordered_map


def reorder_connectivity_heatmaps(
        uniqus: np.ndarray, areas: np.ndarray, grids: np.ndarray
    ):
    # Find the target resolution from the first grid
    sample_grid_id = h3.h3_to_string(grids[0])
    target_resolution = h3.h3_get_resolution(sample_grid_id)
    grids_unordered_map = create_grids_unordered_map(grids)

    areas_reordered = np.zeros(grids.size, np.float32)
    get_id = lambda tag: grids_unordered_map.get(tag, -1)
    uniques_pointers = np.vectorize(get_id)(uniqus)
    mask = uniques_pointers != -1
    masked_pointers = uniques_pointers[mask]
    areas_reordered[masked_pointers] = areas[mask]
    return areas_reordered


def get_connectivity_average(areas:np.ndarray, int max_traveltime):
    max_traveltime -= 1
    lambda_func = lambda area: np.average(area[:max_traveltime])
    areas_average = np.apply_along_axis(lambda_func, 1, areas)
    return areas_average


def concatenate_and_fix_uniques_index_order(uniques: list[tuple[np.ndarray, np.ndarray]],connectivity_heatmaps: list[np.ndarray]):
    """
    Fix the uniques index order.
    """
    agg_previous_length = 0
    unique_index_fixed = []
    unique_ids = [uniques[i][0] for i in range(len(uniques))]
    for i in range(len(uniques)):
        fixed_indexes = uniques[i][1] + agg_previous_length
        unique_index_fixed.append(fixed_indexes)
        agg_previous_length += connectivity_heatmaps[i].shape[0]
    unique_ids = np.concatenate(unique_ids)
    unique_index_fixed = np.concatenate(unique_index_fixed)
    return (unique_ids, unique_index_fixed)