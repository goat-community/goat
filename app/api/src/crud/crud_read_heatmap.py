import pyximport

pyximport.install()
import json
import math
import os
import time

import geopandas as gpd
import h3
import numpy as np
from rich import print
from shapely.geometry import Polygon

from src.core import heatmap as heatmap_core
from src.core import heatmap_cython
from src.core.config import settings
from src.db.session import legacy_engine
from src.schemas.heatmap import HeatmapMode, HeatmapSettings, HeatmapType
from src.schemas.isochrone import IsochroneDTO, IsochroneMode
from src.utils import create_h3_grid, print_warning, timing


class CRUDBaseHeatmap:
    def __init__(self, db=None, current_user=None):
        self.db = db
        self.current_user = current_user
        self.travel_time_base_path = os.path.join(settings.CACHE_DIR, "traveltime_matrices")
        self.connectivity_base_path = os.path.join(settings.CACHE_DIR, "connectivity_matrices")

    def get_traveltime_path(self, mode: str, profile: str, h6_id: int):
        if np.issubdtype(type(h6_id), int):
            h6_id = f"{h6_id:x}"
        return os.path.join(self.travel_time_base_path, mode, profile, f"{h6_id}.npz")

    def get_connectivity_path(self, mode: str, profile: str):
        return os.path.join(self.connectivity_base_path, mode, profile)

    def get_routing_profile(self, isochrone_dto: IsochroneDTO):
        if isochrone_dto.mode == IsochroneMode.WALKING:
            profile = isochrone_dto.settings.walking_profile.value
        elif isochrone_dto.mode == IsochroneMode.CYCLING:
            profile = isochrone_dto.settings.cycling_profile.value
        else:
            profile = ""

        return profile

    async def read_h3_grids_study_areas(
        self, resolution: int, buffer_size: int, study_area_ids: list[int] = []
    ) -> list[str]:

        """Reads grid ids for study areas.

        Args:
            resolution (int): H3 resolution for grids.
            buffer_size (int): Buffer size in meters.
            study_area_ids (list[int], optional): List of study area ids. Defaults to None and will use all study area.

        Returns:
            list[str]: List of grid ids.
        """

        study_areas_union_geom = (
            gpd.read_postgis(
                f"SELECT geom FROM basic.study_area sa WHERE sa.id = any(array{study_area_ids})",
                legacy_engine,
            )
            .to_crs("EPSG:3857")
            .buffer(buffer_size)
            .to_crs("EPSG:4326")
            .unary_union
        )

        bulk_ids = create_h3_grid(
            study_areas_union_geom, resolution, intersect_with_centroid=False
        )

        return bulk_ids["h3_index"].to_list()


class CRUDReadHeatmap(CRUDBaseHeatmap):
    async def read_opportunity_matrix(
        self, matrix_base_path: str, bulk_ids: list[str], heatmap_config: dict
    ):
        travel_times_dict = {}
        grid_ids_dict = {}
        weight_dict = {}
        opportunity_types = list(heatmap_config.keys())
        opportunity_categories = {}

        for opportunity_type in opportunity_types:
            opportunity_categories[opportunity_type] = list(
                heatmap_config[opportunity_type].keys()
            )
            for cat in opportunity_categories[opportunity_type]:
                travel_times_dict[cat] = []
                grid_ids_dict[cat] = []
                weight_dict[cat] = []

        for bulk_id in np.array(bulk_ids):
            for opportunity_type in opportunity_types:
                try:
                    base_path = os.path.join(matrix_base_path, bulk_id, opportunity_type)
                    categories = np.load(
                        os.path.join(base_path, "categories.npy"),
                        allow_pickle=True,
                    )
                    travel_times = np.load(
                        os.path.join(base_path, "travel_times.npy"),
                        allow_pickle=True,
                    )
                    #todo: check if this is needed. Travel times should not be saved if they are empty
                    if travel_times.size == 0:
                        continue
                    grid_ids = np.load(
                        os.path.join(base_path, "grid_ids.npy"),
                        allow_pickle=True,
                    )
                    weight = np.load(
                        os.path.join(base_path, "weight.npy"),
                        allow_pickle=True,
                    )
                    for cat in opportunity_categories[opportunity_type]:
                        selected_category_index = np.in1d(categories, np.array([cat]))
                        travel_times_dict[cat].extend(travel_times[selected_category_index])
                        grid_ids_dict[cat].extend(grid_ids[selected_category_index])
                        weight_dict[cat].extend(weight[selected_category_index])

                except FileNotFoundError:
                    print(base_path)
                    print(f"File not found for bulk_id {bulk_id}")
                    continue
        for cat in travel_times_dict.keys():
            if grid_ids_dict[cat]:
                grid_ids_dict[cat] = np.concatenate(
                    np.concatenate(grid_ids_dict[cat], axis=None), axis=None
                )
                travel_times_dict[cat] = np.concatenate(
                    np.concatenate(travel_times_dict[cat], axis=None), axis=None
                )
                weight_dict[cat] = np.concatenate(
                    np.concatenate(weight_dict[cat], axis=None), axis=None
                )
            else:
                grid_ids_dict[cat] = np.array([], np.int64)
                travel_times_dict[cat] = np.array([], np.int8)
                weight_dict[cat] = np.array([], np.float64)

        return grid_ids_dict, travel_times_dict, weight_dict

    async def read_bulk_ids(self, study_area_ids: list[int]):
        """
        Read list of bulk ids from cache
        """

        bulk_ids_list = []
        for study_area_id in study_area_ids:
            base_path = settings.ANALYSIS_UNIT_PATH
            directory = os.path.join(base_path, str(study_area_id), "h3")
            grids_file_name = os.path.join(directory, "6_grids.npy")
            bulk_ids_list.append(np.load(grids_file_name, allow_pickle=True))

        bulk_ids = []
        for bulk_ids_ in bulk_ids_list:
            for bulk_id in bulk_ids_:
                bulk_ids.append(f"{bulk_id:x}")

        return list(set(bulk_ids))

    @timing
    async def read_heatmap(
        self,
        heatmap_settings: HeatmapSettings,
    ) -> list[dict]:

        # Get buffer size
        # speed = HeatmapBaseSpeed[heatmap_settings.mode.value].value
        # buffer_size = (speed / 3.6) * (heatmap_settings.max_travel_time * 60)

        # Get bulk ids
        start_time = time.time()
        bulk_ids = await self.read_bulk_ids(heatmap_settings.study_area_ids)
        end_time = time.time()
        print(f"Time to read bulk_ids: {end_time - start_time}")

        # Read hexagons
        grids, h_polygons = await self.read_hexagons(
            heatmap_settings.study_area_ids, heatmap_settings.resolution
        )

        # Get heatmap settings
        profile = ""
        
        # Aggregated data does not need a profile
        if heatmap_settings.heatmap_type != HeatmapType.aggregated_data:
            if heatmap_settings.mode == HeatmapMode.walking:
                profile = heatmap_settings.walking_profile.value
            elif heatmap_settings.mode == HeatmapMode.cycling:
                profile = heatmap_settings.cycling_profile.value

        if heatmap_settings.heatmap_type == HeatmapType.connectivity:
            connectivity_heatmaps_sorted, uniques = await self.read_connectivity_heatmaps_sorted(
                bulk_ids, heatmap_settings, profile
            )
            areas = heatmap_cython.sums(connectivity_heatmaps_sorted, uniques)
            areas_reordered = heatmap_cython.reorder_connectivity_heatmaps(
                uniques[0], areas, grids
            )
            quantiles = heatmap_core.quantile_classify(areas_reordered)
            geojson = self.generate_data_final_geojson(
                grids, h_polygons, areas_reordered, quantiles, data_name="area"
            )
        elif heatmap_settings.heatmap_type == HeatmapType.aggregated_data:
            source = heatmap_settings.heatmap_config.source.value
            aggregated_data_heatmaps_sorted, uniques = await self.read_aggregating_data_sorted(
                bulk_ids, heatmap_settings, source
            )
            aggregated_data = heatmap_cython.sums(
                aggregated_data_heatmaps_sorted, uniques
            )
            aggregated_data_reordered = heatmap_cython.reorder_connectivity_heatmaps(
                uniques[0], aggregated_data, grids
            )
            quantiles = heatmap_core.quantile_classify(aggregated_data_reordered)
            geojson = self.generate_data_final_geojson(
                grids,
                h_polygons,
                aggregated_data_reordered,
                quantiles,
                data_name=source,
            )
        else:

            matrix_base_path = os.path.join(
                settings.OPPORTUNITY_MATRICES_PATH, heatmap_settings.mode.value, profile
            )
            # Read travel times and grid ids
            begin = time.time()
            grid_ids, traveltimes, weights = await self.read_opportunity_matrix(
                matrix_base_path=matrix_base_path,
                bulk_ids=bulk_ids,
                heatmap_config=heatmap_settings.heatmap_config,
            )

            end = time.time()
            print(f"Reading matrices took {end - begin} seconds")
            grid_ids = self.convert_grid_ids_to_parent(grid_ids, heatmap_settings.resolution)
            # TODO: Pick right function that correspond the heatmap the user want to calculate
            travel_times_sorted, weights_sorted, uniques = self.sort_and_unique(
                grid_ids, traveltimes, weights
            )  # Resolution 10 inside
            calculations = self.do_calculations(
                travel_times_sorted, weights_sorted, uniques, heatmap_settings
            )
            # TODO: Warning: Study areas should get concatenated
            calculations = self.reorder_calculations(calculations, grids, uniques)
            quantiles = self.create_quantile_arrays(calculations)
            agg_classes = self.calculate_agg_class(quantiles, heatmap_settings.heatmap_config)
            geojson = self.generate_final_geojson(
                grids, h_polygons, calculations, quantiles, agg_classes
            )

        return geojson

    def generate_data_final_geojson(
        self, grids: np.ndarray, h_polygons: np.ndarray, areas: np.ndarray, quantiles: np.ndarray, data_name: str
    ):
        data_name_class = f"{data_name}_class"
        features = []
        for grid, h_polygon, area, quantile in zip(grids, h_polygons, areas, quantiles):
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": int(grid),
                        data_name: round(float(area), 2),
                        data_name_class: int(quantile),
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [h_polygon.tolist()],
                    },
                }
            )
        geojson = {"type": "FeatureCollection", "features": features}
        return geojson

    async def read_connectivity_heatmaps_sorted(
        self, bulk_ids: np.ndarray, heatmap_settings: HeatmapSettings, profile: str
    ) -> dict:
        connectivity_base_path = self.get_connectivity_path(heatmap_settings.mode.value, profile)
        target_resolution = heatmap_settings.resolution
        connectivity_heatmaps = []
        uniques = []
        max_traveltime = heatmap_settings.heatmap_config.max_traveltime
        for bulk_id in bulk_ids:
            file_path = os.path.join(connectivity_base_path, f"{bulk_id}.npz")
            if not os.path.exists(file_path):
                print_warning(f"File {file_path} does not exist")
                continue
            connectivity = np.load(file_path, allow_pickle=True)
            areas = heatmap_cython.get_connectivity_average(connectivity["areas"], max_traveltime)
            grids = heatmap_cython.convert_to_parents(connectivity["grid_ids"], target_resolution)
            connectivity_areas_sorted, unique = heatmap_cython.sort_and_unique_by_grid_ids(
                grids, areas
            )
            connectivity_heatmaps.append(connectivity_areas_sorted)
            uniques.append(unique)
        uniques = heatmap_cython.concatenate_and_fix_uniques_index_order(
            uniques, connectivity_heatmaps
        )
        # uniques = (uniques[0].astype(np.uint64), uniques[1])
        connectivity_heatmaps = np.concatenate(connectivity_heatmaps)
        return connectivity_heatmaps, uniques
    
    def get_aggregating_data_path(self, bulk_id, source: str):
        return os.path.join(settings.AGGREGATING_MATRICES_PATH, bulk_id, f"{source}.npz")
    
    async def read_aggregating_data_sorted(self, bulk_ids, heatmap_settings, source):
        target_resolution = heatmap_settings.resolution
        aggregating_data = []
        uniques = []
        for bulk_id in bulk_ids:
            file_path = self.get_aggregating_data_path(bulk_id, source)
            if not os.path.exists(file_path):
                print_warning(f"File {file_path} does not exist")
                continue
            data = np.load(file_path, allow_pickle=True)
            grids = heatmap_cython.convert_to_parents(data["grid_id"], target_resolution)
            data_sorted, unique = heatmap_cython.sort_and_unique_by_grid_ids(grids, data["value"])
            aggregating_data.append(data_sorted)
            uniques.append(unique)
        uniques = heatmap_cython.concatenate_and_fix_uniques_index_order(
            uniques, aggregating_data
        )
        aggregating_data = np.concatenate(aggregating_data)
        return aggregating_data, uniques

    @timing
    def calculate_agg_class(self, quantiles: dict, heatmap_config: dict):
        """
        Calculate the aggregated class for each grid cell based on the opportunity weights.
        """

        weighted_quantiles = []
        weight_agg = 0
        categories = {}
        for opportunity_categories in heatmap_config.values():
            categories = {**categories, **opportunity_categories}

        for key, quantile in quantiles.items():
            if quantile.size:
                weighted_quantiles.append(quantile * categories[key].get("weight", 1))
            weight_agg += categories[key].get("weight", 1)

        agg_class = np.array(weighted_quantiles).sum(axis=0) / weight_agg
        return agg_class

    @timing
    def sort_and_unique(self, grid_ids: dict, traveltimes: dict, weights: dict):
        """
        Sort grid_ids in order to do calculations on travel times faster.
        Also find the uniques which used as ids (h3 index)

        returing unique is dict[tuple(unique_ids, unique_index)]
        sorted_table is dict[Array[grid_ids, travel_times]]
        """

        travel_times_sorted, weights_sorted, unique = {}, {}, {}
        for op in traveltimes.keys():
            (
                travel_times_sorted[op],
                weights_sorted[op],
                unique[op],
            ) = heatmap_cython.sort_and_unique_by_grid_ids2(
                grid_ids[op], traveltimes[op], weights[op]
            )
        return travel_times_sorted, weights_sorted, unique

    @timing
    def do_calculations(
        self, travel_times_sorted: dict, weights_sorted, uniques: dict, heatmap_settings: dict
    ):
        # TODO: find a better name for this function
        """
        connect the heatmap core calculations to the heatmap method
        """

        method_map = {
            "modified_gaussian": "modified_gaussian_per_grid",
            "combined_cumulative_modified_gaussian": "combined_modified_gaussian_per_grid",
            "connectivity": "connectivity",
            "cumulative": "counts",
            "closest_average": "mins",
        }
        output = {}

        if heatmap_settings.heatmap_type.value == "modified_gaussian":
            for opportunity_type in heatmap_settings.heatmap_config.keys():
                categories = heatmap_settings.heatmap_config[opportunity_type]
                for category in categories:
                    heatmap_config = categories[category]
                    output[category] = heatmap_core.modified_gaussian_per_grid(
                        travel_times_sorted[category],
                        uniques[category],
                        heatmap_config["sensitivity"],
                        heatmap_config["max_traveltime"],
                        weights_sorted[category],
                    )

        elif heatmap_settings.heatmap_type.value == "combined_cumulative_modified_gaussian":
            for opportunity_type in heatmap_settings.heatmap_config.keys():
                categories = heatmap_settings.heatmap_config[opportunity_type]
                for category in categories:
                    heatmap_config = categories[category]
                    output[category] = heatmap_core.combined_modified_gaussian_per_grid(
                        travel_times_sorted[category],
                        uniques[category],
                        heatmap_config["sensitivity"],
                        heatmap_config["max_traveltime"],
                        heatmap_config["static_traveltime"],
                        weights_sorted[category],
                    )
        else:
            method_name = method_map[heatmap_settings.heatmap_type.value]
            method = getattr(heatmap_core, method_name)
            for opportunity_type in heatmap_settings.heatmap_config.keys():
                categories = heatmap_settings.heatmap_config[opportunity_type]
                for category in categories:
                    heatmap_config = categories[category]
                    output[category] = method(
                        travel_times_sorted[category], uniques[category], weights_sorted[category]
                    )

        return output

    @timing
    def quantile_classify(self, calculations):
        """
        For each calculation, classify the values into quantiles

        returns: dict[quantile_index]
        """

        quantile_index = {}
        for key, a in calculations.items():
            quantile_index[key] = heatmap_core.quantile_classify(a)
        return quantile_index

    @timing
    async def read_hexagons(self, study_area_ids: int, resolution: int):
        """
        Read the hexagons from the cache in requested resolution
        returns: grids, polygons
        """
        grids = []
        polygons = []
        base_path = settings.ANALYSIS_UNIT_PATH
        for study_area_id in study_area_ids:
            directory = os.path.join(base_path, str(study_area_id), "h3")
            grids_file_name = os.path.join(directory, f"{resolution}_grids.npy")
            polygons_file_name = os.path.join(directory, f"{resolution}_polygons.npy")
            grids.append(np.load(grids_file_name))
            polygons.append(np.load(polygons_file_name, allow_pickle=True))
        grids, idx = np.unique(np.concatenate(grids), return_index=True)
        polygons = np.concatenate(polygons)[idx]
        return grids, polygons

    @timing
    def convert_grid_ids_to_parent(self, grid_ids: dict, target_resolution: int):
        for key, grid_id in grid_ids.items():
            if not grid_id.size:
                continue
            grid_ids[key] = heatmap_cython.get_h3_parents(grid_id, target_resolution)
        return grid_ids

    @timing
    def tag_uniques_by_parent(self, uniques: dict, target_resolution: int):
        """
        For each unique (hex id) find the parent id in (requested resolution)
        returns: dict[parent_tag]
        """

        parent_tags = {}
        # parent_tag_lambda = lambda grid_id: int(
        #     h3.h3_to_parent(h3.h3_to_string(grid_id), target_resolution), 16
        # )
        parent_tag_lambda = lambda grid_id: h3._cy.parent(grid_id, target_resolution)
        tags = np.vectorize(parent_tag_lambda)
        for key, unique in uniques.items():
            if not unique[0].size:
                parent_tags[key] = np.array([])
                continue
            # parent_tags[key] = tags(unique[0])
            parent_tags[key] = heatmap_cython.get_h3_parents(unique[0], target_resolution)

        return parent_tags

    @timing
    def create_grids_unordered_map(self, grids: np.ndarray):
        """
        Convert grids to unordered map for fast lookup
        """

        indexes = range(grids.size)
        grids_unordered_map = dict(zip(grids, indexes))
        return grids_unordered_map

    def get_calculations_null_array(self, grids):
        return np.full(grids.size, np.nan, np.float32)

    @timing
    def create_grid_pointers(self, grids_unordered_map, parent_tags):
        """
        Pointing each calculation to the corresponding grid
        returns pointers to target hexagons
        """

        return heatmap_cython.create_grid_pointers(grids_unordered_map, parent_tags)

    @timing
    def create_calculation_arrays(self, grids, grid_pointers, calculations):
        """
        each calculation with their grid_pointers can be considered as a sparse array
        This function converts the sparse array to a dense array
        """

        calculation_arrays = {}
        for key, grid_pointer in grid_pointers.items():
            if not grid_pointer.size:
                calculation_arrays[key] = grid_pointer.copy()
                continue
            calculation_arrays[key] = self.get_calculations_null_array(grids)
            mask = grid_pointer != -1
            masked_grid_pointer = grid_pointer[mask]
            calculation_arrays[key][masked_grid_pointer] = calculations[key][mask]
        return calculation_arrays

    @timing
    def create_quantile_arrays(self, calculations):
        """
        Classify each calculation to a quantile
        returns dict[quantile_array]
        """

        quantile_arrays = {}
        for key, calculation in calculations.items():
            quantile_arrays[key] = heatmap_core.quantile_classify(calculation)
        return quantile_arrays

    # @timing
    def reorder_calculations(self, calculations: dict, grids, uniques: dict):
        """
        First we create kind of a sparse array for each calculation
        Then we convert the sparse array to a dense array targeting the hexagon grids
        """

        # Find the target resolution from the first grid
        sample_grid_id = h3.h3_to_string(grids[0])
        target_resolution = h3.h3_get_resolution(sample_grid_id)
        #############################################

        # uniques_parent_tags = self.tag_uniques_by_parent(uniques, target_resolution)
        grids_unordered_map = self.create_grids_unordered_map(grids)
        grid_pointer = self.create_grid_pointers(grids_unordered_map, uniques)
        calculations = self.create_calculation_arrays(grids, grid_pointer, calculations)
        return calculations

    @timing
    def convert_parent_tags_to_geojson(self, parent_tags: dict):
        """
        For testing purposes
        Save the parent tags to geojson file to visualize in QGIS
        """
        tags = set()
        for key, tag in parent_tags.items():
            tags.update(tag)
        hex_tags = np.array([h3.h3_to_string(tag) for tag in tags])

        tags_polygons = [h3.h3_to_geo_boundary(str(tag), True) for tag in hex_tags]
        tags_polygons = [Polygon(polygon) for polygon in tags_polygons]
        # tags_polygons = np.array(tags_polygons)

        hex_polygons = gpd.GeoSeries(tags_polygons, crs="EPSG:4326")
        # write hex_polygons to geojson file
        hex_polygons_data_frame = gpd.GeoDataFrame(hex_polygons, columns=["geometry"])
        hex_polygons_data_frame.to_file("/app/src/cache/hex_polygons.geojson", driver="GeoJSON")

    @timing
    def generate_final_geojson(
        self,
        grid_ids: np.ndarray,
        polygons: np.ndarray,
        calculations: dict,
        quantiles: dict,
        agg_classes: np.ndarray,
    ):
        """
        Generate the final geojson to return to the client
        """
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
                    feature["properties"][key + "_class"] = 0
                    continue
                if np.isnan(calculation[i]):
                    feature["properties"][key] = None
                    feature["properties"][key + "_class"] = 0
                    continue
                feature["properties"][key] = round(float(calculation[i]), 2)
                feature["properties"][key + "_class"] = int(quantiles[key][i])
            features.append(feature)
        geojson["type"] = "FeatureCollection"
        # geojson["crs"] = {"type": "name", "properties": {"name": "EPSG:4326"}}
        geojson["features"] = features
        return geojson


read_heatmap = CRUDReadHeatmap
