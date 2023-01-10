import asyncio
import json
import math
import os
import time
from typing import List

import geopandas as gpd
import h3
import heatmap_utils
import numpy as np
import pandas as pd
from codetiming import Timer
from geoalchemy2.functions import ST_Dump
from geoalchemy2.shape import to_shape
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
from src.crud.crud_read_heatmap import CRUDBaseHeatmap
from src.db import models
from src.db.session import async_session, legacy_engine, sync_session
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
            starting_ids = await self.db.execute(
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
                )
            )
            await self.db.commit()
            starting_ids = starting_ids.scalars().all()

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
            network = await crud.isochrone.read_network(
                db=self.db,
                obj_in=isochrone_dto,
                current_user=self.current_user,
                isochrone_type=schemas.isochrone.IsochroneTypeEnum.heatmap.value,
            )
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
            ) = prepare_network_isochrone(edge_network_input=network)

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
                print("Computed traveltime for {} starting points".format(len(starting_ids_bulk)))

            # Run multiprocessing
            # traveltimeobjs = heatmap_multiprocessing(heatmapObject)
            traveltimeobjs = merge_heatmap_traveltime_objects(traveltimeobjs)
            # Save files into cache folder
            file_name = f"{key}.npz"
            file_dir = os.path.join(
                settings.TRAVELTIME_MATRICES_PATH,
                isochrone_dto.mode.value,
                isochrone_dto.settings.walking_profile.value,
                file_name,
            )
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

        # TODO Performance improvements here (consider multiprocessing)
        begin = time.time()

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

                indices_relevant_matrices = (
                    (travel_time_matrices_north <= x)
                    & (travel_time_matrices_south >= x)
                    & (travel_time_matrices_west <= y)
                    & (travel_time_matrices_east >= y)
                ).nonzero()[0]
                relevant_traveltime_matrices = travel_time_matrices_travel_times[
                    indices_relevant_matrices
                ]
                relevant_traveltime_matrices_grid_ids = travel_time_matrices_grids_ids[
                    indices_relevant_matrices
                ]

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

    async def create_h3_girds(self, study_area_ids):
        base_path = "/app/src/cache/analyses_unit/"  # 9222/h3/10
        for study_area_id in study_area_ids:
            study_area = await crud.study_area.get(self.db, id=study_area_id)
            for resolution in range(6, 11):
                grids = []
                study_area_polygon = to_shape(study_area.geom)
                for polygon_ in list(study_area_polygon):
                    grids_ = h3.polyfill_geojson(polygon_.__geo_interface__, resolution)
                    # Get hexagon geometries and convert to GeoDataFrame
                    grids.extend(grids_)
                grids = list(set(grids))
                hex_polygons = lambda hex_id: Polygon(h3.h3_to_geo_boundary(hex_id, geo_json=True))
                hex_polygons = gpd.GeoSeries(list(map(hex_polygons, grids)), crs="EPSG:4326")
                gdf = gpd.GeoDataFrame(
                    data={"bulk_id": grids}, geometry=hex_polygons, crs="EPSG:4326"
                )
                directory = os.path.join(base_path, str(study_area_id), "h3")
                file_name = os.path.join(directory, f"{resolution}.geojson")
                if not os.path.exists(directory):
                    os.makedirs(directory)
                gdf.to_file(file_name, driver="GeoJSON")

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
        await self.create_h3_girds(study_area_ids)
        # Get calculation objects
        calculation_objs = await self.prepare_bulk_objs(
            study_area_ids=study_area_ids,
            bulk_resolution=bulk_resolution,
            calculation_resolution=calculation_resolution,
            buffer_size=buffer_size,
        )

        await self.create_h3_girds(calculation_objs)

        # await self.compute_traveltime_active_mobility(
        #     isochrone_dto=isochrone_dto,
        #     calculation_objs=calculation_objs,
        # )

        await self.compute_opportunity_matrix(
            isochrone_dto=isochrone_dto,
            calculation_objs=calculation_objs,
        )


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

    print("Heatmap is finished. Press Ctrl+C to exit.")
    input()


if __name__ == "__main__":
    main()
