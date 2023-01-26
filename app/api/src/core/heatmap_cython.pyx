import h3
import numpy as np
import cython

def get_h3_parents(h3_array, resolution):
    if h3_array is None:
        return None
    if not h3_array.size:
        return h3_array.copy()
    out = np.empty(h3_array.size, np.uint64)
    for i in range(h3_array.size):
        out[i] = h3._cy.parent(h3_array[i], resolution)
    return out


def create_grid_pointers(grids_unordered_map, parent_tags):
    grid_pointers = {}
    get_id = lambda tag: grids_unordered_map.get(tag, -1)
    for key, parent_tag in parent_tags.items():
        if not parent_tag.size:
            grid_pointers[key] = parent_tag.copy()
            continue
        grid_pointers[key] = np.vectorize(get_id)(parent_tag)
    return grid_pointers

def generate_final_geojson(grid_ids, polygons, calculations, quantiles, agg_classes):
    geojson = {}
    features = []
    for i, grid_id in enumerate(grid_ids):
        feature = {
            "type": "Feature",
            "properties": {
                "id": int(grid_id),
                "agg_class": round(agg_classes[i], 2),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygons[i].tolist()],
            },
        }
        for key, calculation in calculations.items():
            if not calculation.size:
                feature["properties"][key] = None
                feature["properties"][key + "_class"] = -1
                continue
            if np.isnan(calculation[i]):
                feature["properties"][key] = None
                feature["properties"][key + "_class"] = -1
                continue
            feature["properties"][key] = float(calculation[i])
            feature["properties"][key + "_class"] = int(quantiles[key][i])
        features.append(feature)
    geojson["type"] = "FeatureCollection"
    # geojson["crs"] = {"type": "name", "properties": {"name": "EPSG:4326"}}
    geojson["features"] = features
    return geojson
