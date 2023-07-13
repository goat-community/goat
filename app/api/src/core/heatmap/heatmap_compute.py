import base64
from datetime import datetime
from pathlib import Path

import pyximport
from aiohttp import BasicAuth, ClientError, ClientSession
import rasterio

pyximport.install()
import asyncio
import math
import os
import time

import h3
import numpy as np
from geopandas import GeoDataFrame, points_from_xy, read_postgis
from pandas import isnull
from rich import print
from shapely.geometry import Point, Polygon, box
from sqlalchemy.sql.functions import func

from src.crud.crud_isochrone import isochrone
from src.core.heatmap import heatmap_core_cython as heatmap_cython
from src.core.config import settings
from src.core.heatmap.heatmap_core import save_traveltime_matrix
from src.core.isochrone import network_to_grid, prepare_network_isochrone, dijkstra, construct_adjacency_list_
from src.core.heatmap.heatmap_read import BaseHeatmap
from src.db.session import async_session, legacy_engine, sync_session
from src.schemas.heatmap import (
    BulkTravelTime,
    HeatmapBulkResolution,
    HeatmapCalculationResolution,
)
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMode,
    IsochroneStartingPointCoord,
    IsochroneTypeEnum,
    R5TravelTimePayloadTemplate,
)
from src.utils import (
    coordinate_to_pixel,
    create_dir,
    create_h3_grid,
    decode_r5_grid,
    delete_file,
    filter_r5_grid,
    get_random_string,
    h3_to_int,
    print_hashtags,
    print_info,
    print_warning,
    web_mercator_to_wgs84,
    wgs84_to_web_mercator,
    downsample_array,
    pad_to_divisible,
)


def pixelate_geom(geom, isochrone_resolution):
    """
    Pixelate a geometry to the resolution of the isochrone

    :param geom:
    :param isochrone_resolution:

    :return: list of pixel coordinates
    """

    if geom.geom_type == "Point":
        coord = coordinate_to_pixel(
            [geom.x, geom.y],
            zoom=isochrone_resolution,
            return_dict=False,
            round_int=True,
        )
        return np.array(coord)

    if geom.geom_type == "Polygon":
        bounds = geom.bounds

        # Calculate the width and height on the resolution of the isochrone
        isochrone_resolution = isochrone_resolution
        bl_isochrone_res = coordinate_to_pixel(
            [bounds[0], bounds[1]],
            zoom=isochrone_resolution,
            return_dict=False,
            round_int=False,
        )

        tr_isochrone_res = coordinate_to_pixel(
            [bounds[2], bounds[3]],
            zoom=isochrone_resolution,
            return_dict=False,
            round_int=False,
        )

        width_isochrone_res = (
            round(tr_isochrone_res[0] - bl_isochrone_res[0]) + 1
        )  # +1 because the pixel coordinates are inclusive
        height_isochrone_res = (
            round(bl_isochrone_res[1] - tr_isochrone_res[1]) + 1
        )  # the order of the y coordinates is reversed in the pixel coordinate system
        geom_fill_isochrone_res = (height_isochrone_res, width_isochrone_res)  # (rows, cols)

        # Calculate the width and height on the resolution of the polygon pixelate
        polygon_pixelate_resolution = 15  # todo: make this a parameter
        bl = coordinate_to_pixel(  # bottom left
            [bounds[0], bounds[1]],
            zoom=polygon_pixelate_resolution,
            return_dict=False,
            round_int=False,
        )
        tr = coordinate_to_pixel(  # top right
            [bounds[2], bounds[3]],
            zoom=polygon_pixelate_resolution,
            return_dict=False,
            round_int=False,
        )

        width = round(tr[0] - bl[0]) + 1
        height = round(bl[1] - tr[1]) + 1
        affine_transform = rasterio.transform.from_bounds(
            bounds[0], bounds[1], bounds[2], bounds[3], width, height
        )
        geom_fill_pixelate_res = rasterio.features.rasterize(
            [geom],
            out_shape=(height, width),
            all_touched=False,
            transform=affine_transform,
        )
        geom_fill_pixelate_res_padded = pad_to_divisible(
            geom_fill_pixelate_res, height_isochrone_res, width_isochrone_res
        )
        # Downsample the array
        downsampled_arr = downsample_array(
            geom_fill_pixelate_res_padded, geom_fill_isochrone_res, method="sum"
        )
        # Top left corner coordinates isochrone res
        x0, y0 = round(bl_isochrone_res[0]), round(tr_isochrone_res[1])

        # Generate x and y coordinates for every point in the array
        x_coords, y_coords = np.meshgrid(
            np.arange(x0, x0 + downsampled_arr.shape[1]),
            np.arange(y0, y0 + downsampled_arr.shape[0]),
        )

        # Get the values of each point in the array (area in square meters)
        values = downsampled_arr.ravel()

        # Create a list of tuples for x, y and value
        coords = np.concatenate(
            (x_coords.reshape(-1, 1), y_coords.reshape(-1, 1), values.reshape(-1, 1)), axis=1
        ).astype(int)

        return coords


def get_relevant_travel_time_matrices(travel_time_matrices: dict, feature: dict) -> dict:
    """
    Get the travel time matrices that are relevant for the isochrone resolution

    :param travel_time_matrices:
    :param isochrone_resolution:

    :return: dict of relevant travel time matrices
    """
    if feature.geom.geom_type == "Point":
        x, y = feature.pixel
        # Check if feature is in relevant travel time matrices
        indices_relevant_matrices = (
            (travel_time_matrices["north"] <= y)
            & (travel_time_matrices["south"] >= y)
            & (travel_time_matrices["west"] <= x)
            & (travel_time_matrices["east"] >= x)
        ).nonzero()[0]

    elif feature.geom.geom_type == "Polygon" or feature.geom.geom_type == "MultiPolygon":
        # Check if feature is in relevant travel time matrices
        try:
            indices_relevant_matrices = (
                (travel_time_matrices["north"] <= feature.pixel[0][1])
                & (travel_time_matrices["south"] >= feature.pixel[-1][1])
                & (travel_time_matrices["west"] <= feature.pixel[0][0])
                & (travel_time_matrices["east"] >= feature.pixel[-1][0])
            ).nonzero()[0]
        except:
            return []

    return indices_relevant_matrices


def get_opportunity_relations(
    pixels: np.array,
    tt_north: np.array,
    tt_width: np.array,
    tt_west: np.array,
    indices_relevant_matrices: np.array,
    relevant_traveltime_matrices: np.array,
    relevant_traveltime_matrices_grid_ids: np.array,
    max_travel_time: int,
    weight: int = None,
):
    """
    Get the opportunity relations for a given set of pixels

    :param pixels: np.array of pixels
    :param tt_north: np.array of north coordinates of travel time matrices
    :param tt_width: np.array of width of travel time matrices
    :param tt_west: np.array of west coordinates of travel time matrices
    :param indices_relevant_matrices: np.array of indices of relevant travel time matrices
    :param relevant_traveltime_matrices: np.array of relevant travel time matrices
    :param relevant_traveltime_matrices_grid_ids: np.array of grid ids of relevant travel time matrices
    :param max_travel_time: int of maximum travel time
    :param weight: int of weight value. Relevant only for point features. Default is None

    :return: dict of opportunity relations
    """
    result = {"grid_ids": [], "travel_times": [], "weight": [], "relation_size": []}
    # For polygon features. (aoi, etc) we need to iterate over all pixels and get the weight from the tuple. Edge case
    if weight is None and len(pixels.shape) == 2:
        opportunity_relation = {}
        for pixel in pixels:
            x = pixel[0]
            y = pixel[1]
            weight = pixel[2]
            if weight == 0:
                continue
            # Get the indices of the traveltimes to the opportunity
            indices_travel_times = (
                (y - tt_north[indices_relevant_matrices]) * tt_width[indices_relevant_matrices]
                + x
                - tt_west[indices_relevant_matrices]
            )

            for idx, matrix in enumerate(relevant_traveltime_matrices):
                travel_time = matrix[indices_travel_times[idx]]
                if travel_time <= max_travel_time and travel_time >= 0:
                    grid_id = relevant_traveltime_matrices_grid_ids[idx]
                    if grid_id not in opportunity_relation:
                        opportunity_relation[grid_id] = {}
                    if travel_time not in opportunity_relation[grid_id]:
                        opportunity_relation[grid_id][travel_time] = 0

                    opportunity_relation[grid_id][travel_time] += weight

        for grid_id, items in opportunity_relation.items():
            result["travel_times"].extend(list(items.keys()))
            result["weight"].extend(list(items.values()))
            grid_ids = [grid_id] * len(items)
            result["grid_ids"].extend(grid_ids)
            result["relation_size"].append(len(items))

    else:
        # For point features.
        x = pixels[0]
        y = pixels[1]
        indices_travel_times = (
            (y - tt_north[indices_relevant_matrices]) * tt_width[indices_relevant_matrices]
            + x
            - tt_west[indices_relevant_matrices]
        )
        for idx, matrix in enumerate(relevant_traveltime_matrices):
            travel_time = matrix[indices_travel_times[idx]]
            if travel_time <= max_travel_time and travel_time >= 0:
                result["travel_times"].append(travel_time)
                result["weight"].append(weight)
                result["grid_ids"].append(relevant_traveltime_matrices_grid_ids[idx])
        result["relation_size"].append(len(result["travel_times"]))

    return result


class ComputeHeatmap(BaseHeatmap):
    async def get_bulk_ids(
        self,
        buffer_distance: int,
        study_area_ids: list[int] = None,
    ) -> list[str]:

        # Get unioned study areas
        bulk_ids = self.read_h3_grids_study_areas(
            resolution=HeatmapBulkResolution.active_mobility.value,
            buffer_size=buffer_distance,
            study_area_ids=study_area_ids,
        )
        return bulk_ids

    async def create_calculation_object(
        self,
        isochrone_dto: IsochroneDTO,
        bulk_id: str,
        calculation_resolution: int = None,
    ) -> dict:

        mode = isochrone_dto.mode
        if mode == IsochroneMode.TRANSIT:
            # todo: Find a better way to define/estimate the extent of the isochrone for transit
            buffer_size = 70000  # in meters
            calculation_resolution = (
                calculation_resolution or HeatmapCalculationResolution.motorized_transport.value
            )
            bulk_calculation_ids = h3.h3_to_children(bulk_id, calculation_resolution)
            h3_grid_gdf = GeoDataFrame(columns=["h3_index"])
            h3_grid_gdf["h3_index"] = list(bulk_calculation_ids)
            h3_grid_gdf["geometry"] = h3_grid_gdf["h3_index"].apply(
                lambda x: Polygon(h3.h3_to_geo_boundary(h=x, geo_json=True))
            )
            h3_grid_gdf.crs = "EPSG:4326"
            pt_stop_buffer = (isochrone_dto.settings.walk_speed / 3.6) * (
                isochrone_dto.settings.max_walk_time * 60
            )
            # Get all stops within bulk cell, buffer and clip. This approach avoids calculating places that are not reachable within the max walk time
            station_clip_calcualtion_grid_gdf = read_postgis(
                f"""SELECT st_intersection(st_union(st_transform(st_buffer(st_transform(st.stop_loc, 3857),{pt_stop_buffer}),4326)), 'SRID=4326;{h3_grid_gdf.unary_union.wkt}'::geometry) AS geom
                FROM gtfs.stops st WHERE ST_Intersects(st.stop_loc, 'SRID=4326;{h3_grid_gdf.unary_union.wkt}'::geometry)
                """,
                legacy_engine,
            )
            station_clip_calcualtion_ids = create_h3_grid(
                geometry=station_clip_calcualtion_grid_gdf.unary_union,
                h3_resolution=calculation_resolution,
                intersect_with_centroid=True,
            )["h3_index"].tolist()

            calculation_ids = list(set(station_clip_calcualtion_ids) & bulk_calculation_ids)
            # use the extent of the bulk object. This is done to optimize the R5 calculation speed. Since the buffer is quite large we can use the bulk object extent.
            bulk_lat, bulk_lon = h3.h3_to_geo(bulk_id)
            bulk_geom = wgs84_to_web_mercator(Point(bulk_lon, bulk_lat))
            extent = bulk_geom.buffer(buffer_size)

        elif mode == IsochroneMode.WALKING or mode == IsochroneMode.CYCLING:
            buffer_size = (isochrone_dto.settings.speed / 3.6) * (
                isochrone_dto.settings.travel_time * 60
            )
            calculation_resolution = (
                calculation_resolution or HeatmapCalculationResolution.active_mobility.value
            )

            calculation_ids = h3.h3_to_children(bulk_id, calculation_resolution)

        # Define variables
        calculation_obj = {}
        lons = []
        lats = []
        starting_point_objs = []
        coords = []
        calculation_obj[bulk_id] = {}
        # Loop through all calculation ids and create centroid coordinates for starting points
        for calculation_id in calculation_ids:
            lat, lon = h3.h3_to_geo(calculation_id)
            coords.append([lon, lat])
            starting_point_objs.append(IsochroneStartingPointCoord(lat=lat, lon=lon))
            lons.append(lon)
            lats.append(lat)
        calculation_obj[bulk_id]["calculation_ids"] = list(calculation_ids)
        calculation_obj[bulk_id]["coords"] = coords
        calculation_obj[bulk_id]["starting_point_objs"] = starting_point_objs

        # Get buffered extents for grid size
        if mode == IsochroneMode.TRANSIT:
            # same extent for all calculation ids
            calculation_obj[bulk_id]["extents"] = [list(extent.bounds)] * len(calculation_ids)
        else:
            gdf_starting_points = points_from_xy(x=lons, y=lats, crs="epsg:4326")
            gdf_starting_points = gdf_starting_points.to_crs(epsg=3395)
            extents = gdf_starting_points.buffer(buffer_size * math.sqrt(2), cap_style=3)
            extents = extents.to_crs(epsg=3857)
            extents = extents.bounds
            extents = extents.tolist()
            calculation_obj[bulk_id]["extents"] = extents

        calculation_obj[bulk_id]["lats"] = lats
        calculation_obj[bulk_id]["lons"] = lons

        return calculation_obj

    async def compute_opportunity_matrix(
        self,
        bulk_id: str,
        isochrone_dto: IsochroneDTO,
        opportunity_type: str,
        opportunities: GeoDataFrame,
        travel_time_matrices: dict,
        output_path: str = settings.OPPORTUNITY_MATRICES_PATH,
        s3_folder: str = None,
    ):
        """Computes opportunity matrix

        Args:
            bulk_id (str): Bulk id
            isochrone_dto (IsochroneDTO): Settings for the isochrone calculation
            opportunity_type (str): Type of opportunity
            opportunities (GeoDataFrame): Opportunities
            travel_time_matrices (dict): Travel time matrices
            output_path (str, optional): Path to save opportunity matrix. Defaults to settings.OPPORTUNITY_MATRICES_PATH. For scenarios, this is the path to the scenario folder.
            s3_folder (str, optional): S3 folder to save opportunity matrix. Defaults to None.
        """
        routing_profile = self.get_isochrone_routing_profile(isochrone_dto)
        # OPPORTUNITY INTERSECTION
        opportunities["pixel"] = opportunities["geom"].apply(
            pixelate_geom, isochrone_resolution=isochrone_dto.output.resolution
        )
        weight = None
        if opportunity_type == "population":
            # edge case for population data. Also for other `point` data that that we don't know the key for the weight
            # todo: make this more generic by defining the weight key somewhere else.
            opportunities["category"] = "population"
            weight = "population"
        if opportunity_type == "poi":
            weight = 1

        opportunity_matrix = {
            "travel_times": [],
            "grid_ids": [],
            "names": [],
            "uids": [],
            "weight": [],
            "relation_size": [],
        }
        types = {
            "travel_times": np.byte,
            "grid_ids": np.int_,
            "weight": np.float32,
            "relation_size": np.int_,
        }
        _grid_id_int_cache = {}
        opportunity_categories = []
        opportunities = opportunities.groupby("category")
        for category, opportunity_group in opportunities:
            opportunity_categories.append(category)
            for key in opportunity_matrix.keys():
                opportunity_matrix[key].append([])
            idx_opportunity_category = len(opportunity_categories) - 1
            for _index, opportunity in opportunity_group.iterrows():
                uid = opportunity.get("uid") or opportunity.get("id")
                name = opportunity.get("name") or ""
                category = opportunity["category"]
                # Check if feature is in relevant travel time matrices
                indices_relevant_matrices = get_relevant_travel_time_matrices(
                    travel_time_matrices, opportunity
                )
                if len(indices_relevant_matrices) == 0:
                    continue
                # Get the relevant travel time matrices
                relevant_traveltime_matrices = travel_time_matrices["travel_times"][
                    indices_relevant_matrices
                ]
                # Get the grid ids of the relevant travel time matrices
                relevant_traveltime_matrices_grid_ids = travel_time_matrices["grids_ids"][
                    indices_relevant_matrices
                ]

                if weight is not None and weight in opportunity.keys():
                    weight = opportunity[weight]
                    if isnull(weight):
                        weight = 0

                opportunity_relations = get_opportunity_relations(
                    opportunity["pixel"],
                    travel_time_matrices["north"],
                    travel_time_matrices["width"],
                    travel_time_matrices["west"],
                    indices_relevant_matrices,
                    relevant_traveltime_matrices,
                    relevant_traveltime_matrices_grid_ids,
                    isochrone_dto.settings.travel_time,
                    weight,
                )

                if len(opportunity_relations["travel_times"]) > 0:
                    try:
                        for key in ["travel_times", "weight", "relation_size"]:
                            opportunity_matrix[key][idx_opportunity_category].append(
                                np.array(opportunity_relations[key], dtype=types[key])
                            )
                    except Exception as e:
                        print(e)
                        print(opportunity_relations)
                        raise e
                    h3_arr_grid_ids = []
                    for x in opportunity_relations["grid_ids"]:
                        h3_int = _grid_id_int_cache.setdefault(x, h3.string_to_h3(str(x)))
                        h3_arr_grid_ids.append(h3_int)

                    h3_arr_grid_ids = np.array(h3_arr_grid_ids, dtype=np.dtype(np.int_))
                    opportunity_matrix["grid_ids"][idx_opportunity_category].append(
                        h3_arr_grid_ids
                    )

                    opportunity_matrix["names"][idx_opportunity_category].append(name)
                    opportunity_matrix["uids"][idx_opportunity_category].append(uid)

                else:
                    continue

        for key in ["travel_times", "grid_ids", "weight", "relation_size"]:
            for idx, category in enumerate(opportunity_matrix[key]):
                opportunity_matrix[key][idx] = np.array(category, dtype=object)

        for key in ["names", "uids"]:
            for idx, category in enumerate(opportunity_matrix[key]):
                opportunity_matrix[key][idx] = np.array(category, dtype=np.str_)


        try:
            for key in ["travel_times", "grid_ids", "weight", "relation_size", "names", "uids"]:
                opportunity_matrix[key] = np.array(opportunity_matrix[key], dtype=object)

            opportunity_matrix["categories"] = np.array(opportunity_categories, dtype=np.str_)

        except Exception as e:
            print(e)
            return

        dir = os.path.join(
            output_path,
            isochrone_dto.mode.value,
            routing_profile,
            bulk_id,
            opportunity_type,
        )
        create_dir(dir)
        for value in opportunity_matrix.keys():
            np.save(
                f"{dir}/{value}",
                opportunity_matrix[value],
            )
        if settings.S3_CLIENT and s3_folder:
            try:
                s3_folder_path = os.path.join(
                    f"{s3_folder}/opportunity_matrices",
                    isochrone_dto.mode.value,
                    routing_profile,
                    bulk_id,
                    opportunity_type,
                )
                for _root, _dirs, files in os.walk(dir):
                    for file in files:
                        settings.S3_CLIENT.upload_file(
                            f"{dir}/{file}", settings.AWS_BUCKET_NAME, f"{s3_folder_path}/{file}"
                        )
            except Exception as e:
                print_warning(f"Could not upload to s3: {e}")
                pass

    async def compute_connectivity_matrix(
        self, mode: str, profile: str, bulk_id: str, max_traveltime: int, s3_folder: str = ""
    ):

        directory = self.get_connectivity_path(mode, profile)
        if not os.path.exists(directory):
            os.makedirs(directory)
        matrix = await self.download_travel_time_matrices(bulk_id, mode, profile, s3_folder)

        if matrix is not None:
            areas = heatmap_cython.calculate_areas_from_pixles(
                matrix["travel_times"], list(range(1, max_traveltime + 1))
            )
            grid_ids = h3_to_int(matrix["grid_ids"])

            file_name = os.path.join(directory, f"{bulk_id}.npz")
            np.savez(file_name, grid_ids=grid_ids, areas=areas)
            await self.upload_npz_to_s3(
                bulk_id,
                local_folder=directory,
                s3_folder=s3_folder
                + f"/connectivity_matrices/{mode}/{profile}",
            )


    async def compute_traveltime_active_mobility(
        self,
        isochrone_dto: IsochroneDTO,
        calculation_obj: dict,
        s3_folder: str = "",
    ):
        """Computes the traveltime for active mobility in matrix style.

        Args:
            isochrone_dto (IsochroneDTO): Settings for the isochrone calculation
            calculation_obj (dict): Hierarchical structure of starting points for the calculation using the bulk resolution as parent and calculation resolution as children.
            s3_folder: The S3 output directory where the travel time folder will be stored
        """
        # Create random table prefix for starting ids and artificial edges
        random_table_prefix = get_random_string(10)
        starting_time = time.time()

        # Get Routing Profile
        routing_profile = self.get_isochrone_routing_profile(isochrone_dto)

        # Get calculation object
        bulk_id = list(calculation_obj.keys())[0]
        obj = calculation_obj[bulk_id]

        # Check if there are no starting points
        if len(obj["starting_point_objs"]) == 0:
            print_info("No starting points for section.")
            return
        # Prepare starting points using routing network
        db = async_session()
        starting_ids = await db.execute(
            func.basic.heatmap_prepare_artificial(
                obj["lons"],
                obj["lats"],
                isochrone_dto.settings.travel_time * 60,
                isochrone_dto.settings.speed / 3.6,
                "default",  # no scenario for active mobility yet
                0,  # no scenario for active mobility yet
                isochrone_dto.mode.value + "_" + routing_profile,
                True,
                obj["calculation_ids"],
                random_table_prefix,
            )
        )
        await db.commit()
        starting_ids = starting_ids.scalars().all()
        await db.close()

        if len(starting_ids) == 0:
            print_info("No starting points for section.")
            return

        # Sort out invalid starting points (no network edge found)
        valid_extents = []
        valid_starting_ids = []
        valid_starting_point_objs = []
        valid_calculation_ids = []

        for starting_id, grid_calculation_id in starting_ids:
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
        db = sync_session()
        network = isochrone.read_network(
            db=db,
            obj_in=isochrone_dto,
            current_user=self.current_user,
            isochrone_type=IsochroneTypeEnum.heatmap.value,
            table_prefix=random_table_prefix,
        )
        db.close()
        network = network[0]
        network = network.iloc[1:, :]

        # Prepare network
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
        traveltimeobjs = {
            "west": [],
            "north": [],
            "zoom": [],
            "width": [],
            "height": [],
            "grid_ids": [],
            "travel_times": [],
        }
        adj_list = construct_adjacency_list_(len(edges_source), edges_source, edges_target, edges_cost, edges_reverse_cost)

        for idx, start_vertex in enumerate(starting_ids):
            # Assign variables
            grid_id = grid_ids[idx]
            extent = extents[idx]
            starting_point_objs[idx]
            # Get start vertex
            try:
                start_id = np.array([unordered_map[v] for v in [start_vertex]])
            except Exception as e:
                print(e)
                continue
            # Run Dijkstra
            start_time = time.time()
            distances = dijkstra(start_id, adj_list, isochrone_dto.settings.travel_time)
            print(f"Time dijkstra: {time.time() - start_time}")

            # Convert network to grid
            grid = network_to_grid(
                extent,
                isochrone_dto.output.resolution,
                edges_source,
                edges_target,
                edges_length,
                geom_address,
                geom_array,
                distances,
                node_coords,
                isochrone_dto.settings.speed / 3.6,
                isochrone_dto.settings.travel_time,
            )
            try:
                grid = filter_r5_grid(
                    grid, percentile=5, travel_time_limit=isochrone_dto.settings.travel_time
                )
            except Exception:
                print("Could not filter grid")
            # Assign grid_id and rename data to travel_times
            grid["grid_ids"] = grid_id
            grid["travel_times"] = grid.pop("data")
            # Save to traveltime object
            for key in traveltimeobjs.keys():
                traveltimeobjs[key].append(grid[key])
            # Print progress
            if idx % 100 == 0:
                print_info(f"Progress traveltime matrices: {idx}/{len(starting_ids)}")

        # Convert to numpy arrays
        for key in traveltimeobjs.keys():
            # Check if str then obj type
            if isinstance(traveltimeobjs[key][0], str):
                traveltimeobjs[key] = np.array(traveltimeobjs[key], dtype=object)
            else:
                traveltimeobjs[key] = np.array(traveltimeobjs[key])

        # Save files into cache folder
        file_name = f"{bulk_id}.npz"
        directory = os.path.join(
            settings.TRAVELTIME_MATRICES_PATH,
            isochrone_dto.mode.value,
            routing_profile,
        )
        # Create directory if not exists
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_dir = os.path.join(directory, file_name)
        delete_file(file_dir)
        # Save to file
        np.savez_compressed(
            file_dir,
            **traveltimeobjs,
        )
        # Copy to S3 bucket (if configured)
        if s3_folder:
            await self.upload_npz_to_s3(
                bulk_id,
                local_folder=directory,
                s3_folder=s3_folder
                + f"/traveltime_matrices/{isochrone_dto.mode.value}/{routing_profile}",
            )

        end_time = time.time()
        print_hashtags()
        print_info(
            f"Total time: [bold magenta]{(end_time - starting_time)}[/bold magenta] seconds"
        )

    async def compute_traveltime_motorized_transport(
        self,
        isochrone_dto: IsochroneDTO,
        calculation_obj: dict,
        parallel_requests: int = 60,
        s3_folder: str = "",
    ) -> BulkTravelTime:
        """Computes the traveltime for active mobility in matrix style.

        Args:
            isochrone_dto (IsochroneDTO): Settings for the isochrone calculation
            calculation_obj (dict): Hierarchical structure of starting points for the calculation using the bulk resolution as parent and calculation resolution as children.
            parallel_requests (int, optional): Number of parallel requests to R5. Defaults to 60.
            s3_folder: The S3 output directory where the travel time folder will be stored
        """
        # Get calculation object
        bulk_id = list(calculation_obj.keys())[0]
        obj = calculation_obj[bulk_id]
        start = time.time()
        print_info(f"Starting to process travel times for bulk {bulk_id}")
        # Create output dir if it does not exist
        output_dir = settings.TRAVELTIME_MATRICES_PATH + "/" + isochrone_dto.mode.value
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Prepare metadata. This will be used to create the metadata file for the bulk object to know which h3 index was calculated and which has failed.
        metadata = {"h3_index": [], "status": [], "geometry": []}
        # Prepare R5 payloads
        # Loop through all calculation objects and create a payload for each one
        payloads = []
        # R5 Authorization credentials
        if settings.R5_AUTHORIZATION is None:
            user, password = "", ""
        else:
            user, password = (
                base64.b64decode(settings.R5_AUTHORIZATION.split(" ")[1]).decode("utf-8").split(":")
            )
        for idx, value in enumerate(obj["calculation_ids"]):
            payload = R5TravelTimePayloadTemplate.copy()
            payload["h3_index"] = value
            payload["fromLon"] = obj["lons"][idx]
            payload["fromLat"] = obj["lats"][idx]
            extent = obj["extents"][idx]
            extent = list(web_mercator_to_wgs84(box(*extent, ccw=True)).bounds)
            payload["bounds"] = {
                "north": extent[3],
                "south": extent[1],
                "east": extent[2],
                "west": extent[0],
            }
            payloads.append(payload)

        # Send requests to R5 API in batches
        traveltimeobjs = {
            "west": [],
            "north": [],
            "zoom": [],
            "width": [],
            "height": [],
            "grid_ids": [],
            "travel_times": [],
        }

        if parallel_requests is None:
            parallel_requests = len(payloads)
        async with ClientSession(
            auth=BasicAuth(user, password),
        ) as client:
            for i in range(0, len(payloads), parallel_requests):
                api_calls = []
                batch = payloads[i : i + parallel_requests]
                for _index, payload in enumerate(batch):
                    api_calls.append(
                        self.fetch_r5_travel_time(
                            payload=payload,
                            client=client,
                            travel_time_percentile=5,
                            travel_time_limit=60,
                        )
                    )
                results = await asyncio.gather(*api_calls)
                for result in results:
                    h3_grid_id = result["h3_index"]
                    grid = result.get("grid")
                    status = "success"
                    if grid is None:
                        status = "failed"
                        continue

                    for key in ["west", "north", "zoom", "width", "height"]:
                        traveltimeobjs[key].append(grid[key])

                    traveltimeobjs["grid_ids"].append(h3_grid_id)
                    traveltimeobjs["travel_times"].append(grid["data"])

                    # fill metadata
                    metadata["h3_index"].append(h3_grid_id)
                    metadata["status"].append(status)
                    metadata["geometry"].append(Point(result["fromLon"], result["fromLat"]))

        if len(traveltimeobjs["travel_times"]) == 0:
            print_warning(f"Could not compute travel times for {bulk_id}")
            return
        # Save results to npz file
        print_info(f"Saving travel times for {bulk_id}")

        save_traveltime_matrix(
            bulk_id=bulk_id, traveltimeobjs=traveltimeobjs, output_dir=output_dir
        )
        # Save metadata to geojson file
        await self.save_metadata_gdf(metadata, f"{output_dir}/metadata/{bulk_id}.geojson")
        # Copy to S3 bucket (if configured)
        if s3_folder:
            await self.upload_npz_to_s3(
                bulk_id,
                local_folder=output_dir,
                s3_folder=s3_folder + "/traveltime_matrices/transit",
            )

        print_info(f"Computed travel times for {bulk_id} in {time.time() - start} seconds")
        return traveltimeobjs

    async def download_travel_time_matrices(self, bulk_id: str, mode: str, profile: str, s3_folder: str = ""):
        """Downloads travel time matrices from S3 bucket if not exists."""

        file_name = f"{bulk_id}.npz"
        dir_profile = os.path.join(
            settings.TRAVELTIME_MATRICES_PATH, mode, profile
        )
        file_path = os.path.join(
            dir_profile,
            file_name,
        )
        if s3_folder != "" and not os.path.exists(file_path):
            # check if file exists in S3
            if settings.S3_CLIENT:
                print_info(f"File {bulk_id}.npz not found locally. Checking S3...")
                try:
                    s3_path = os.path.join(
                        f"{s3_folder}/traveltime_matrices/{mode}",
                        profile,
                        file_name,
                    )
                    if not os.path.exists(dir_profile):
                        os.makedirs(dir_profile, exist_ok=True)
                    settings.S3_CLIENT.download_file(
                        settings.AWS_BUCKET_NAME,
                        s3_path,
                        file_path,
                    )
                except Exception:
                    print_warning(f"File {bulk_id}.npz not found in S3. Skipping...")

            else:
                print_warning(f"File {bulk_id}.npz not found locally. Skipping...")

        try:
            matrix = np.load(
                file_path,
                allow_pickle=True,
            )
            return matrix
        except FileNotFoundError:
            print_warning(f"Cant load file {file_path}. Skipping...")




    async def read_travel_time_matrices(
        self, bulk_id: str, isochrone_dto: IsochroneDTO, s3_folder: str = ""
    ):
        """
        Reads the travel time matrices from the local file system or from S3 if configured.

        Args:
            bulk_id (str): The bulk id for which the travel time matrices should be read
            isochrone_dto (IsochroneDTO): The isochrone DTO containing the settings

        Returns:
            dict: The travel time matrices

        """
        # FIND RELEVANT TRAVEL TIME MATRICES
        bulk_resolution = h3.h3_get_resolution(h=bulk_id)
        routing_profile = self.get_isochrone_routing_profile(isochrone_dto)
        if (
            isochrone_dto.mode == IsochroneMode.WALKING
            or isochrone_dto.mode == IsochroneMode.CYCLING
        ):
            max_travel_distance = (
                isochrone_dto.settings.speed / 3.6 * (isochrone_dto.settings.travel_time * 60)
            )  # in meters
        else:
            # todo: find a better way to do this
            max_travel_distance = 20000  # in meters FOR MOTORIZED MODES

        edge_length = h3.edge_length(resolution=bulk_resolution, unit="m")
        distance_in_neightbors = math.ceil(max_travel_distance / edge_length)
        travel_time_grids = h3.k_ring(h=bulk_id, k=distance_in_neightbors)

        # FETCH TRAVEL TIME MATRICES
        travel_time_matrices = {
            "north": [],
            "west": [],
            "south": [],
            "east": [],
            "height": [],
            "width": [],
            "grids_ids": [],
            "travel_times": [],
        }

        for key in travel_time_grids:
            print(f"Reading travel time matrix {key}...")
            file_name = f"{key}.npz"
            dir_profile = os.path.join(
                settings.TRAVELTIME_MATRICES_PATH, isochrone_dto.mode.value, routing_profile
            )
            file_path = os.path.join(
                dir_profile,
                file_name,
            )
            # check if file doesn't exist in local file system and missing_keys folder
            if s3_folder != "" and not os.path.exists(file_path):
                # check if file exists in S3
                if settings.S3_CLIENT:
                    print_info(f"File {key}.npz not found locally. Checking S3...")
                    try:
                        s3_path = os.path.join(
                            f"{s3_folder}/traveltime_matrices/{isochrone_dto.mode.value}",
                            routing_profile,
                            file_name,
                        )
                        if not os.path.exists(dir_profile):
                            os.makedirs(dir_profile, exist_ok=True)
                        settings.S3_CLIENT.download_file(
                            settings.AWS_BUCKET_NAME,
                            s3_path,
                            file_path,
                        )
                    except Exception:
                        print_warning(f"File {key}.npz not found in S3. Skipping...")
                        continue
                else:
                    print_warning(f"File {key}.npz not found locally. Skipping...")
                    continue

            try:
                matrix = np.load(
                    file_path,
                    allow_pickle=True,
                )
            except FileNotFoundError:
                print_warning(f"Cant load file {file_path}. Skipping...")
                continue

            # loop through travel_time_matrices and add the values of grid
            for key in set(travel_time_matrices.keys()).difference(["south", "east", "grids_ids"]):
                travel_time_matrices[key].append(matrix[key])

            # calculate south and east
            travel_time_matrices["south"].append(matrix["north"] + matrix["height"] - 1)
            travel_time_matrices["east"].append(matrix["west"] + matrix["width"] - 1)
            travel_time_matrices["grids_ids"].append(matrix["grid_ids"])

        if len(travel_time_matrices["north"]) == 0:
            return None
        try:
            for key in travel_time_matrices:
                travel_time_matrices[key] = np.concatenate(travel_time_matrices[key])
        except Exception as e:
            print_warning(f"Error while reading travel time matrices: {e}")
            return None

        return travel_time_matrices

    @staticmethod
    async def fetch_r5_travel_time(
        payload: dict,
        client: ClientSession,
        travel_time_percentile: int = 5,
        travel_time_limit: int = 60,
    ) -> dict:
        """
        Fetches a single travel time from the R5 API and returns the decoded grid
        Grid is filtered to only include the area within the study area within the travel time surface

        :param payload: R5 API payload
        :param client: ClientSession
        :param travel_time_percentile: percentile of travel time to use for filtering
        :param travel_time_limit: maximum travel time to use for filtering

        :return: decoded grid
        """
        data = None
        retry_count = 0
        while data is None and retry_count < 30:
            try:
                async with client.post(
                    settings.R5_API_URL + "/analysis", json=payload
                ) as response:
                    response.raise_for_status()
                    if response.status == 202:
                        # throw exception to retry. 202 means that the request is still being processed
                        content = await response.content.read()
                        if content is not None and len(content) == 33:
                            # 33 is the length of the string "Building network...". Reset the retry count if this is the case
                            retry_count = 0
                            print ("Building network...")
                            await asyncio.sleep(8)
                        raise ClientError("Request still being processed")
                    data = await response.content.read()
            except ClientError:
                # sleep a little and try again for
                retry_count += 1
                await asyncio.sleep(4)

        if data is None:
            print_warning(f"Could not fetch travel time for {payload['h3_index']}")
            payload["grid"] = None
            return payload
        grid = decode_r5_grid(data)
        try:
            grid = filter_r5_grid(
                grid, travel_time_percentile, travel_time_limit
            )  # TODO: compare the travel time result with the one from conveyal to see if they are the same
        except Exception as e:
            print_warning(f"Error while filtering travel time grid: {e}")
            grid = None
            return payload
        payload["grid"] = grid
        print_info(f"Fetched travel time for {payload['h3_index']}")
        return payload

    @staticmethod
    async def upload_npz_to_s3(bulk_id: str, local_folder: str, s3_folder: str = "") -> None:
        """
        Uploads the travel time matrix and metadata to S3

        :param bulk_id: bulk id
        :param local_folder: local output directory
        :param s3_folder: S3 output directory
        """
        # upload npz and metadata to S3
        s3_client = settings.S3_CLIENT
        if s3_folder == "":
            # add time as folder name
            s3_folder = datetime.now().strftime("%Y-%m-%d")
        s3_client.upload_file(
            f"{local_folder}/{bulk_id}.npz",
            settings.AWS_BUCKET_NAME,
            f"{s3_folder}/{bulk_id}.npz",
        )
        metadata_file_path = f"{local_folder}/metadata/{bulk_id}.geojson"
        if os.path.exists(metadata_file_path):
            s3_client.upload_file(
                metadata_file_path,
                settings.AWS_BUCKET_NAME,
                f"{s3_folder}/metadata/{bulk_id}.geojson",
            )
        return

    @staticmethod
    async def save_metadata_gdf(metadata, output_file):
        """
        Saves the metadata to a geojson file

        :param metadata: metadata object with geometry column
        :param output_file: output file path
        """
        output_file_path = Path(output_file)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_gdf = GeoDataFrame(metadata, geometry="geometry", crs="EPSG:4326")
        metadata_gdf.to_file(
            output_file,
            driver="GeoJSON",
        )
