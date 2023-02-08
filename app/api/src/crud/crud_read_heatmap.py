import pyximport

pyximport.install()
import asyncio
import concurrent.futures
import json
import math
import os
import time
from typing import List

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
from codetiming import Timer
from geoalchemy2.functions import ST_Dump
from rich import print
from scipy import spatial
from shapely.geometry import Polygon
from sqlalchemy.sql import select, text

from src.core import heatmap as heatmap_core
from src.core import heatmap_cython
from src.core.config import settings
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import async_session, legacy_engine, sync_session
from src.resources.enums import RoutingTypes
from src.schemas.heatmap import (
    HeatmapBaseSpeed,
    HeatmapMode,
    HeatmapSettings,
    HeatmapType,
    HeatmapWalkingBulkResolution,
    HeatmapWalkingCalculationResolution,
    ReturnTypeHeatmap,
)
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMode,
    IsochroneOutput,
    IsochroneOutputType,
    IsochroneScenario,
    IsochroneSettings,
    IsochroneStartingPoint,
    IsochroneStartingPointCoord,
)
from src.utils import (
    create_dir,
    delete_dir,
    delete_file,
    print_hashtags,
    print_info,
    print_warning,
    timing,
)

poi_layers = {
    "poi": models.Poi,
    "poi_modified": models.PoiModified,
    "poi_user": models.PoiUser,
}


class CRUDGridCalculation(
    CRUDBase[models.GridCalculation, models.GridCalculation, models.GridCalculation]
):
    pass


# TODO: Refactor code and split into two files. One for precalculation and one for the endpoints.
# TODO: Add more comments


class CRUDBaseHeatmap:
    def __init__(self, db, current_user):
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

    async def read_h3_grids_study_areas(
        self, resolution: int, buffer_size: int, study_area_ids: list[int] = None
    ) -> list[str]:

        """Reads grid ids for study areas.

        Args:
            resolution (int): H3 resolution for grids.
            buffer_size (int): Buffer size in meters.
            study_area_ids (list[int], optional): List of study area ids. Defaults to None and will use all study area.

        Returns:
            list[str]: List of grid ids.
        """

        resolution = 6

        # Get relevant study areas
        if study_area_ids is None:
            statement = select(models.StudyArea.id)
        else:
            statement = select(models.StudyArea.id).where(models.StudyArea.id.in_(study_area_ids))
        study_area_ids = await self.db.execute(statement)
        study_area_ids = study_area_ids.scalars().all()
        print_info(f"Processing will be done for Study area ids: {str(study_area_ids)[1:-1]}")

        # Get buffer size
        buffer_size = buffer_size + h3.edge_length(resolution, "m")

        # # Get unioned study areas
        # # Doing this in Raw SQL because query could not be build with SQLAlchemy ORM
        # TODO: Reduce the amount of grids
        sql_query = text(
            f"""
            SELECT ST_AsGeoJSON(ST_BUFFER(geom::geography, :buffer_size)::geometry) AS geom
            FROM
            ( 
                SELECT (ST_DUMP(geom)).geom AS geom
                FROM basic.study_area sa
                WHERE sa.id = :study_area_id
            ) AS dumped
        """
        )
        union_geoms = [
            self.db.execute(sql_query, {"study_area_id": i, "buffer_size": buffer_size})
            for i in study_area_ids
        ]
        union_geoms = await asyncio.gather(*union_geoms)
        union_geoms = [geom.fetchall() for geom in union_geoms][0]
        union_geoms_json = [json.loads(geom[0]) for geom in union_geoms]

        #  Get all grids for the bulk resolution
        bulk_ids = []
        for geom in union_geoms_json:
            if geom["type"] != "Polygon":
                raise ValueError("Unioned Study area geometries are not a of type polygon.")

            bulk_ids.extend(list(h3.polyfill_geojson(geom, resolution)))

        # kring_buffer = ceil(buffer_size / h3.edge_length(resolution, "m"))
        bulk_ids = list(set(bulk_ids))
        # bulk_ids = set().union(*[set().union(*h3.k_ring_distances(i, kring_buffer)) for i in bulk_ids])
        # Testing grids for the bulk resolution

        # # Get hexagon geometries and convert to GeoDataFrame
        # hex_polygons = lambda hex_id: Polygon(h3.h3_to_geo_boundary(hex_id, geo_json=True))
        # hex_polygons = gpd.GeoSeries(list(map(hex_polygons, bulk_ids)), crs="EPSG:4326")
        # gdf = gpd.GeoDataFrame(data={"bulk_id": bulk_ids}, geometry=hex_polygons, crs="EPSG:4326")
        # gdf.to_file("hex_polygons.geojson", driver="GeoJSON")

        return bulk_ids


class CRUDReadHeatmap(CRUDBaseHeatmap):
    async def prepare_bulk_objs(
        self,
        bulk_resolution: int,
        calculation_resolution: int,
        buffer_size: float,
        study_area_ids: list[int] = None,
    ) -> dict:

        """Created the starting points for the traveltime matrix calculation.

        Args:
            db (AsyncSession): Database session.
            bulk_resolution (int): H3 resolution for the bulk grids.
            calculation_resolution (int): H3 resolution for the calculation grids.
            study_area_ids (list[int], optional): List of study area ids. Defaults to None and will use all study area.

        Raises:
            ValueError: If the bulk resolution is smaller than the calculation resolution.

        Returns:
            dict: Hierarchical structure of starting points for the calculation using the bulk resolution as parent and calculation resolution as children.
        """
        begin = time.time()
        if bulk_resolution >= calculation_resolution:
            raise ValueError(
                "Resolution of parent grid cannot be smaller then resolution of children grid."
            )

        print_hashtags()
        print_info("Preparing starting points for heatmap calculation")

        begin = time.time()
        # Get unioned study areas
        bulk_ids = await self.read_h3_grids_study_areas(
            resolution=bulk_resolution, buffer_size=buffer_size, study_area_ids=study_area_ids
        )
        end = time.time()
        print_info(f"Time to get bulk ids: {end - begin}")

        # Get all grids for the calculation resolution that are children of the bulk resolution
        calculation_objs = {}
        cnt_calculation_ids = 0

        for bulk_id in bulk_ids:
            lons = []
            lats = []
            calculation_ids = h3.h3_to_children(bulk_id, calculation_resolution)
            starting_point_objs = []
            coords = []
            calculation_objs[bulk_id] = {}
            for calculation_id in calculation_ids:
                lat, lon = h3.h3_to_geo(calculation_id)
                coords.append([lon, lat])
                starting_point_objs.append(IsochroneStartingPointCoord(lat=lat, lon=lon))
                lons.append(lon)
                lats.append(lat)
            calculation_objs[bulk_id]["calculation_ids"] = list(calculation_ids)
            calculation_objs[bulk_id]["coords"] = coords
            calculation_objs[bulk_id]["starting_point_objs"] = starting_point_objs
            cnt_calculation_ids += len(calculation_ids)

            # Get buffered extents for grid size
            gdf_starting_points = gpd.points_from_xy(x=lons, y=lats, crs="epsg:4326")
            gdf_starting_points = gdf_starting_points.to_crs(epsg=3395)
            extents = gdf_starting_points.buffer(buffer_size * math.sqrt(2), cap_style=3)
            extents = extents.to_crs(epsg=3857)
            extents = extents.bounds
            extents = extents.tolist()
            calculation_objs[bulk_id]["extents"] = extents
            calculation_objs[bulk_id]["lats"] = lats
            calculation_objs[bulk_id]["lons"] = lons

        end = time.time()
        print_info(f"Number of bulk grids: {len(bulk_ids)}")
        print_info(f"Number of calculation grids: {cnt_calculation_ids}")
        print_info(f"Calculation time: {end - begin} seconds")
        print_hashtags()
        return calculation_objs

    async def read_poi(
        self,
        isochrone_dto: IsochroneDTO,
        table_name: str,
        filter_geoms: List[str],
        data_upload_id: int = None,
        bulk_ids: List[int] = None,
    ) -> pd.DataFrame:
        """Read POIs from database for given filter geoms

        Args:
            isochrone_dto (IsochroneDTO): Settings for the isochrone calculation
            table_name (str): Name of the POI table
            filter_geoms (List[str]): Geometries to filter the POIs
            data_upload_id (int, optional): Upload ids for poi_user. Defaults to None.

        Raises:
            ValueError: If table_name is not poi or poi_user

        Returns:
            POIs (List): Nested list of POIs
        """

        if table_name == "poi":
            sql_query = f"""
                SELECT :bulk_id AS bulk_id, p.uid, p.category, p.name, pixel[1] AS x, pixel[2] AS y
                FROM basic.poi p, LATERAL basic.coordinate_to_pixel(ST_Y(p.geom), ST_X(p.geom), :pixel_resolution) AS pixel
                WHERE ST_Intersects(p.geom, ST_GeomFromText(:filter_geom, 4326))
                ORDER BY p.category
            """
            sql_params = {}
        elif table_name == "poi_user" and data_upload_id is not None:
            sql_query = f"""
                SELECT :bulk_id AS bulk_id, p.uid, p.category, p.name, pixel[1] AS x, pixel[2] AS y
                FROM basic.poi_user p, LATERAL basic.coordinate_to_pixel(ST_Y(p.geom), ST_X(p.geom), :pixel_resolution) AS pixel
                WHERE ST_Intersects(p.geom, ST_GeomFromText(:filter_geom, 4326))
                AND p.data_upload_id = :data_upload_id
                ORDER BY p.category
            """
            sql_params = {"data_upload_id": data_upload_id}

        else:
            raise ValueError(f"Table name {table_name} is not a valid poi table name")

        pois = [
            self.db.execute(
                sql_query,
                sql_params
                | {
                    "bulk_id": bulk_ids[idx],
                    "filter_geom": filter_geom,
                    "pixel_resolution": isochrone_dto.output.resolution,
                },
            )
            for idx, filter_geom in enumerate(filter_geoms)
        ]

        pois = await asyncio.gather(*pois)
        pois = [batch.fetchall() for batch in pois]
        pois_dict = {}
        for idx_bulk, batch in enumerate(pois):
            if len(batch) > 0:
                bulk_id = batch[0][0]
                batch = [poi[1:] for poi in batch]
                pois_dict[bulk_id] = batch
        return pois_dict

    async def get_categories_opportunities(self, heatmap_settings: HeatmapSettings) -> list[str]:
        """Get all categories from the heatmap config

        Args:
            heatmap_settings (HeatmapSettings): Heatmap settings

        Returns:
            list: List of categories
        """
        categories = []
        if heatmap_settings.heatmap_type == HeatmapType.closest:
            for category in heatmap_settings.heatmap_config["opportunity"]["poi"]:
                categories.append(category)

        return categories

    async def read_opportunity_matrix(
        self, matrix_base_path: str, bulk_ids: list[str], chosen_categories
    ):
        travel_times_dict = {}
        grid_ids_dict = {}
        for cat in chosen_categories:
            travel_times_dict[cat] = []
            grid_ids_dict[cat] = []

        for bulk_id in np.array(bulk_ids):
            try:
                base_path = os.path.join(matrix_base_path, bulk_id)
                # Select relevant POI categories
                poi_categories = np.load(
                    os.path.join(base_path, "categories.npy"),
                    allow_pickle=True,
                )
                travel_times = np.load(
                    os.path.join(base_path, "travel_times.npy"),
                    allow_pickle=True,
                )
                grid_ids = np.load(
                    os.path.join(base_path, "grid_ids.npy"),
                    allow_pickle=True,
                )
                for cat in chosen_categories:

                    selected_category_index = np.in1d(poi_categories, np.array([cat]))
                    travel_times_dict[cat].extend(travel_times[selected_category_index])
                    grid_ids_dict[cat].extend(grid_ids[selected_category_index])

            except FileNotFoundError:
                print(base_path)
                print(f"File not found for bulk_id {bulk_id}")
                continue
        for cat in chosen_categories:
            if grid_ids_dict[cat]:
                grid_ids_dict[cat] = np.concatenate(
                    np.concatenate(grid_ids_dict[cat], axis=None), axis=None
                )
                travel_times_dict[cat] = np.concatenate(
                    np.concatenate(travel_times_dict[cat], axis=None), axis=None
                )
            else:
                grid_ids_dict[cat] = np.array([], np.int64)
                travel_times_dict[cat] = np.array([], np.int8)

        return grid_ids_dict, travel_times_dict

    async def read_bulk_ids(self, study_area_ids: list[int]):
        """
        Read list of bulk ids from cache
        """

        bulk_ids_list = []
        for study_area_id in study_area_ids:
            base_path = "/app/src/cache/analyses_unit/"
            directory = os.path.join(base_path, str(study_area_id), "h3")
            grids_file_name = os.path.join(directory, "6_grids.npy")
            bulk_ids_list.append(np.load(grids_file_name, allow_pickle=True))

        bulk_ids = []
        for bulk_ids_ in bulk_ids_list:
            for bulk_id in bulk_ids_:
                bulk_ids.append(f"{bulk_id:x}")

        return bulk_ids

    @timing
    async def read_heatmap(
        self,
        heatmap_settings: HeatmapSettings,
    ) -> list[dict]:

        # Get buffer size
        speed = HeatmapBaseSpeed[heatmap_settings.mode.value].value
        # buffer_size = (speed / 3.6) * (heatmap_settings.max_travel_time * 60)

        # Get bulk ids
        start_time = time.time()
        bulk_ids = await self.read_bulk_ids(heatmap_settings.study_area_ids)
        end_time = time.time()
        print(f"Time to read bulk_ids: {end_time - start_time}")

        # Read hexagons
        grids, h_polygons = await self.read_hexagons(
            heatmap_settings.study_area_ids[0], heatmap_settings.resolution
        )

        # Get heatmap settings
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
            geojson = self.generate_connectivity_final_geojson(
                grids, h_polygons, areas_reordered, quantiles
            )
        else:

            matrix_base_path = os.path.join(
                settings.OPPORTUNITY_MATRICES_PATH, heatmap_settings.mode.value, profile
            )
            # Read travel times and grid ids
            opportunities = heatmap_settings.heatmap_config.keys()
            begin = time.time()
            grid_ids, traveltimes = await self.read_opportunity_matrix(
                matrix_base_path=matrix_base_path,
                bulk_ids=bulk_ids,
                chosen_categories=opportunities,
            )

            end = time.time()
            print(f"Reading matrices took {end - begin} seconds")

            # TODO: Pick right function that correspond the heatmap the user want to calculate
            sorted_table, uniques = self.sort_and_unique(
                grid_ids, traveltimes
            )  # Resolution 10 inside
            calculations = self.do_calculations(sorted_table, uniques, heatmap_settings)
            # TODO: Warnong: Study areas should get concatenated
            calculations = self.reorder_calculations(calculations, grids, uniques)
            quantiles = self.create_quantile_arrays(calculations)
            agg_classes = self.calculate_agg_class(quantiles, heatmap_settings.heatmap_config)
            geojson = self.generate_final_geojson(
                grids, h_polygons, calculations, quantiles, agg_classes
            )

        return geojson

    def generate_connectivity_final_geojson(
        self, grids: np.ndarray, h_polygons: np.ndarray, areas: np.ndarray, quantiles: np.ndarray
    ):
        features = []
        for grid, h_polygon, area, quantile in zip(grids, h_polygons, areas, quantiles):
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": int(grid),
                        "area": round(float(area), 2),
                        "area_class": int(quantile),
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
            connectivity = np.load(file_path, allow_pickle=True)
            areas = heatmap_cython.get_connectivity_average(connectivity["areas"], max_traveltime)
            grids = heatmap_cython.convert_to_parents(connectivity["grid_ids"], target_resolution)
            connectivity_areas_sorted, unique = heatmap_cython.sort_and_unique_by_grid_ids(
                grids, areas
            )
            connectivity_heatmaps.append(connectivity_areas_sorted)
            uniques.append(unique)
        uniques = heatmap_cython.concatenate_and_fix_uniques_index_order(uniques)
        # uniques = (uniques[0].astype(np.uint64), uniques[1])
        connectivity_heatmaps = np.concatenate(connectivity_heatmaps)
        return connectivity_heatmaps, uniques

    def calculate_agg_class(self, quantiles: dict, heatmap_config: dict):
        """
        Calculate the aggregated class for each grid cell based on the opportunity weights.
        """

        weighted_quantiles = []
        weight_agg = 0
        for key, quantile in quantiles.items():
            if quantile.size:
                weighted_quantiles.append(quantile * heatmap_config[key].get("weight", 1))
            weight_agg += heatmap_config[key].get("weight", 1)

        agg_class = np.array(weighted_quantiles).sum(axis=0) / weight_agg
        return agg_class

    @timing
    def sort_and_unique(self, grid_ids: dict, traveltimes: dict):
        """
        Sort grid_ids in order to do calculations on travel times faster.
        Also find the uniques which used as ids (h3 index)

        returing unique is dict[tuple(unique_ids, unique_index)]
        sorted_table is dict[Array[grid_ids, travel_times]]
        """

        sorted_table, unique = {}, {}
        for op in traveltimes.keys():
            # sorted_table[op], unique[op] = heatmap_core.sort_and_unique_by_grid_ids(
            sorted_table[op], unique[op] = heatmap_core.sort_and_unique_by_grid_ids(
                grid_ids[op], traveltimes[op]
            )
        return sorted_table, unique

    @timing
    def do_calculations(self, sorted_table: dict, uniques: dict, heatmap_settings: dict):
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
            for key, heatmap_config in heatmap_settings.heatmap_config.items():
                output[key] = heatmap_core.modified_gaussian_per_grid(
                    sorted_table[key],
                    uniques[key],
                    heatmap_config["sensitivity"],
                    heatmap_config["max_traveltime"],
                )
        elif heatmap_settings.heatmap_type.value == "combined_cumulative_modified_gaussian":
            for key, heatmap_config in heatmap_settings.heatmap_config.items():
                output[key] = heatmap_core.combined_modified_gaussian_per_grid(
                    sorted_table[key],
                    uniques[key],
                    heatmap_config["sensitivity"],
                    heatmap_config["max_traveltime"],
                    heatmap_config["static_traveltime"],
                )
        else:
            method_name = method_map[heatmap_settings.heatmap_type.value]
            method = getattr(heatmap_core, method_name)
            for key, heatmap_config in heatmap_settings.heatmap_config.items():
                output[key] = method(sorted_table[key], uniques[key])

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
    async def read_hexagons(self, study_area_id: int, resolution: int):
        """
        Read the hexagons from the cache in requested resolution
        returns: grids, polygons
        """

        base_path = "/app/src/cache/analyses_unit/"
        directory = os.path.join(base_path, str(study_area_id), "h3")
        grids_file_name = os.path.join(directory, f"{resolution}_grids.npy")
        polygons_file_name = os.path.join(directory, f"{resolution}_polygons.npy")
        grids = np.load(grids_file_name)
        polygons = np.load(polygons_file_name)
        return grids, polygons

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

        uniques_parent_tags = self.tag_uniques_by_parent(uniques, target_resolution)
        grids_unordered_map = self.create_grids_unordered_map(grids)
        grid_pointer = self.create_grid_pointers(grids_unordered_map, uniques_parent_tags)
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
