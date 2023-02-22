import pyximport

pyximport.install()
import asyncio
import json
import math
import os
import time
from itertools import compress
from typing import List

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
from codetiming import Timer
from geoalchemy2.functions import ST_Dump
from geoalchemy2.shape import to_shape
from pyproj import Geod
from rich import print
from scipy import spatial
from shapely.geometry import Polygon
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, text
from sqlalchemy.sql.functions import func

from src import crud, schemas
from src.core import heatmap as heatmap_core
from src.core import heatmap_cython
from src.core.config import settings
from src.core.heatmap import merge_heatmap_traveltime_objects
from src.core.isochrone import (
    compute_isochrone_heatmap,
    heatmap_multiprocessing,
    prepare_network_isochrone,
)
from src.crud.base import CRUDBase
from src.crud.crud_read_heatmap import CRUDBaseHeatmap
from src.db import models
from src.db.session import async_session, engine, legacy_engine, sync_session
from src.jsoline import jsolines
from src.resources.enums import RoutingTypes
from src.schemas.heatmap import (
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
    get_random_string,
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


# TODO: Add more comments
class CRUDComputeHeatmap(CRUDBaseHeatmap):   
    
    async def get_bulk_ids(
        self,
        bulk_resolution: int,
        calculation_resolution: int,
        buffer_size: float,
        speed: float,
        travel_time: float,
        study_area_ids: list[int] = None,
    ) -> list[str]:
        
        buffer_size = speed * (travel_time * 60)
        
        if bulk_resolution >= calculation_resolution:
            raise ValueError(
                "Resolution of parent grid cannot be smaller then resolution of children grid."
            )

        # Get unioned study areas
        bulk_ids = await self.read_h3_grids_study_areas(
            resolution=bulk_resolution, buffer_size=buffer_size, study_area_ids=study_area_ids
        )
        return bulk_ids
    
    async def create_calculation_object(
        self,
        calculation_resolution: int,
        buffer_size: float,
        bulk_id: str,
    ) -> dict:
        calculation_obj = {}
        lons = []
        lats = []
        calculation_ids = h3.h3_to_children(bulk_id, calculation_resolution)
        starting_point_objs = []
        coords = []
        calculation_obj[bulk_id] = {}
        for calculation_id in calculation_ids:
            lat, lon = h3.h3_to_geo(calculation_id)
            coords.append([lon, lat])
            starting_point_objs.append(IsochroneStartingPointCoord(lat=lat, lon=lon))
            lons.append(lon)
            lats.append(lat)
        calculation_obj[bulk_id]["calculation_ids"] = list(calculation_ids)
        calculation_obj[bulk_id]["coords"] = coords
        calculation_obj[bulk_id]["starting_point_objs"] = starting_point_objs
        cnt_calculation_ids = len(calculation_ids)

        # Get buffered extents for grid size
        gdf_starting_points = gpd.points_from_xy(x=lons, y=lats, crs="epsg:4326")
        gdf_starting_points = gdf_starting_points.to_crs(epsg=3395)
        extents = gdf_starting_points.buffer(buffer_size * math.sqrt(2), cap_style=3)
        extents = extents.to_crs(epsg=3857)
        extents = extents.bounds
        extents = extents.tolist()
        calculation_obj[bulk_id]["extents"] = extents
        calculation_obj[bulk_id]["lats"] = lats
        calculation_obj[bulk_id]["lons"] = lons
        
        return calculation_obj
        
    
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

    async def compute_traveltime_active_mobility(
        self, isochrone_dto: IsochroneDTO, calculation_objs: dict
    ):
        """Computes the traveltime for active mobility in matrix style.

        Args:
            isochrone_dto (IsochroneDTO): Settings for the isochrone calculation
            calculation_objs (dict): Hierarchical structure of starting points for the calculation using the bulk resolution as parent and calculation resolution as children.
        """
        random_table_prefix = get_random_string(10)
        starting_time = time.time()

        cnt = 0
        cnt_sections = len(calculation_objs)

        routing_profile = None
        if isochrone_dto.mode.value == IsochroneMode.WALKING.value:
            routing_profile = (
                isochrone_dto.mode.value + "_" + isochrone_dto.settings.walking_profile.value
            )
        elif isochrone_dto.mode.value == IsochroneMode.CYCLING.value:
            routing_profile = (
                isochrone_dto.mode.value + "_" + isochrone_dto.settings.cycling_profile.value
            )

        for key, obj in calculation_objs.items():
            starting_time_section = time.time()
            starting_time_network_preparation = time.time()
            cnt += 1
            cnt_theoretical_starting_points = len(obj["starting_point_objs"])
            # Check if there are no starting points
            if len(obj["starting_point_objs"]) == 0:
                print_info(
                    f"No starting points for section [bold magenta]{str(cnt)}[/bold magenta]"
                )
                continue

            # Prepare starting points using routing network
            db = async_session()
            starting_ids = await db.execute(
                func.basic.heatmap_prepare_artificial(
                    obj["lons"],
                    obj["lats"],
                    isochrone_dto.settings.travel_time * 60,
                    isochrone_dto.settings.speed,
                    isochrone_dto.scenario.modus.value,
                    isochrone_dto.scenario.id,
                    routing_profile,
                    True,
                    obj["calculation_ids"],
                    random_table_prefix,
                )
            )
            await db.commit()
            starting_ids = starting_ids.scalars().all()
            await db.close()

            valid_extents = []
            valid_starting_ids = []
            valid_starting_point_objs = []
            valid_calculation_ids = []
            for i in starting_ids:
                starting_id = i[0]
                grid_calculation_id = i[1]
                idx = obj["calculation_ids"].index(grid_calculation_id)
                valid_extents.append(obj["extents"][idx])
                valid_starting_ids.append(starting_id)
                valid_starting_point_objs.append(obj["starting_point_objs"][idx])
                valid_calculation_ids.append(grid_calculation_id)

            grid_ids = np.array(valid_calculation_ids)
            extents = np.array(valid_extents)
            starting_point_objs = np.array(valid_starting_point_objs)
            starting_ids = np.array(valid_starting_ids)
            isochrone_dto.starting_point.input = starting_point_objs

            # Read network
            db = async_session()
            network = await crud.isochrone.read_network(
                db=db,
                obj_in=isochrone_dto,
                current_user=self.current_user,
                isochrone_type=schemas.isochrone.IsochroneTypeEnum.heatmap.value,
                table_prefix=random_table_prefix,
            )
            await db.close()
            network = network[0]
            network = network.iloc[1:, :]

            # Get end time for network preparation
            end_time_network_preparation = time.time()

            (
                edges_source,
                edges_target,
                edges_cost,
                edges_reverse_cost,
                edges_length,
                unordered_map,
                node_coords,
                total_extent,
                geom_address,
                geom_array,
            ) = prepare_network_isochrone(network)

            # Prepare heatmap calculation objects
            traveltimeobjs = []
            for i in range(0, len(starting_ids), settings.HEATMAP_MULTIPROCESSING_BULK_SIZE):
                starting_ids_bulk = starting_ids[
                    i : i + settings.HEATMAP_MULTIPROCESSING_BULK_SIZE
                ]
                grid_ids_bulk = grid_ids[i : i + settings.HEATMAP_MULTIPROCESSING_BULK_SIZE]
                extents_bulk = extents[i : i + settings.HEATMAP_MULTIPROCESSING_BULK_SIZE]

                results = compute_isochrone_heatmap(
                    edges_source,
                    edges_target,
                    edges_cost,
                    edges_reverse_cost,
                    geom_address,
                    geom_array,
                    edges_length,
                    unordered_map,
                    node_coords,
                    extents_bulk,
                    starting_ids_bulk,
                    grid_ids_bulk,
                    isochrone_dto.settings.travel_time,
                    isochrone_dto.output.resolution,
                )
                traveltimeobjs.append(results)
                print(f"Computed traveltime for {i} to {i + settings.HEATMAP_MULTIPROCESSING_BULK_SIZE}th starting points out of {len(starting_ids)}")

            # Run multiprocessing
            # traveltimeobjs = heatmap_multiprocessing(heatmapObject)
            traveltimeobjs = merge_heatmap_traveltime_objects(traveltimeobjs)
            # Save files into cache folder
            file_name = f"{key}.npz"
            directory = os.path.join(
                settings.TRAVELTIME_MATRICES_PATH,
                isochrone_dto.mode.value,
                isochrone_dto.settings.walking_profile.value,
            )
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_dir = os.path.join(directory, file_name)
            delete_file(file_dir)
            np.savez_compressed(
                file_dir,
                **traveltimeobjs,
            )

            end_time_section = time.time()

            print_hashtags()
            print_info(
                f"You computed [bold magenta]{cnt}[/bold magenta] out of [bold magenta]{cnt_sections}[/bold magenta] added."
            )
            print_info(
                f"Section contains [bold magenta]{starting_ids.size}[/bold magenta] starting points"
            )
            print_info(
                f"Section took [bold magenta]{(end_time_section - starting_time_section)}[/bold magenta] seconds"
            )
            print_info(
                f"Network preparation took [bold magenta]{(end_time_network_preparation - starting_time_network_preparation)}[/bold magenta] seconds"
            )
            print_hashtags()

        end_time = time.time()
        print_hashtags()
        print_info(
            f"Total time: [bold magenta]{(end_time - starting_time)}[/bold magenta] seconds"
        )

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
        db = async_session()
        pois = [
            db.execute(
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
        await db.close()
        pois_dict = {}
        for idx_bulk, batch in enumerate(pois):
            if len(batch) > 0:
                bulk_id = batch[0][0]
                batch = [poi[1:] for poi in batch]
                pois_dict[bulk_id] = batch
        return pois_dict

    async def compute_opportunity_matrix(
        self, isochrone_dto: IsochroneDTO, calculation_objs: dict
    ):
        """Computes opportunity matrix

        Args:
            isochrone_dto (IsochroneDTO): _description_
            calculation_objs (dict): _description_
        """

        # Read relevant pois
        filter_geoms = []
        bulk_ids = list(calculation_objs.keys())
        for bulk_id in bulk_ids:
            coords = h3.h3_to_geo_boundary(h=bulk_id, geo_json=True)
            coords_str = ""
            for coord in coords:
                coords_str = coords_str + str(coord[0]) + " " + str(coord[1]) + ", "
            coords_str = coords_str + str(coords[0][0]) + " " + str(coords[0][1])
            filter_geoms.append(f"POLYGON(({coords_str}))")

        pois = await self.read_poi(
            isochrone_dto=isochrone_dto,
            table_name="poi",
            filter_geoms=filter_geoms,
            bulk_ids=bulk_ids,
        )

        # Read relevant opportunity matrices and merged arrays
        travel_time_matrices_north = []
        travel_time_matrices_west = []
        travel_time_matrices_south = []
        travel_time_matrices_east = []
        travel_time_matrices_height = []
        travel_time_matrices_width = []
        travel_time_matrices_grids_ids = []
        travel_time_matrices_travel_times = []

        #TODO: Buffer our single hex geom by 
        # buffer = isochrone_dto.settings.speed * (isochrone_dto.settings.travel_time * 60)

        #TODO: Find all hexes within buffer to get all relevant travel time matrices

        #TODO: Merge all relevant travel time matrices based on the hexes we found before
        for key in calculation_objs:
            file_name = f"{key}.npz"
            file_path = os.path.join(
                settings.TRAVELTIME_MATRICES_PATH,
                isochrone_dto.mode.value,
                isochrone_dto.settings.walking_profile.value,
                file_name,
            )
            matrix = np.load(
                file_path,
                allow_pickle=True,
            )

            travel_time_matrices_north.append(matrix["north"])
            travel_time_matrices_west.append(matrix["west"])
            travel_time_matrices_south.append(matrix["north"] + matrix["height"] - 1)
            travel_time_matrices_east.append(matrix["west"] + matrix["width"] - 1)
            travel_time_matrices_travel_times.append(matrix["travel_times"])
            travel_time_matrices_height.append(matrix["height"])
            travel_time_matrices_width.append(matrix["width"])
            travel_time_matrices_grids_ids.append(matrix["grid_ids"])

        travel_time_matrices_north = np.concatenate(travel_time_matrices_north)
        travel_time_matrices_west = np.concatenate(travel_time_matrices_west)
        travel_time_matrices_south = np.concatenate(travel_time_matrices_south)
        travel_time_matrices_east = np.concatenate(travel_time_matrices_east)
        travel_time_matrices_travel_times = np.concatenate(travel_time_matrices_travel_times)
        travel_time_matrices_height = np.concatenate(travel_time_matrices_height)
        travel_time_matrices_width = np.concatenate(travel_time_matrices_width)
        travel_time_matrices_grids_ids = np.concatenate(travel_time_matrices_grids_ids)

        # Loop through all POIs
        # TODO Performance improvements here (consider multiprocessing) and avoid loops
        for bulk_id in pois:
            poi_bulk = pois[bulk_id]
            previous_category = None

            poi_matrix = {
                "travel_times": [],
                "travel_times_matrix_size": [],
                "grid_ids": [],
                "names": [],
                "uids": [],
            }
            poi_categories = []

            for poi in poi_bulk:
                uid, category, name, x, y = poi

                # Check if category is already in poi categories
                if poi_categories == [] or previous_category != category:
                    poi_categories.append(category)
                    idx_poi_category = len(poi_categories) - 1
                    for key in poi_matrix.keys():
                        poi_matrix[key].append([])

                previous_category = category

                # Check if poi is in relevant travel time matrices
                indices_relevant_matrices = (
                    (travel_time_matrices_north <= x)
                    & (travel_time_matrices_south >= x)
                    & (travel_time_matrices_west <= y)
                    & (travel_time_matrices_east >= y)
                ).nonzero()[0]
                # Get the relevant travel time matrices
                relevant_traveltime_matrices = travel_time_matrices_travel_times[
                    indices_relevant_matrices
                ]
                # Get the grid ids of the relevant travel time matrices
                relevant_traveltime_matrices_grid_ids = travel_time_matrices_grids_ids[
                    indices_relevant_matrices
                ]
                # Get the indices of the traveltimes to the poi
                indices_travel_times = (
                    (x - travel_time_matrices_north[indices_relevant_matrices])
                    * travel_time_matrices_width[indices_relevant_matrices]
                    + y
                    - travel_time_matrices_west[indices_relevant_matrices]
                )

                arr_travel_times = []
                arr_grid_ids = []

                cnt = 0
                # TODO: Avoid this loop by selecting the indices directly from nested array
                for idx, matrix in enumerate(relevant_traveltime_matrices):
                    travel_time = matrix[indices_travel_times[idx]]

                    if travel_time < 2147483647:
                        arr_travel_times.append(travel_time)
                        arr_grid_ids.append(
                            h3.string_to_h3(str(relevant_traveltime_matrices_grid_ids[idx]))
                        )
                    else:
                        cnt += 1
                arr_travel_times = np.array(arr_travel_times, dtype=np.dtype(np.byte))
                arr_grid_ids = np.array(arr_grid_ids, dtype=np.dtype(np.int_))

                if len(arr_travel_times) > 0:
                    poi_matrix["travel_times"][idx_poi_category].append(arr_travel_times)
                    poi_matrix["travel_times_matrix_size"][idx_poi_category].append(
                        arr_travel_times.shape[0]
                    )
                    poi_matrix["grid_ids"][idx_poi_category].append(arr_grid_ids)
                    poi_matrix["names"][idx_poi_category].append(name)
                    poi_matrix["uids"][idx_poi_category].append(uid)
                else:
                    continue

            for key in ["travel_times", "grid_ids"]:
                for idx, category in enumerate(poi_matrix[key]):
                    poi_matrix[key][idx] = np.array(category, dtype=object)

            for idx, category in enumerate(poi_matrix["uids"]):
                poi_matrix["uids"][idx] = np.array(category, dtype=np.str_)

            for idx, category in enumerate(poi_matrix["names"]):
                poi_matrix["names"][idx] = np.array(category, dtype=np.str_)

            poi_matrix["travel_times_matrix_size"] = np.array(
                poi_matrix["travel_times_matrix_size"], dtype=object
            )
            for idx, category in enumerate(poi_matrix["travel_times_matrix_size"]):
                poi_matrix["travel_times_matrix_size"][idx] = np.array(
                    category, dtype=np.dtype(np.ushort)
                )

            poi_matrix["travel_times"] = np.array(poi_matrix["travel_times"], dtype=object)
            poi_matrix["grid_ids"] = np.array(poi_matrix["grid_ids"], dtype=object)
            poi_matrix["uids"] = np.array(poi_matrix["uids"], dtype=object)
            poi_matrix["names"] = np.array(poi_matrix["names"], dtype=object)
            poi_matrix["categories"] = np.array(poi_categories, dtype=np.str_)

            dir = os.path.join(
                settings.OPPORTUNITY_MATRICES_PATH,
                isochrone_dto.mode.value,
                isochrone_dto.settings.walking_profile.value,
                bulk_id,
            )
            create_dir(dir)
            for value in poi_matrix.keys():
                np.save(
                    f"{dir}/{value}",
                    poi_matrix[value],
                )

    async def get_neighbors(self, grids):
        neighbors = set()
        for h in grids:
            neighbors_ = h3.k_ring(h, 1)
            for n in neighbors_:
                if not n in grids:
                    neighbors.add(n)
        return list(neighbors)

    async def get_interior_neighbors(self, grids, study_area_polygon):
        neighbors = await self.get_neighbors(grids)
        neighbor_polygons = lambda hex_id: Polygon(h3.h3_to_geo_boundary(hex_id, geo_json=True))
        neighbor_polygons = gpd.GeoSeries(list(map(neighbor_polygons, neighbors)), crs="EPSG:4326")
        intersects = neighbor_polygons.intersects(study_area_polygon)
        neighbors = list(compress(neighbors, intersects.values))
        return neighbors

    async def get_h3_grids(self, study_area_id, resolution, style="int"):
        db = async_session()
        study_area = await crud.study_area.get(db, id=study_area_id)
        await db.close()
        study_area_polygon = to_shape(study_area.geom)
        grids = []
        for polygon_ in list(study_area_polygon.geoms):
            grids_ = h3.polyfill_geojson(polygon_.__geo_interface__, resolution)
            # Get hexagon geometries and convert to GeoDataFrame
            grids.extend(grids_)
        grids = list(set(grids))
        neighbors = await self.get_interior_neighbors(grids, study_area_polygon)
        grids.extend(neighbors)
        if style == "hex":
            grids = np.array(grids)
        elif style == "int":
            grids = np.array([int(hex_id, 16) for hex_id in grids])
        return grids

    async def create_h3_grids(self, study_area_ids):
        # TODO: Part of this is moved as a utility function. Refactor.
        base_path = "/app/src/cache/analyses_unit/"  # 9222/h3/10
        for study_area_id in study_area_ids:
            for resolution in range(6, 11):
                grids = await self.get_h3_grids(study_area_id, resolution, style="hex")
                hex_polygons = [
                    np.array(h3.h3_to_geo_boundary(str(hex_id), geo_json=True)) for hex_id in grids
                ]
                grids = np.array([int(hex_id, 16) for hex_id in grids])
                # hex_polygons_func = np.vectorize(hex_polygons_lambda)
                hex_polygons = np.array(hex_polygons)

                # hex_polygons = gpd.GeoSeries(list(map(hex_polygons, grids)), crs="EPSG:4326")
                # gdf = gpd.GeoDataFrame(
                #     data={"bulk_id": grids}, geometry=hex_polygons, crs="EPSG:4326"
                # )

                directory = os.path.join(base_path, str(study_area_id), "h3")
                grids_file_name = os.path.join(directory, f"{resolution}_grids.npy")
                hex_polygons_filename = os.path.join(directory, f"{resolution}_polygons.npy")
                if not os.path.exists(directory):
                    os.makedirs(directory)

                np.save(grids_file_name, grids)
                np.save(hex_polygons_filename, hex_polygons)

    async def execute_pre_calculation(
        self,
        isochrone_dto: IsochroneDTO,
        bulk_resolution: HeatmapWalkingBulkResolution,
        calculation_resolution: HeatmapWalkingCalculationResolution,
        study_area_ids: list[int] = None,
    ):
        """Executes pre-calculation for the heatmaps

        Args:
            isochrone_dto (IsochroneDTO): Settings for the isochrone calculation
            bulk_resolution (int): H3 resolution for the bulk grids.
            calculation_resolution (int): H3 resolution for the calculation grids.
            study_area_ids (list[int], optional): List of study area ids. Defaults to None and will use all study area.
        """

        buffer_size = isochrone_dto.settings.speed * (isochrone_dto.settings.travel_time * 60)
        await self.create_h3_grids(study_area_ids)
        # Get calculation objects
        calculation_objs = await self.prepare_bulk_objs(
            study_area_ids=study_area_ids,
            bulk_resolution=bulk_resolution,
            calculation_resolution=calculation_resolution,
            buffer_size=buffer_size,
        )

        # await self.compute_traveltime_active_mobility(
        #     isochrone_dto=isochrone_dto,
        #     calculation_objs=calculation_objs,
        # )

        await self.compute_opportunity_matrix(
            isochrone_dto=isochrone_dto,
            calculation_objs=calculation_objs,
        )

    async def create_connectivity_heatmap_files(
        self, mode: str, profile: str, h6_id: str, max_time: int
    ):
        if type(h6_id) is int:
            h6_id = h6_id.toString(16)

        travel_time_path = self.get_traveltime_path(mode, profile, h6_id)
        traveltime_h6 = np.load(travel_time_path, allow_pickle=True)
        areas = []
        for i in range(traveltime_h6["west"].size):
            isochrone_multipolygon_coordinates = jsolines(
                traveltime_h6["travel_times"][i],
                traveltime_h6["width"][i],
                traveltime_h6["height"][i],
                traveltime_h6["west"][i],
                traveltime_h6["north"][i],
                traveltime_h6["zoom"][i],
                np.array(list(range(1, max_time + 1)), dtype=np.uint8),
                web_mercator=False,
            )
            areas.append(isochrone_multipolygon_coordinates["full"].area)
        areas = np.array(areas)
        pass

    async def compute_areas(self, mode: str, profile: str, h6_id: str, max_time: int):
        travel_time_path = self.get_traveltime_path(mode, profile, h6_id)
        traveltime_h6 = np.load(travel_time_path, allow_pickle=True)
        areas = heatmap_cython.calculate_areas_from_pixles(
            traveltime_h6["travel_times"], list(range(1, max_time + 1))
        )
        return areas

    async def generate_connectivity_heatmap(
        self, mode: str, profile: str, study_area_id: int, max_time: int
    ):

        directory = self.get_connectivity_path(mode, profile)
        if not os.path.exists(directory):
            os.makedirs(directory)
        h6_hexagons = await self.get_h3_grids(study_area_id, 6, style="hex")
        for h6_id in h6_hexagons:
            travel_time_path = self.get_traveltime_path(mode, profile, h6_id)
            traveltime_h6 = np.load(travel_time_path, allow_pickle=True)
            areas = heatmap_cython.calculate_areas_from_pixles(
                traveltime_h6["travel_times"], list(range(1, max_time + 1))
            )
            grid_ids = heatmap_cython.h3_to_int(traveltime_h6["grid_ids"])

            file_name = os.path.join(directory, f"{h6_id}.npz")
            np.savez(file_name, grid_ids=grid_ids, areas=areas)
            pass


def main():
    # Get superuser
    db = async_session()
    superuser = asyncio.get_event_loop().run_until_complete(
        CRUDBase(models.User).get_by_key(db, key="id", value=15)
    )
    superuser = superuser[0]

    isochrone_dto = IsochroneDTO(
        mode="walking",
        settings=IsochroneSettings(
            travel_time=20,
            speed=5,
            walking_profile=RoutingTypes["walking_standard"].value.split("_")[1],
        ),
        starting_point=IsochroneStartingPoint(
            input=[
                IsochroneStartingPointCoord(lat=0, lon=0)
            ],  # Dummy points will be replaced in the function
            region_type="study_area",  # Dummy to avoid validation error
            region=[1, 2, 3],  # Dummy to avoid validation error
        ),
        output=IsochroneOutput(
            format=IsochroneOutputType.GRID,
            resolution=12,
        ),
        scenario=IsochroneScenario(
            id=1,
            name="Default",
        ),
    )

    crud_heatmap = CRUDComputeHeatmap(db=db, current_user=superuser)
    asyncio.get_event_loop().run_until_complete(
        crud_heatmap.execute_pre_calculation(
            isochrone_dto=isochrone_dto,
            bulk_resolution=HeatmapWalkingBulkResolution["resolution"],
            calculation_resolution=HeatmapWalkingCalculationResolution["resolution"],
            study_area_ids=[
                91620000,
            ],
        )
    )
    # asyncio.get_event_loop().run_until_complete(
    #     crud_heatmap.create_h3_grids(
    #         study_area_ids=[
    #             91620000,
    #         ],
    #     )
    # )
    # asyncio.get_event_loop().run_until_complete(
    #     crud_heatmap.create_connectivity_heatmap_files(
    #         profile="walking", h6_id="861f8d787ffffff", max_time=20
    #     )
    # )
    start_time = time.time()
    # areas = asyncio.get_event_loop().run_until_complete(
    #     crud_heatmap.compute_areas(profile="walking", h6_id="861f8d787ffffff", max_time=20)
    # )
    # asyncio.get_event_loop().run_until_complete(
    #     crud_heatmap.generate_connectivity_heatmap(
    #         mode="walking", profile="standard", study_area_id=91620000, max_time=20
    #     )
    # )
    end_time = time.time()
    print(f"Compute Areas Time: {end_time - start_time}")
    print("Heatmap is finished. Press Ctrl+C to exit.")
    input()


if __name__ == "__main__":
    main()
