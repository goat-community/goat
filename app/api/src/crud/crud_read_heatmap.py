import asyncio
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
from sqlalchemy.sql.functions import func

from src import crud, schemas
from src.core import heatmap as heatmap_core
from src.core.config import settings
from src.core.heatmap import merge_heatmap_traveltime_objects
from src.core.isochrone import (
    compute_isochrone_heatmap,
    heatmap_multiprocessing,
    prepare_network_isochrone,
)
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
                # Select relevant POI categories
                poi_categories = np.load(
                    os.path.join(matrix_base_path, bulk_id, "categories" + ".npy"),
                    allow_pickle=True,
                )
                travel_times = np.load(
                    os.path.join(matrix_base_path, bulk_id, "travel_times" + ".npy"),
                    allow_pickle=True,
                )
                grid_ids = np.load(
                    os.path.join(matrix_base_path, bulk_id, "grid_ids" + ".npy"),
                    allow_pickle=True,
                )
                for cat in chosen_categories:

                    selected_category_index = np.in1d(poi_categories, np.array([cat]))
                    travel_times_dict[cat].extend(travel_times[selected_category_index])
                    grid_ids_dict[cat].extend(grid_ids[selected_category_index])

            except FileNotFoundError:
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

    async def read_heatmap(
        self,
        heatmap_settings: HeatmapSettings,
    ) -> list[dict]:

        # Get buffer size
        speed = HeatmapBaseSpeed[heatmap_settings.mode.value].value
        buffer_size = (speed / 3.6) * (heatmap_settings.max_travel_time * 60)

        # Get bulk ids
        bulk_ids = await self.read_h3_grids_study_areas(
            resolution=heatmap_settings.resolution,
            buffer_size=buffer_size,
            study_area_ids=heatmap_settings.study_area_ids,
        )
        # Get heatmap settings
        opportunities = heatmap_settings.heatmap_config.keys()
        if heatmap_settings.mode == HeatmapMode.walking:
            profile = heatmap_settings.walking_profile.value
        elif heatmap_settings.mode == HeatmapMode.cycling:
            profile = heatmap_settings.cycling_profile.value

        matrix_base_path = os.path.join(
            settings.OPPORTUNITY_MATRICES_PATH, heatmap_settings.mode.value, profile
        )
        # Read travel times and grid ids
        begin = time.time()
        grid_ids, traveltimes = await self.read_opportunity_matrix(
            matrix_base_path=matrix_base_path, bulk_ids=bulk_ids, chosen_categories=opportunities
        )
        end = time.time()
        print(f"Reading matrices took {end - begin} seconds")

        ## Compile
        # TODO: Pick right function that correspond the heatmap the user want to calculate
        sorted_table, uniques = self.sort_and_unique(grid_ids, traveltimes)  # Resolution 10 inside
        calculations = self.do_calculations(sorted_table, uniques, heatmap_settings)
        grids, h_polygons = await self.read_hexagons(
            heatmap_settings.study_area_ids[0], heatmap_settings.resolution
        )
        # TODO: Warnong: Study areas should get concatenated
        calculation_arrays = self.reorder_calculations(calculations, grids, uniques)

        print()

        # sorted_table, unique = heatmap_core.sort_and_unique_by_grid_ids(grid_ids, traveltimes)
        # mins = heatmap_core.mins(sorted_table, unique)
        ## Run

        # TODO: Aggregate on required resolution
        # Here we need an if condition performing different actions depending on the resolution and analyses unit
        # Inside here we will also get the geometries as the geometries are different depending on the analyses unit

        # await self.aggregate_on_building(merged_df, study_area_ids)
        # grid_ids = matrix_min_travel_time["grid_id"]
        # travel_times = matrix_min_travel_time["travel_time"]

        # # # Get hexagon geometries and convert to GeoDataFrame
        # hex_polygons = lambda hex_id: Polygon(h3.h3_to_geo_boundary(hex_id, geo_json=True))
        # hex_polygons = gpd.GeoSeries(list(map(hex_polygons, matrix_min_travel_time["grid_id"].tolist())), crs="EPSG:4326")
        # gdf=gpd.GeoDataFrame(data={"grid_ids": matrix_min_travel_time["grid_id"], "travel_times": matrix_min_travel_time["travel_time"]}, geometry=hex_polygons)
        # gdf.to_file("test_results.geojson", driver="GeoJSON")
        # print(f"Read study areas: {end - begin}")
        return

    def sort_and_unique(self, grid_ids, traveltimes):
        sorted_table, unique = {}, {}
        for op in traveltimes.keys():
            sorted_table[op], unique[op] = heatmap_core.sort_and_unique_by_grid_ids(
                grid_ids[op], traveltimes[op]
            )
        return sorted_table, unique

    def do_calculations(self, sorted_table, uniques, heatmap_settings):
        # TODO: find a better name for this function
        """
        connect the heatmap core calculations to the heatmap method
        """
        method_map = {
            "gravity": "modified_gaussian_per_grid",
            "connectivity": "connectivity",
            "cumulative": "counts",
            "closest_average": "mins",
        }
        output = {}
        if heatmap_settings.heatmap_type.value == "gravity":
            for key, heatmap_config in heatmap_settings.heatmap_config.items():
                output[key] = heatmap_core.modified_gaussian_per_grid(
                    sorted_table[key],
                    uniques[key],
                    heatmap_config["sensitivity"],
                    heatmap_config["cutoff"],
                )
        else:
            method_name = method_map[heatmap_settings.heatmap_type.value]
            method = getattr(heatmap_core, method_name)
            for key, heatmap_config in heatmap_settings.heatmap_config.items():
                output[key] = method(sorted_table[key], uniques[key])

        return output

    def quantile_classify(self, calculations):
        quantile_index = {}
        for key, a in calculations.items():
            quantile_index[key] = heatmap_core.quantile_classify(a)
        return quantile_index

    # def calculations_to_data_frame(self, uniques, calculations, quantiles):
    #     dataframes = []
    #     for opportunity, unique in uniques.items():
    #         if not unique[0].size:
    #             continue
    #         # TODO: What to do with empty arrays
    #         start_time = time.time()
    #         frame = pd.DataFrame(
    #             data=[unique[0], calculations[opportunity], quantiles[opportunity]]
    #         ).T
    #         end_time = time.time()
    #         print_info(f"converting {opportunity} time: {end_time-start_time} s")
    #         frame.columns = ["id", opportunity, "class"]
    #         dataframes.append(frame)

    #     return dataframes

    # async def read_h3_dataframe(self, study_area_id, resolution):
    #     base_path = "/app/src/cache/analyses_unit/"  # 9222/h3/10
    #     directory = os.path.join(base_path, str(study_area_id), "h3")
    #     file_name = os.path.join(directory, f"{resolution}.geojson")
    #     dataframe = gpd.read_file(file_name)
    #     dataframe["bulk_id"] = dataframe["bulk_id"].apply(int, base=16)
    #     return dataframe

    async def read_hexagons(self, study_area_id: int, resolution: int):
        base_path = "/app/src/cache/analyses_unit/"
        directory = os.path.join(base_path, str(study_area_id), "h3")
        grids_file_name = os.path.join(directory, f"{resolution}_grids.npy")
        polygons_file_name = os.path.join(directory, f"{resolution}_polygons.npy")
        grids = np.load(grids_file_name)
        polygons = np.load(polygons_file_name)
        return grids, polygons

    def tag_uniques_by_parent(self, uniques: dict, target_resolution: int):
        parent_tags = {}
        parent_tag_lambda = lambda grid_id: int(
            h3.h3_to_parent(h3.h3_to_string(grid_id), target_resolution), 16
        )
        tags = np.vectorize(parent_tag_lambda)
        for key, unique in uniques.items():
            if not unique[0].size:
                parent_tags[key] = np.array([])
                continue
            parent_tags[key] = tags(unique[0])

        return parent_tags

    def create_grids_unordered_map(self, grids: dict):
        """
        Convert grids to unordered map for fast lookup
        """
        indexes = range(grids.size)
        grids_unordered_map = dict(zip(grids, indexes))
        return grids_unordered_map

    def get_calculations_null_array(self, grids):
        return np.full(grids.size, np.nan, np.float32)

    def create_grid_pointers(self, grids_unordered_map, parent_tags):
        grid_pointers = {}
        get_id = lambda tag: grids_unordered_map.get(tag, -1)
        for key, parent_tag in parent_tags.items():
            if not parent_tag.size:
                grid_pointers[key] = parent_tag.copy()
                continue
            grid_pointers[key] = np.vectorize(get_id)(parent_tag)
        return grid_pointers

    def create_calculation_arrays(self, grids, grid_pointers, calculations):
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

    def create_quantile_arrays(self, calculations):
        quantile_arrays = {}
        for key, calculation in calculations.items():
            quantile_arrays[key] = heatmap_core.quantile_classify(calculation)
        return quantile_arrays

    def reorder_calculations(self, calculations, grids, uniques):
        """
        Reorder calculations to match the order of grids
        """
        # convert grid_id from int to hex
        sample_grid_id = h3.h3_to_string(grids[0])
        target_resolution = h3.h3_get_resolution(sample_grid_id)
        uniques_parent_tags = self.tag_uniques_by_parent(uniques, target_resolution)
        grids_unordered_map = self.create_grids_unordered_map(grids)
        grid_pointer = self.create_grid_pointers(grids_unordered_map, uniques_parent_tags)
        calculations = self.create_calculation_arrays(grids, grid_pointer, calculations)
        quantiles = self.create_quantile_arrays(calculations)
        return calculations, quantiles

    def convert_parent_tags_to_geojson(self, parent_tags: dict):
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


read_heatmap = CRUDReadHeatmap

# TODO: Remove this and instead write endpoint to test using OpenAPI
def test_heatmap():
    """Test heatmap calculation"""
    db = async_session()
    superuser = asyncio.get_event_loop().run_until_complete(
        CRUDBase(models.User).get_by_key(db, key="id", value=15)
    )
    superuser = superuser[0]
    heatmap_setting = HeatmapSettings(
        mode="walking",
        max_travel_time=20,
        study_area_ids=[
            91620000,
        ],
        resolution=6,
        walking_profile="standard",
        scenario=IsochroneScenario(
            id=1,
            name="Default",
        ),
        analysis_unit="building",
        heatmap_type="closest_average",
        heatmap_config={
            "atm": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "bar": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "gym": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "pub": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "bank": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "cafe": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "fuel": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "park": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "yoga": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "hotel": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "bakery": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "cinema": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "forest": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "museum": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "butcher": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "dentist": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "nursery": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "bus_stop": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "pharmacy": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "post_box": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "fast_food": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "gymnasium": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "nightclub": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "recycling": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "tram_stop": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "playground": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "realschule": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "restaurant": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "car_sharing": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "convenience": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "grundschule": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "hypermarket": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "marketplace": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "post_office": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "supermarket": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "bike_sharing": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "discount_gym": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "kindergarten": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "rail_station": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "subway_entrance": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "charging_station": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "organic_supermarket": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "discount_supermarket": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "general_practitioner": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "swimming_pool_outdoor": {"weight": 1, "max_count": 1, "max_traveltime": 5},
            "hauptschule_mittelschule": {"weight": 1, "max_count": 1, "max_traveltime": 5},
        },
        return_type="geojson",
    )

    crud_heatmap = CRUDReadHeatmap(db=db, current_user=superuser)
    begin = time.time()
    asyncio.get_event_loop().run_until_complete(
        crud_heatmap.read_heatmap(
            heatmap_settings=heatmap_setting,
            # current_user=superuser,
            # study_area_ids=[
            #     91620000,
            #     # 83110000,
            #     # 9184,
            #     # 9263,
            #     # 9274,
            #     # 9186,
            #     # 9188,
            #     # 9361,
            #     # 9362,
            #     # 9363,
            #     # 9461,
            #     # 9462,
            #     # 9463,
            # ],
        )
    )
    end = time.time()
    print(f"Read heatmap: {end - begin}")


if __name__ == "__main__":
    test_heatmap()


#  async def aggregate_on_building(
#         self, grid_ids: dict, indices: dict, study_area_ids: list[int]
#     ):

#         Get buildings for testing. Currently only one study area is supported
#         buildings = await self.db.execute(
#             text(
#                 """
#                 SELECT b.id, ARRAY[ST_X(centroid), ST_Y(centroid)] AS coords
#                 FROM basic.building b, basic.study_area s, LATERAL ST_TRANSFORM(ST_CENTROID(b.geom), 3857) AS centroid
#                 WHERE ST_Intersects(b.geom, s.geom)
#                 AND s.id = :study_area_id
#                 """
#             ),
#             {"study_area_id": study_area_ids[0]},
#         )
#         buildings_points = buildings.fetchall()
#         buildings_ids = [building[0] for building in buildings_points]
#         buildings_points = [building[1] for building in buildings_points]

#         Preliminary solution to get all grids from DB in the future do this outside this function and read from files instead DB
#         all_grid = await self.db.execute(
#             text(
#                 """
#                 SELECT g.id, ST_X(centroid) x, ST_Y(centroid) y
#                 FROM basic.grid_calculation g, basic.study_area s, LATERAL ST_TRANSFORM(ST_CENTROID(g.geom), 3857) AS centroid
#                 WHERE ST_Intersects(g.geom, s.geom)
#                 AND s.id = :study_area_id
#                 """
#             ),
#             {"study_area_id": study_area_ids[0]},
#         )
#         all_grid = all_grid.fetchall()
#         all_grids = np.array([grid[0] for grid in all_grid])
#         x = np.array([grid[1] for grid in all_grid])
#         y = np.array([grid[2] for grid in all_grid])

#         grid_points = np.stack((x, y), axis=1)
#         tree = spatial.KDTree(grid_points)

#         distances, positions = tree.query(
#             buildings_points, k=3, distance_upper_bound=200, workers=-1
#         )
#         indices_all_inf = (distances == np.inf).all(axis=1)
#         distances = distances[np.where(indices_all_inf == False)].tolist()
#         positions = positions[np.where(indices_all_inf == False)].tolist()
#         buildings_ids = np.array(buildings_ids)[np.where(indices_all_inf == False)].tolist()
#         distances[distances == np.inf] = 0
#         distances_flatten = distances.flatten()
#         positions_flatten = positions.flatten()
#         all_grids = np.append(all_grids, np.inf)
#         grid_map = np.take(all_grids, positions_flatten)

#         interpolated = {"building_id": buildings_ids}
#         for category in indices.keys():
#             costs = indices[category]
#             if costs is None:
#                 continue
#             grids = grid_ids[category][0]

#             intersect_grids = np.intersect1d(all_grids, grids, return_indices=True)
#             grids, relevant_indices = intersect_grids[0], intersect_grids[2]
#             costs = costs[relevant_indices]

#             interpolated_values = []
#             for idx, distance in enumerate(distances):
#                 position = positions[idx]
#                 sum_distance = 0
#                 sum_distance_cost = 0
#                 for idx2, idx_grid in enumerate(position):
#                     if distance[idx2] != np.inf:
#                         grid = all_grids[idx_grid]
#                         idx_cost = np.isin(grids, grid).nonzero()
#                         if len(idx_cost[0]) > 0:
#                             idx_cost = idx_cost[0][0]
#                         else:
#                             continue
#                         cost = costs[idx_cost]
#                         distance_times_cost = distance[idx2] * cost
#                         sum_distance += distance[idx2]
#                         sum_distance_cost += distance_times_cost
#                     else:
#                         continue

#                 if sum_distance != 0:
#                     interpolated_value = sum_distance_cost / sum_distance
#                     interpolated_values.append(interpolated_value)
#                 else:
#                     interpolated_values.append(9999999)
#             interpolated[category] = np.array(interpolated_values)

#         building_df = pd.DataFrame(interpolated)
#         building_df.to_sql(
#             "min_traveltime_building_level",
#             legacy_engine,
#             schema="temporal",
#             if_exists="replace",
#             index=False,
#         )
