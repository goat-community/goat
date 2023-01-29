import h3
import numpy as np
import cython

def get_h3_parents(h3_array: np.ndarray, int resolution):
    """Get the parent of each H3 index in the array at the given resolution.
    """

    if h3_array is None:
        return None
    if not h3_array.size:
        return h3_array.copy()
    out = np.empty(h3_array.size, np.uint64)
    for i in range(h3_array.size):
        out[i] = h3._cy.parent(h3_array[i], resolution)
    return out


def create_grid_pointers(grids_unordered_map:dict, parent_tags:dict):
    """
    Create grid pointers for each grid in the grid map.
    """
    grid_pointers = {}
    get_id = lambda tag: grids_unordered_map.get(tag, -1)
    for key, parent_tag in parent_tags.items():
        if not parent_tag.size:
            grid_pointers[key] = parent_tag.copy()
            continue
        grid_pointers[key] = np.vectorize(get_id)(parent_tag)
    return grid_pointers