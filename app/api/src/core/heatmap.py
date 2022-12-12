import numpy as np

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