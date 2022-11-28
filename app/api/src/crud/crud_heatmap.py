import asyncio
import bz2
import os
import time
from datetime import datetime, timedelta
from functools import partial
from itertools import repeat
from multiprocessing.pool import Pool

import numpy as np
import pandas as pd
from rich import print
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, text

from src import crud, schemas
from src.core.isochrone import (
    compute_isochrone_heatmap,
    heatmap_multiprocessing,
    prepare_network_isochrone,
)
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import legacy_engine
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneOutput,
    IsochroneOutputType,
    IsochroneScenario,
    IsochroneSettings,
    IsochroneStartingPoint,
    IsochroneStartingPointCoord,
)
from src.utils import print_hashtags, print_info, print_warning

# from multiprocessing.pool import ThreadPool as Pool
# from concurrent.futures import ProcessPoolExecutor as Pool
# from loky import get_reusable_executor
# from pathos.multiprocessing import ProcessingPool as Pool

# from pathos.pools import ProcessPool as Pool




class CRUDGridCalculation(
    CRUDBase[models.GridCalculation, models.GridCalculation, models.GridCalculation]
):
    pass


# Alternative to_sql() *method* for DBs that support COPY FROM
import csv
from io import StringIO


class CRUDHeatmap:
    # == WALKING AND CYCLING INDICATORS ==#

    async def prepare_starting_points(self, db: AsyncSession, current_user: models.User):
        """Get starting points for heatmap calculation."""

        await db.execute(text("DROP TABLE IF EXISTS temporal.heatmap_grid_helper;"))
        await db.commit()
        query = text(
           """
            CREATE TABLE temporal.heatmap_grid_helper AS 
            WITH relevant_study_area_ids AS 
            (
                SELECT id FROM basic.study_area WHERE id IN (83110000)
            ),
            cnt AS 
            (
                SELECT count(*) cnt 
                FROM basic.grid_visualization g, basic.study_area_grid_visualization s
                WHERE s.study_area_id IN (SELECT * FROM relevant_study_area_ids) 
                AND g.id = s.grid_visualization_id 
            ) 
            SELECT ST_ClusterKMeans(g.geom, (cnt / 50)::integer) OVER() AS cid, g.id, g.geom, False as already_processed  
            FROM basic.grid_visualization g, basic.study_area_grid_visualization s, cnt 
            WHERE s.study_area_id IN (SELECT * FROM relevant_study_area_ids) 
            AND g.id = s.grid_visualization_id 
            """
        )
        await db.execute(query)
        await db.commit()


async def compute_traveltime(db: AsyncSession, db_sync: Session, current_user: models.User):
    starting_time = time.time()
    travel_time = 20
    speed = 5
    buffer_distance = (speed / 3.6) * (travel_time * 60)

    kmeans_classes = await db.execute(
        text("SELECT DISTINCT cid FROM temporal.heatmap_grid_helper;")
    )
    kmeans_classes = kmeans_classes.fetchall()
    kmeans_classes = [c[0] for c in kmeans_classes]

    await db.execute(
        "SELECT basic.heatmap_prepare_artificial(:kmeans_classes);",
        {"kmeans_classes": kmeans_classes},
    )
    await db.commit()

    cnt = 0
    cnt_sections = len(kmeans_classes)
    cpus = os.cpu_count()
    batch_size = 20

    for kmeans_class in kmeans_classes:
        starting_time_section = time.time()
        starting_time_network_preparation = time.time()
        cnt += 1
        # Get starting points for starting grids
        starting_points = await db.execute(
            text(
                f"""
                SELECT ARRAY_AGG(starting_id) AS starting_id, ARRAY_AGG(grid_calculation_id) AS grid_calculation_id, 
                ARRAY_AGG(x) AS x, ARRAY_AGG(y) AS y, ARRAY_AGG(extent) AS extent 
                FROM 
                (
                    SELECT (row_number() over()) / :batch_size AS id, v.id AS starting_id, c.id AS grid_calculation_id, 
                    ST_X(ST_CENTROID(v.geom)) AS x, ST_Y(ST_CENTROID(v.geom)) AS y,
                    ARRAY[
                        ST_X(ST_TRANSFORM(ST_PROJECT(v.geom, :buffer_distance, radians(-45.0))::geometry, 3857)),
                        ST_Y(ST_TRANSFORM(ST_PROJECT(v.geom, :buffer_distance, radians(135.0))::geometry, 3857)),
                        ST_X(ST_TRANSFORM(ST_PROJECT(v.geom, :buffer_distance, radians(135.0))::geometry, 3857)),
                        ST_Y(ST_TRANSFORM(ST_PROJECT(v.geom, :buffer_distance, radians(-45.0))::geometry, 3857))
                    ] AS extent
                    FROM temporal.heatmap_starting_vertices v, basic.grid_calculation c, temporal.heatmap_grid_helper h  
                    WHERE ST_Intersects(v.geom, c.geom)
                    AND c.grid_visualization_id = h.id 
                    AND h.cid = :cid 
                    AND h.already_processed = False 
                ) AS g
                GROUP BY id
                """
            ),
            {"cid": kmeans_class, "buffer_distance": buffer_distance, "batch_size": batch_size},
        )

        starting_points = starting_points.fetchall()

        # Check if there are no starting points
        if len(starting_points) == 0:
            print_info(f"No starting points for section [bold magenta]{str(cnt)}[/bold magenta]")
            continue
        # Create a list of DTOs for starting points
        starting_points_dto_arr = []
        starting_ids = []
        grid_ids = []
        extents = []

        for batch in starting_points:
            starting_ids.append(batch[0])
            grid_ids.append(batch[1])
            extents.append(batch[4])

            for idx, lon in enumerate(batch[2]):
                lat = batch[3][idx]
                starting_points_dto_arr.append(IsochroneStartingPointCoord(lat=lat, lon=lon))

        # Create Isochrone DTO for heatmap calculation
        # TODO: Adjust DTO to properly work with heatmap
        obj_multi_isochrones = IsochroneDTO(
            mode="walking",
            settings=IsochroneSettings(
                travel_time=travel_time,
                speed=speed,
                walking_profile="standard",
            ),
            starting_point=IsochroneStartingPoint(
                input=starting_points_dto_arr,
                region_type="study_area",  # Dummy to avoid validation error
                region=[1, 2, 3],  # Dummy to avoid validation error
            ),
            output=IsochroneOutput(format=IsochroneOutputType.GRID),
            scenario=IsochroneScenario(
                id=1,
                name="Default",
            ),
        )
        # Read network
        network = await crud.isochrone.read_network(
            db=db,
            obj_in=obj_multi_isochrones,
            current_user=current_user,
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
        # WORKS
        # total_inserts = []
        # for idx, batch_starting_ids in enumerate(starting_ids):

        #     batch_insert = compute_isochrone_heatmap(
        #         adj_list,
        #         edges_source,
        #         edges_target,
        #         edges_geom,
        #         edges_length,
        #         unordered_map,
        #         node_coords,
        #         extents[idx],
        #         batch_starting_ids,
        #         grid_ids[idx],
        #         obj_multi_isochrones.settings.travel_time,
        #         obj_multi_isochrones.output.resolution,
        #     )
        #     total_inserts.extend(batch_insert)

        # Compute isochrones
        # DOES NOT WORK WITH MULTIPROCESSING
        # TODO: Fix multiprocessing
        zip_object = zip(
            repeat(adj_list),
            repeat(edges_source),
            repeat(edges_target),
            repeat(edges_geom),
            repeat(edges_length),
            repeat(unordered_map),
            repeat(node_coords),
            extents,
            starting_ids,
            grid_ids,
            repeat(obj_multi_isochrones.settings.travel_time),
            repeat(obj_multi_isochrones.output.resolution),
        )
        heatmap_multiprocessing(zip_object)

        # TURNED OFF TABLE ISERTION TO NOT CAUSE PROBLEMS ##################################################
        # beginning_time_bulk_insert = time.time()
        # db.add_all(total_inserts)
        # await db.commit()
        # end_time_bulk_insert = time.time()

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
    print_info(f"Total time: [bold magenta]{(end_time - starting_time)}[/bold magenta] seconds")


indicator = CRUDHeatmap()


def main():
    from src.db.session import async_session, sync_session

    db = async_session()
    db_sync = sync_session()
    superuser = asyncio.get_event_loop().run_until_complete(
        CRUDBase(models.User).get_by_key(db, key="id", value=15)
    )
    superuser = superuser[0]
    asyncio.get_event_loop().run_until_complete(
        CRUDHeatmap().prepare_starting_points(db=db, current_user=superuser)
    )
    asyncio.get_event_loop().run_until_complete(
        compute_traveltime(db=db, db_sync=db_sync, current_user=superuser)
    )
    # asyncio.get_event_loop().run_until_complete(CRUDHeatmap().finalize_connectivity_heatmap(db=db))
    # asyncio.get_event_loop().run_until_complete(
    #     CRUDHeatmap().bulk_compute_reached_pois(db=async_session(), current_user=superuser)
    # )
    # asyncio.get_event_loop().run_until_complete(
    # CRUDHeatmap().compute_population_heatmap(db=async_session())
    # )
    # asyncio.get_event_loop().run_until_complete(
    #     CRUDHeatmap().bulk_recompute_scenario(db=db)
    # )
    # asyncio.get_event_loop().run_until_complete(
    #     CRUDHeatmap().bulk_recompute_poi_user(db=db)
    # )

    print("Heatmap is finished. Press Ctrl+C to exit.")
    input()


main()
