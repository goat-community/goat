import asyncio
import bz2
import os
import time
import h3

import numpy as np
import pandas as pd
import geopandas as gpd
import json
from rich import print
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, text, select
from sqlalchemy.sql.functions import func
from src import crud, schemas
from src.endpoints import deps
from src.core.isochrone import (
    heatmap_multiprocessing,
    prepare_network_isochrone,
)
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import legacy_engine
from codetiming import Timer
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneOutput,
    IsochroneOutputType,
    IsochroneScenario,
    IsochroneSettings,
    IsochroneStartingPoint,
    IsochroneStartingPointCoord,
)
from src.resources.enums import (
    HeatmapWalkingBulkResolution,
    HeatmapWalkingCalculationResolution,
    RoutingTypes,
)
from src.utils import print_hashtags, print_info, print_warning
from src.db.session import async_session, sync_session


class CRUDGridCalculation(
    CRUDBase[models.GridCalculation, models.GridCalculation, models.GridCalculation]
):
    pass


class CRUDHeatmap:
    def __init__(self, db, db_sync, current_user):
        self.db = db
        self.db_sync = db_sync
        self.current_user = current_user

    async def prepare_bulk_objs(
        self,
        bulk_resolution: int,
        calculation_resolution: int,
        buffer_extent: float,
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

        # Get relevant study areas
        if study_area_ids is None:
            statement = select(models.StudyArea.id)
        else:
            statement = select(models.StudyArea.id).where(models.StudyArea.id.in_(study_area_ids))
        study_area_ids = await self.db.execute(statement)
        study_area_ids = study_area_ids.scalars().all()

        print_info(f"Processing will be done for Study area ids: {str(study_area_ids)[1:-1]}")

        # Get unioned study areas
        # Doing this in Raw SQL because query could not be build with SQLAlchemy ORM
        sql_query = f"""
                SELECT ST_AsGeoJSON(ST_MakePolygon(ST_ExteriorRing(geom))) AS geom 
                FROM 
                (
                    SELECT (ST_DUMP(ST_UNION(geom))).geom
                    FROM basic.study_area sa
                    WHERE sa.id IN ({str(study_area_ids)[1:-1]})
                ) u
            """
        union_geoms = await self.db.execute(text(sql_query))
        union_geoms = union_geoms.scalars().all()
        union_geoms_json = [json.loads(i) for i in union_geoms]

        #  Get all grids for the bulk resolution
        bulk_ids = []
        for geom in union_geoms_json:
            if geom["type"] != "Polygon":
                raise ValueError("Unioned Study area geometries are not a of type polygon.")

            bulk_ids.extend(list(h3.polyfill_geojson(geom, bulk_resolution)))

        bulk_ids = list(set(bulk_ids))

        # Get all grids for the calculation resolution that are children of the bulk resolution
        calculation_objs = {}
        cnt_calculation_ids = 0
        lons = []
        lats = []
        for bulk_id in bulk_ids:
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
            extents = gdf_starting_points.buffer(buffer_extent, cap_style=3)
            extents = extents.to_crs(epsg=3857)
            extents = extents.bounds
            extents = extents[:, [2, 1, 0, 3]]
            extents = extents.tolist()
            calculation_objs[bulk_id]["extents"] = extents

        end = time.time()
        print_info(f"Number of bulk grids: {len(bulk_ids)}")
        print_info(f"Number of calculation grids: {cnt_calculation_ids}")
        print_info(f"Calculation time: {end - begin} seconds")
        print_hashtags()
        return calculation_objs

    async def compute_traveltime(
        self,
        isochrone_settings: IsochroneSettings,
        routing_type: RoutingTypes,
        calculation_objs: dict,
        traveltime_grid_resolution: int,
    ):
        starting_time = time.time()

        cnt = 0
        cpus = os.cpu_count()
        cnt_sections = len(calculation_objs)

        begin = time.time()
        await self.db.execute(text("SELECT ST_CENTROID(geom) FROM basic.building"))
        end = time.time()
        print_info(f"Time to execute dummy query: {end - begin} seconds")

        for bulk in calculation_objs:
            starting_time_section = time.time()
            starting_time_network_preparation = time.time()
            cnt += 1


            # TODO: Compute bulk starting nodes from network

            # Check if there are no starting points
            if len(bulk["starting_point_objs"]) == 0:
                print_info(
                    f"No starting points for section [bold magenta]{str(cnt)}[/bold magenta]"
                )
                continue

            isochrone_dto = IsochroneDTO(
                mode="walking",
                settings=isochrone_settings,
                starting_point=IsochroneStartingPoint(
                    input=bulk["starting_point_objs"],
                    region_type="study_area",  # Dummy to avoid validation error
                    region=[1, 2, 3],  # Dummy to avoid validation error
                ),
                output=IsochroneOutput(
                    format=IsochroneOutputType.GRID,
                    resolution=traveltime_grid_resolution,
                ),
                scenario=IsochroneScenario(
                    id=1,
                    name="Default",
                ),
            )

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
                adj_list,
                edges_source,
                edges_target,
                edges_cost,
                edges_reverse_cost,
                edges_geom,
                edges_length,
                unordered_map,
                node_coords,
                total_extent,
            ) = prepare_network_isochrone(edge_network_input=network)

            heatmapObject = []
            for indx, starting_id in enumerate(starting_ids):
                # print(unordered_map)
                singleHeatmapIsochrone = (
                    edges_source,
                    edges_target,
                    edges_cost,
                    edges_reverse_cost,
                    edges_geom,
                    edges_length,
                    unordered_map,
                    node_coords,
                    extents[indx],
                    starting_id,
                    grid_ids[indx],
                    isochrone_dto.settings.travel_time,
                    isochrone_dto.output.resolution,
                )

                heatmapObject.append(singleHeatmapIsochrone)

            heatmap_multiprocessing(heatmapObject)

            end_time_section = time.time()

            print_hashtags()
            print_info(
                f"You computed [bold magenta]{cnt}[/bold magenta] out of [bold magenta]{cnt_sections}[/bold magenta] added."
            )
            print_info(
                f"Section contains [bold magenta]{sum([len(i) for i in starting_ids])}[/bold magenta] starting points"
            )
            print_info(
                f"Section took [bold magenta]{(end_time_section - starting_time_section)}[/bold magenta] seconds"
            )
            print_info(
                f"Network preparation took [bold magenta]{(end_time_network_preparation - starting_time_network_preparation)}[/bold magenta] seconds"
            )
            # print_info(f"Bulk insert took [bold magenta]{end_time_bulk_insert-beginning_time_bulk_insert}[/bold magenta]")
            print_hashtags()

        end_time = time.time()
        print_hashtags()
        print_info(
            f"Total time: [bold magenta]{(end_time - starting_time)}[/bold magenta] seconds"
        )

    async def execute_pre_calculation(
        self,
        routing_type: RoutingTypes,
        isochrone_settings: IsochroneSettings,
        bulk_resolution: HeatmapWalkingBulkResolution,
        calculation_resolution: HeatmapWalkingCalculationResolution,
        traveltime_grid_resolution: int,
        study_area_ids: list[int] = None,
    ):

        buffer_extent = (isochrone_settings.speed / 3.6) * (isochrone_settings.travel_time * 60)
        # Get calculation objects
        calculation_objs = await self.prepare_bulk_objs(
            study_area_ids=study_area_ids,
            bulk_resolution=bulk_resolution,
            calculation_resolution=calculation_resolution,
            buffer_extent=buffer_extent,
        )
        await self.compute_traveltime(
            isochrone_settings=isochrone_settings,
            routing_type=routing_type,
            calculation_objs=calculation_objs,
            traveltime_grid_resolution=traveltime_grid_resolution,
        )


def main():
    # Get superuser
    db = async_session()
    db_sync = sync_session()
    superuser = asyncio.get_event_loop().run_until_complete(
        CRUDBase(models.User).get_by_key(db, key="id", value=15)
    )
    superuser = superuser[0]

    isochrone_settings = IsochroneSettings(
        travel_time=20,
        speed=5,
        walking_profile=RoutingTypes["walking_standard"].value.split("_")[1],
    )

    crud_heatmap = CRUDHeatmap(db=db, db_sync=db_sync, current_user=superuser)
    asyncio.get_event_loop().run_until_complete(
        crud_heatmap.execute_pre_calculation(
            routing_type=RoutingTypes["walking_standard"],
            isochrone_settings=isochrone_settings,
            bulk_resolution=HeatmapWalkingBulkResolution["resolution"],
            calculation_resolution=HeatmapWalkingCalculationResolution["resolution"],
            traveltime_grid_resolution=12,
            study_area_ids=[9576],
        )
    )

    print("Heatmap is finished. Press Ctrl+C to exit.")
    input()


#main()
