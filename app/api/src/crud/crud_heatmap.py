import asyncio
from datetime import datetime, timedelta

import pandas as pd
from fastapi import HTTPException
from geopandas import GeoSeries
from rich import print
from shapely.geometry import Polygon
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, text

from src import crud, schemas
from src.core.isochrone import compute_isochrone
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
                SELECT id FROM basic.study_area WHERE id IN (281460, 44021, 83110000, 91620000, 9564, 9188, 9174, 9178, 9177, 9175, 9184, 9188, 9179, 9564)
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

    async def compute_traveltime(
        self, db: AsyncSession, db_sync: Session, current_user: models.User
    ):
        before = datetime.now()
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

        for kmeans_class in kmeans_classes:
            cnt += 1
            starting_time_section = datetime.now()

            # Get starting points for starting grids
            starting_points = await db.execute(
                text(
                    """SELECT v.id AS starting_id, c.id AS grid_calculation_id, ST_X(ST_CENTROID(v.geom)) AS x, ST_Y(ST_CENTROID(v.geom)) AS y   
                    FROM temporal.heatmap_starting_vertices v, basic.grid_calculation c, temporal.heatmap_grid_helper h  
                    WHERE ST_Intersects(v.geom, c.geom)
                    AND c.grid_visualization_id = h.id 
                    AND h.cid = :cid 
                    AND h.already_processed = False 
                    """
                ),
                {"cid": kmeans_class},
            )

            starting_points = starting_points.fetchall()
            starting_id = [i[0] for i in starting_points]

            # Check if there are no starting points
            if len(starting_id) == 0:
                continue

            grid_ids = [i[1] for i in starting_points]
            dict_starting_ids = dict(zip(starting_id, grid_ids))

            starting_points_dto_arr = []
            for i in starting_points:
                starting_points_dto_arr.append(IsochroneStartingPointCoord(lat=i[3], lon=i[2]))

            # Create Isochrone DTO for heatmap calculation
            # TODO: Adjust DTO to properly work with heatmap
            obj_multi_isochrones = IsochroneDTO(
                mode="walking",
                settings=IsochroneSettings(
                    travel_time=20,
                    speed=5,
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
            starting_time_network = datetime.now()
            network, starting_ids = await crud.isochrone.read_network(
                db=db,
                obj_in=obj_multi_isochrones,
                current_user=current_user,
                isochrone_type=schemas.isochrone.IsochroneTypeEnum.heatmap.value,
            )

            # # Compute isochrones for connectivity heatmap
            # await self.compute_connectivity_heatmap(
            #     db_sync, edges_network, dict_starting_ids, network_ids, distance_limits
            # )

            # Compute traveltime
            starting_time_calculation = datetime.now()
            calculation_time_catchment = (
                datetime.now() - starting_time_calculation
            ).total_seconds()

            # TODO:
            # Compute isochrone using new function

            for starting_id in starting_ids:
                grid = compute_isochrone(
                    network,
                    starting_id,
                    obj_multi_isochrones.settings.travel_time,
                    obj_multi_isochrones.output.resolution,
                )
                print("Finished")

            # FOR LOOP through starting points that compute individual isochrones
            # Use core.isochrone
            # Compress costs column
            # Save result inside the matrix

            # Finalize connectivity heatmap
            # await self.finalize_connectivity_heatmap(db)

            print(
                "#################################################################################################################"
            )
            print(
                f"INFO: You computed [bold magenta]{cnt}[/bold magenta] out of [bold magenta]{cnt_sections}[/bold magenta] added."
            )
            print(
                f"INFO: Section contains [bold magenta]{len(starting_points)}[/bold magenta] starting points"
            )
            print(
                f"INFO: This section took [bold magenta]{(datetime.now() - starting_time_section).total_seconds()} s[/bold magenta]. For reading the network [bold magenta]{reading_time_network} s[/bold magenta] and for computing the catchments [bold magenta]{calculation_time_catchment} s[/bold magenta]."
            )
            print(
                "#################################################################################################################"
            )

        print(
            f"It took [bold magenta]{(datetime.now() - before).total_seconds() / 60} minutes[/bold magenta] to compute the isochrones."
        )


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
        CRUDHeatmap().compute_traveltime(db=db, db_sync=db_sync, current_user=superuser)
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
