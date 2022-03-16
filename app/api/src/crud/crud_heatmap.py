import asyncio
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
import psycopg2
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from numpy import ndarray
from pyparsing import dblQuotedString
from rich import print
from sqlalchemy import event
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import delete, text

from src import crud, schemas
from src.core.config import settings
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import legacy_engine
from src.exts.cpp.bind import isochrone as isochrone_cpp


class CRUDGridCalculation(
    CRUDBase[models.GridCalculation, models.GridCalculation, models.GridCalculation]
):
    pass

# Alternative to_sql() *method* for DBs that support COPY FROM
import csv
from io import StringIO


def psql_insert_copy(table, conn, keys, data_iter):
    """
    Execute SQL statement inserting data

    Parameters
    ----------
    table : pandas.io.sql.SQLTable
    conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
    keys : list of str
        Column names
    data_iter : Iterable that iterates the values to be inserted
    """
    # gets a DBAPI connection that can provide a cursor
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ', '.join(['"{}"'.format(k) for k in keys])
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
            table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)

class CRUDHeatmap:
    async def prepare_starting_points(self, db: AsyncSession, current_user: models.User):
        """Get starting points for heatmap calculation."""

        await db.execute(text("DROP TABLE IF EXISTS temporal.heatmap_grid_helper;"))
        await db.commit()
        query = text(
            """
            CREATE TABLE temporal.heatmap_grid_helper AS 
            WITH cnt AS 
            (
                SELECT count(*) cnt 
                FROM basic.grid_visualization g 
            )
            SELECT ST_ClusterKMeans(geom, (cnt / 50)::integer) OVER() AS cid, id, geom, False as already_processed  
            FROM basic.grid_visualization g, cnt; 
            """
        )
        await db.execute(query)
        await db.commit()

    async def clean_tables(self, db: AsyncSession):
        """Clean tables reached edges."""
        # Clean tables for heatmap edges
        await db.execute(text("TRUNCATE customer.reached_edge_full_heatmap;"))
        await db.execute(text("TRUNCATE customer.reached_edge_heatmap_grid_calculation;"))
        await db.commit()

        # Reset serials columns
        await db.execute(text("ALTER SEQUENCE customer.reached_edge_full_heatmap_id_seq RESTART WITH 1;"))
        await db.execute(text("ALTER SEQUENCE customer.reached_edge_heatmap_grid_calculation_id_seq RESTART WITH 1;"))
        await db.commit()

    async def process_heatmap_edges(self, db: AsyncSession):
        """Process heatmap edges."""

        await db.execute(text("""INSERT INTO customer.reached_edge_full_heatmap(edge_id, geom)
        SELECT a.edge_id, ST_TRANSFORM(ST_SETSRID(
            ST_GeomFromGeoJSON('{"type":"LineString","coordinates":' || a.geom || '}'),
            3857
        ), 4326) AS geom  
        FROM temporal.artificial_full_edges a;""")) 
        await db.commit()

        await db.execute(text("""INSERT INTO customer.reached_edge_full_heatmap(geom, edge_id)
        WITH merged AS 
        (
            SELECT f.edge_id
            FROM temporal.full_edges f
            LEFT JOIN customer.reached_edge_full_heatmap r 
            ON f.edge_id = r.edge_id 
            WHERE r.edge_id IS NULL  
        )
        SELECT e.geom, m.edge_id 
        FROM merged m, basic.edge e 
        WHERE m.edge_id = e.id; """)) 
        await db.commit()

    async def compute_traveltime(self, db: AsyncSession, current_user: models.User):
        before = datetime.now()
        kmeans_classes = await db.execute(
            text("SELECT DISTINCT cid FROM temporal.heatmap_grid_helper;")
        )
        kmeans_classes = kmeans_classes.fetchall()
        kmeans_classes = [c[0] for c in kmeans_classes]
        
        await db.execute("SELECT basic.heatmap_prepare_artificial(:kmeans_classes);", {"kmeans_classes": kmeans_classes})
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
            grid_ids = [i[1] for i in starting_points]
            x = [i[2] for i in starting_points]
            y = [i[3] for i in starting_points]
            dict_starting_ids = dict(zip(starting_id, grid_ids))

            obj_multi_isochrones = schemas.IsochroneMulti(
                user_id=current_user.id,
                scenario_id=0,
                speed=1.333,
                modus="default",
                n=1,
                minutes=20,
                routing_profile="walking_standard",
                active_upload_ids=[],
                x=x,
                y=y,
            )
            # Read network
            starting_time_network = datetime.now()
            network = await crud.isochrone.read_network(
                db,
                schemas.isochrone.IsochroneTypeEnum.heatmap.value,
                obj_multi_isochrones,
                jsonable_encoder(obj_multi_isochrones),
            )

            edges_network = network[0]
            network_ids = network[1]
            distance_limits = network[2]
            reading_time_network = (datetime.now() - starting_time_network).total_seconds()
          
            # Compute isochrones
            starting_time_calculation = datetime.now()
            try:
                result = isochrone_cpp(edges_network, network_ids, distance_limits)
            except Exception as e:
                print(f"Error: {e}")
                continue
            calculation_time_catchment = (datetime.now() - starting_time_calculation).total_seconds()

            network_df = pd.DataFrame(
                [
                    {
                        "edge_id": getattr(f, "edge"),
                        "start_cost": getattr(f, "start_cost"),
                        "end_cost": getattr(f, "end_cost"),
                        "start_perc": getattr(f, "start_perc"),
                        "end_perc": getattr(f, "end_perc"),
                        "start_id": getattr(f, "start_id"),
                        "geom": getattr(f, "shape"),
                    }
                    for f in result.network
                ]
            )
            network_df["grid_calculation_id"] = network_df["start_id"].map(dict_starting_ids)

            # Classify network
            network_df.loc[~network_df["start_perc"].isin([0, 1]), "edge_type"] = 'p'
            network_df.loc[~network_df["end_perc"].isin([0, 1]), "edge_type"] = 'p'
            network_df.loc[(network_df["edge_id"] > 2000000000) & (network_df["edge_type"] == 'p'), "edge_type"] = 'ap'
            network_df.loc[(network_df["edge_id"] > 2000000000) & (network_df["edge_type"].isnull()), "edge_type"] = 'a'

            network_df["start_perc"] = network_df["start_perc"] * 10000
            network_df["end_perc"] = network_df["end_perc"] * 10000
            network_df = network_df.astype({"start_cost": int, "end_cost": int, "start_perc": int, "end_perc": int, "geom": str})

            network_df.loc[(network_df["edge_type"] != 'p') & (network_df["edge_type"] != 'ap'), "start_perc"] = np.nan
            network_df.loc[(network_df["edge_type"] != 'p') & (network_df["edge_type"] != 'ap'), "end_perc"] = np.nan
            network_df['end_perc'] = network_df['end_perc'].astype('Int64')
            network_df['start_perc'] = network_df['start_perc'].astype('Int64')

            # Write network to database
            artificial_full_edges = network_df[network_df["edge_type"] == "a"][["edge_id", "geom"]]
            artificial_full_edges = artificial_full_edges.drop_duplicates(subset=['edge_id', 'geom'], keep="last")
            artificial_full_edges.to_sql("artificial_full_edges", legacy_engine, method=psql_insert_copy, index=True, if_exists="replace", chunksize=10000, schema="temporal")

            # artificial_partial_edges = network_df[network_df["edge_type"] == "ap"][["edge_id", "geom"]]
            # artificial_partial_edges.to_sql("artificial_partial_edges", legacy_engine, method=psql_insert_copy, index=True, if_exists="replace", chunksize=10000, schema="temporal")
            full_edges = network_df[network_df["edge_type"].isnull()][["edge_id"]].drop_duplicates("edge_id", keep="last")
            full_edges.to_sql("full_edges", legacy_engine, method=psql_insert_copy, index=True, if_exists="replace", chunksize=10000, schema="temporal")

            edges_traveltime = network_df[["edge_id", "start_cost", "end_cost", "start_perc", "end_perc", "grid_calculation_id", "edge_type"]]
            edges_traveltime.rename(columns={"edge_id": "reached_edge_heatmap_id"}, inplace=True)
            edges_traveltime.to_sql("reached_edge_heatmap_grid_calculation", legacy_engine, method=psql_insert_copy, index=False, if_exists="append", chunksize=10000, schema="customer")
            
            # Process edges inside database
            await self.process_heatmap_edges(db)

            print("#################################################################################################################")
            print(f"INFO: You computed [bold magenta]{cnt}[/bold magenta] out of [bold magenta]{cnt_sections}[/bold magenta] added.")
            print(f"INFO: Section contains [bold magenta]{len(starting_points)}[/bold magenta] starting points")
            print(f"INFO: This section took [bold magenta]{(datetime.now() - starting_time_section).total_seconds()} s[/bold magenta]. For reading the network [bold magenta]{reading_time_network} s[/bold magenta] and for computing the catchments [bold magenta]{calculation_time_catchment} s[/bold magenta].")
            print("#################################################################################################################")

        print(f"It took [bold magenta]{(datetime.now() - before).total_seconds() / 60} minutes[/bold magenta] to compute the isochrones.")

    async def compute_reached_pois_scenario(self, db: AsyncSession, current_user: models.User, scenario_id: int):
        """Compute the reached for a certain scenario id. It deletes previously computed calculations and computes it again."""
        
        # Check if user owns the scenario
        scenario = await crud.scenario.get_by_multi_keys(db, keys={"id": scenario_id, "user_id": current_user.id})
        if len(scenario) == 0:
            raise HTTPException(status_code=400, detail="Scenario not found")

        # Delete old reached pois for the data upload id
        await db.execute(delete(models.ReachedPoiHeatmap).where(models.ReachedPoiHeatmap.scenario_id == scenario_id))
        
        # Compute reached pois for the data upload id 
        await db.execute(
            text("""
            SELECT r.* 
            FROM basic.study_area s, 
            LATERAL basic.reached_pois_heatmap(:table_name, s.geom, :user_id_input, :scenario_id_input) r 
            WHERE s.id = :active_study_area_id
            """), {"active_study_area_id": current_user.active_study_area_id, "table_name": "poi_modified", 
            "user_id_input": current_user.id, "scenario_id_input": scenario_id}
        )
        await db.commit()

    async def compute_reached_pois_user(self, db: AsyncSession, current_user: models.User, data_upload_id: int):
        """Compute the reached pois for a certain data upload id."""

        # Check if data upload in current active data uploads
        if data_upload_id not in current_user.active_data_upload_ids:
            raise HTTPException(status_code=400, detail="Data upload id not in your active data uploads.")

        #Check if data upload is already computed
        data_upload_obj = await db.execute(select(models.DataUpload).where(models.DataUpload.id == data_upload_id))
        data_upload_obj = data_upload_obj.first()[0]
        if data_upload_obj.reached_poi_heatmap_computed == True:
            raise HTTPException(status_code=400, detail="Data upload is already computed.")
        
        # Delete old reached pois for the data upload id
        await db.execute(delete(models.ReachedPoiHeatmap).where(models.ReachedPoiHeatmap.data_upload_id == data_upload_id))

        # Compute reached pois for the data upload id 
        await db.execute(
            text("""
            SELECT r.* 
            FROM basic.study_area s, 
            LATERAL basic.reached_pois_heatmap(:table_name, s.geom, :user_id_input, :scenario_id_input, :data_upload_ids) r 
            WHERE s.id = :active_study_area_id
            """), {"active_study_area_id": current_user.active_study_area_id, "table_name": "poi_user", 
            "user_id_input": current_user.id, "scenario_id_input": 0, "data_upload_ids": [data_upload_id]}
        )
        await db.commit()

        scenario_ids = await db.execute(
            text("""
            SELECT s.id  
            FROM customer.scenario s 
            WHERE s.data_upload_ids && :data_upload_ids"""
            ), {"data_upload_ids": [data_upload_id]}
        )

        scenario_ids = scenario_ids.fetchall()
        scenario_ids = [scenario_id[0] for scenario_id in scenario_ids]

        # Calculate all scenario for the data upload id
        if len(scenario_ids) > 0:
            for scenario_id in scenario_ids:
                await db.execute(
                    text("""
                    SELECT r.* 
                    FROM basic.study_area s, 
                    LATERAL basic.reached_pois_heatmap(:table_name, s.geom, :user_id_input, :scenario_id_input) r 
                    WHERE s.id = :active_study_area_id
                    """), {"active_study_area_id": current_user.active_study_area_id, "table_name": "poi_modified", 
                    "user_id_input": current_user.id, "scenario_id_input": scenario_id}
                )
                await db.commit()

        # Update data upload
        data_upload_obj.reached_poi_heatmap_computed = True
        db.add(data_upload_obj)
        await db.commit()

    async def bulk_compute_reached_pois(self, db: AsyncSession, current_user: models.User):
        # Reset reached_pois_heatmap table 
        await db.execute(text("TRUNCATE customer.reached_poi_heatmap;"))
        await db.execute(text("ALTER SEQUENCE customer.reached_poi_heatmap_id_seq RESTART WITH 1;"))
        await db.commit()

        kmeans_classes = await db.execute(
            text("SELECT DISTINCT cid FROM temporal.heatmap_grid_helper;")
        )
        kmeans_classes = kmeans_classes.fetchall()
        kmeans_classes = [c[0] for c in kmeans_classes]

        cnt = 0
        cnt_sections = len(kmeans_classes)
        for kmeans_class in kmeans_classes:
            starting_time_section = datetime.now()
            cnt += 1
            calculation_geom = await db.execute("SELECT ST_ASTEXT(ST_UNION(geom)) AS geom FROM temporal.heatmap_grid_helper WHERE cid = :cid", {"cid": kmeans_class})
            calculation_geom = calculation_geom.fetchall()[0][0]
            await db.execute(
                text("""SELECT basic.reached_pois_heatmap(
                    :table_name, ST_SETSRID(ST_GEOMFROMTEXT(:calculation_geom), 4326), 
                    :user_id_input, :scenario_id_input)"""), 
                    {"table_name" : "poi", "calculation_geom": calculation_geom, 
                    "user_id_input": current_user.id, "scenario_id_input": 0}
            )
            await db.commit()
            
            print("#################################################################################################################")
            print(f"INFO: You computed [bold magenta]{cnt}[/bold magenta] out of [bold magenta]{cnt_sections}[/bold magenta] sections.")
            print(f"INFO: This section took [bold magenta]{(datetime.now() - starting_time_section).total_seconds()} s[/bold magenta].")
            print("#################################################################################################################")

heatmap = CRUDHeatmap()

#from src.db.session import async_session

#test_user = models.User(id=4, active_study_area_id=1)
#db = async_session()
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().prepare_starting_points(db=db, current_user=test_user))
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().clean_tables(db=db))
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().compute_traveltime(db=db, current_user=test_user))

#asyncio.run(CRUDHeatmap().bulk_compute_reached_pois(db=async_session(), current_user=test_user))


