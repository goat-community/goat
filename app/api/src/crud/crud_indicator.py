import bisect
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import pyproj
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from geojson import Feature, FeatureCollection
from geopandas import GeoSeries
from rich import print
from shapely import wkb
from shapely.geometry import Polygon
from shapely.ops import transform, unary_union
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, text

from src import crud, schemas
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import legacy_engine
from src.exts.cpp.bind import isochrone as isochrone_cpp
from src.resources.enums import SQLReturnTypes


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

        columns = ", ".join(['"{}"'.format(k) for k in keys])
        if table.schema:
            table_name = "{}.{}".format(table.schema, table.name)
        else:
            table_name = table.name

        sql = "COPY {} ({}) FROM STDIN WITH CSV".format(table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)


class CRUDIndicator:
    # == WALKING AND CYCLING INDICATORS ==#

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
        await db.execute(text("DROP TABLE IF EXISTS temporal.size_isochrone_heatmap;"))
        await db.execute(text("TRUNCATE customer.reached_edge_full_heatmap;"))
        await db.execute(text("TRUNCATE customer.reached_edge_heatmap_grid_calculation;"))
        await db.commit()

        # Reset serials columns
        await db.execute(
            text("ALTER SEQUENCE customer.reached_edge_full_heatmap_id_seq RESTART WITH 1;")
        )
        await db.execute(
            text(
                "ALTER SEQUENCE customer.reached_edge_heatmap_grid_calculation_id_seq RESTART WITH 1;"
            )
        )
        await db.commit()

    async def process_heatmap_edges(self, db: AsyncSession):
        """Process heatmap edges."""

        await db.execute(
            text(
                """INSERT INTO customer.reached_edge_full_heatmap(edge_id, geom)
                    SELECT a.edge_id, ST_TRANSFORM(ST_SETSRID(
                        ST_GeomFromGeoJSON('{"type":"LineString","coordinates":' || a.geom || '}'),
                        3857
                    ), 4326) AS geom  
                    FROM temporal.artificial_full_edges a;"""
            )
        )
        await db.commit()

        await db.execute(
            text(
                """INSERT INTO customer.reached_edge_full_heatmap(geom, edge_id)
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
                WHERE m.edge_id = e.id; """
            )
        )
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

            # Compute isochrones for connectivity heatmap
            await self.compute_connectivity_heatmap(
                db_sync, edges_network, dict_starting_ids, network_ids, distance_limits
            )

            # Compute traveltime
            starting_time_calculation = datetime.now()
            try:
                result = isochrone_cpp(edges_network, network_ids, distance_limits)
            except Exception as e:
                print(f"Error: {e}")
                continue
            calculation_time_catchment = (
                datetime.now() - starting_time_calculation
            ).total_seconds()

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
            network_df.loc[~network_df["start_perc"].isin([0, 1]), "edge_type"] = "p"
            network_df.loc[~network_df["end_perc"].isin([0, 1]), "edge_type"] = "p"
            network_df.loc[
                (network_df["edge_id"] > 2000000000) & (network_df["edge_type"] == "p"),
                "edge_type",
            ] = "ap"
            network_df.loc[
                (network_df["edge_id"] > 2000000000) & (network_df["edge_type"].isnull()),
                "edge_type",
            ] = "a"

            network_df["start_perc"] = network_df["start_perc"] * 10000
            network_df["end_perc"] = network_df["end_perc"] * 10000
            network_df = network_df.astype(
                {
                    "start_cost": int,
                    "end_cost": int,
                    "start_perc": int,
                    "end_perc": int,
                    "geom": str,
                }
            )

            network_df.loc[
                (network_df["edge_type"] != "p") & (network_df["edge_type"] != "ap"), "start_perc"
            ] = np.nan
            network_df.loc[
                (network_df["edge_type"] != "p") & (network_df["edge_type"] != "ap"), "end_perc"
            ] = np.nan
            network_df["end_perc"] = network_df["end_perc"].astype("Int64")
            network_df["start_perc"] = network_df["start_perc"].astype("Int64")

            # Write network to database
            artificial_full_edges = network_df[network_df["edge_type"] == "a"][["edge_id", "geom"]]
            artificial_full_edges = artificial_full_edges.drop_duplicates(
                subset=["edge_id", "geom"], keep="last"
            )
            artificial_full_edges.to_sql(
                "artificial_full_edges",
                legacy_engine,
                method=psql_insert_copy,
                index=True,
                if_exists="replace",
                chunksize=10000,
                schema="temporal",
            )
            full_edges = network_df[network_df["edge_type"].isnull()][["edge_id"]].drop_duplicates(
                "edge_id", keep="last"
            )
            full_edges.to_sql(
                "full_edges",
                legacy_engine,
                method=psql_insert_copy,
                index=True,
                if_exists="replace",
                chunksize=10000,
                schema="temporal",
            )

            edges_traveltime = network_df[
                [
                    "edge_id",
                    "start_cost",
                    "end_cost",
                    "start_perc",
                    "end_perc",
                    "grid_calculation_id",
                    "edge_type",
                ]
            ]
            edges_traveltime.rename(columns={"edge_id": "reached_edge_heatmap_id"}, inplace=True)
            edges_traveltime.to_sql(
                "reached_edge_heatmap_grid_calculation",
                legacy_engine,
                method=psql_insert_copy,
                index=False,
                if_exists="append",
                chunksize=10000,
                schema="customer",
            )

            # Process edges inside database
            await self.process_heatmap_edges(db)

            # Finalize connectivity heatmap
            await self.finalize_connectivity_heatmap(db)

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

    async def compute_connectivity_heatmap(
        self, db, edges_network, dict_starting_ids, starting_ids, distance_limits
    ):
        # Compute isochrones for connectivity heatmap
        isochrones_connectivity = isochrone_cpp(edges_network, starting_ids, distance_limits)

        isochrones = {}
        for isochrone_result in isochrones_connectivity.isochrone:
            isochrones[isochrone_result.start_id] = {}
            for step in sorted(isochrone_result.shape):
                if len(isochrone_result.shape[step]) > 2:
                    if list(isochrones[isochrone_result.start_id].keys()) == []:
                        isochrones[isochrone_result.start_id][step] = {}
                        isochrones[isochrone_result.start_id][step]["shape"] = GeoSeries(
                            Polygon(isochrone_result.shape[step])
                        )
                    else:
                        isochrones[isochrone_result.start_id][step] = {}
                        isochrones[isochrone_result.start_id][step]["shape"] = GeoSeries(
                            isochrones[isochrone_result.start_id][previous_step]["shape"].union(
                                Polygon(isochrone_result.shape[step])
                            )
                        )
                    previous_step = step

        average_area_isochrones = []
        for start_id, shapes in isochrones.items():
            row_to_update = {}
            for step in shapes:
                isochrones[start_id][step]["area_isochrone"] = float(
                    isochrones[start_id][step]["shape"].area
                )
            row_to_update["id"] = dict_starting_ids[start_id]
            row_to_update["area_isochrone"] = sum(
                isochrones[start_id][step]["area_isochrone"] for step in isochrones[start_id]
            )
            average_area_isochrones.append(row_to_update)

        pd.DataFrame(average_area_isochrones).to_sql(
            "size_isochrone_heatmap",
            legacy_engine,
            method=psql_insert_copy,
            index=True,
            if_exists="append",
            schema="temporal",
        )

        return {"msg": "Success"}

    async def finalize_connectivity_heatmap(self, db):
        await db.execute(
            text(
                """WITH grouped AS 
            (
                SELECT g.grid_visualization_id, avg(area_isochrone) area_isochrone  
                FROM temporal.size_isochrone_heatmap s, basic.grid_calculation g
                WHERE s.id = g.id
                GROUP BY g.grid_visualization_id 
            ), 
            with_perentiles AS 
            (
                SELECT g.grid_visualization_id, area_isochrone, ntile(5) over (order by g.area_isochrone) AS percentile_area_isochrone   
                FROM grouped g 
                WHERE g.area_isochrone <> 0 
            )
            UPDATE basic.grid_visualization g 
            SET area_isochrone = w.area_isochrone, percentile_area_isochrone = w.percentile_area_isochrone 
            FROM with_perentiles w 
            WHERE w.grid_visualization_id = g.id;
            """
            )
        )
        await db.commit()

    async def compute_reached_pois_user(
        self, db: AsyncSession, current_user: models.User, data_upload_id: int
    ):
        """Compute the reached pois for a certain data upload id."""

        # Check if data upload in current active data uploads
        if data_upload_id not in current_user.active_data_upload_ids:
            raise HTTPException(
                status_code=400, detail="Data upload id not in your active data uploads."
            )

        # Check if data upload is already computed
        data_upload_obj = await db.execute(
            select(models.DataUpload).where(models.DataUpload.id == data_upload_id)
        )
        data_upload_obj = data_upload_obj.first()[0]
        if data_upload_obj.reached_poi_heatmap_computed == True:
            return {"msg": "Data upload already computed."}

        # Delete old reached pois for the data upload id
        await db.execute(
            delete(models.ReachedPoiHeatmap).where(
                models.ReachedPoiHeatmap.data_upload_id == data_upload_id
            )
        )

        # Compute reached pois for the data upload id
        await db.execute(
            text(
                """
            SELECT r.* 
            FROM basic.study_area s, 
            LATERAL basic.reached_pois_heatmap(:table_name, s.geom, :user_id_input, :scenario_id_input, :data_upload_ids) r 
            WHERE s.id = :active_study_area_id
            """
            ),
            {
                "active_study_area_id": current_user.active_study_area_id,
                "table_name": "poi_user",
                "user_id_input": current_user.id,
                "scenario_id_input": 0,
                "data_upload_ids": [data_upload_id],
            },
        )
        await db.commit()

        scenario_ids = await db.execute(
            text(
                """
            SELECT s.id  
            FROM customer.scenario s 
            WHERE s.data_upload_ids && :data_upload_ids"""
            ),
            {"data_upload_ids": [data_upload_id]},
        )

        scenario_ids = scenario_ids.fetchall()
        scenario_ids = [scenario_id[0] for scenario_id in scenario_ids]

        # Calculate all scenario for the data upload id
        if len(scenario_ids) > 0:
            for scenario_id in scenario_ids:
                await db.execute(
                    text(
                        """
                    SELECT r.* 
                    FROM basic.study_area s, 
                    LATERAL basic.reached_pois_heatmap(:table_name, s.geom, :user_id_input, :scenario_id_input) r 
                    WHERE s.id = :active_study_area_id
                    """
                    ),
                    {
                        "active_study_area_id": current_user.active_study_area_id,
                        "table_name": "poi_modified",
                        "user_id_input": current_user.id,
                        "scenario_id_input": scenario_id,
                    },
                )
                await db.commit()

        # Update data upload
        data_upload_obj.reached_poi_heatmap_computed = True
        db.add(data_upload_obj)
        await db.commit()

    async def bulk_compute_reached_pois(self, db: AsyncSession, current_user: models.User):
        # Reset reached_pois_heatmap table
        await db.execute(text("TRUNCATE customer.reached_poi_heatmap;"))
        await db.execute(
            text("ALTER SEQUENCE customer.reached_poi_heatmap_id_seq RESTART WITH 1;")
        )
        await db.commit()

        # Make all data uploads not computed
        await db.execute(
            text(
                "UPDATE customer.data_upload SET reached_poi_heatmap_computed = FALSE WHERE study_area_id = :active_study_area_id;"
            ),
            {"active_study_area_id": current_user.active_study_area_id},
        )

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
            calculation_geom = await db.execute(
                "SELECT ST_ASTEXT(ST_UNION(geom)) AS geom FROM temporal.heatmap_grid_helper WHERE cid = :cid",
                {"cid": kmeans_class},
            )
            calculation_geom = calculation_geom.fetchall()[0][0]
            await db.execute(
                text(
                    """SELECT basic.reached_pois_heatmap(
                    :table_name, ST_SETSRID(ST_GEOMFROMTEXT(:calculation_geom), 4326), 
                    :user_id_input, :scenario_id_input)"""
                ),
                {
                    "table_name": "poi",
                    "calculation_geom": calculation_geom,
                    "user_id_input": current_user.id,
                    "scenario_id_input": 0,
                },
            )
            await db.commit()

            print(
                "#################################################################################################################"
            )
            print(
                f"INFO: You computed [bold magenta]{cnt}[/bold magenta] out of [bold magenta]{cnt_sections}[/bold magenta] sections."
            )
            print(
                f"INFO: This section took [bold magenta]{(datetime.now() - starting_time_section).total_seconds()} s[/bold magenta]."
            )
            print(
                "#################################################################################################################"
            )

    async def compute_population_heatmap(self, db: AsyncSession):
        start_time = datetime.now()
        await db.execute(
            text(
                """
            UPDATE basic.grid_visualization
            SET population = NULL, percentile_population = NULL;
            """
            )
        )
        await db.commit()
        await db.execute(
            text(
                """
            WITH grouped_population AS 
            (
                SELECT g.id, SUM(p.population) AS population   
                FROM basic.population p, basic.grid_visualization g
                WHERE ST_Intersects(g.geom, p.geom)
                GROUP BY g.id 
            )
            UPDATE basic.grid_visualization v
            SET percentile_population = 
            (CASE WHEN p.population BETWEEN 1 AND 80 THEN 1 
            WHEN p.population BETWEEN 80 AND 200 THEN 2
            WHEN p.population BETWEEN 200 AND 500 THEN 3 
            WHEN p.population BETWEEN 500 AND 1000 THEN 4 
            WHEN p.population > 1000 THEN 5 END),
            population = p.population
            FROM grouped_population p 
            WHERE p.population IS NOT NULL
            AND v.id = p.id; 
            """
            )
        )
        await db.execute(
            text(
                """
            UPDATE basic.grid_visualization 
            SET percentile_population = 0 
            WHERE population IS NULL;
            """
            )
        )
        await db.commit()
        print(
            "#################################################################################################################"
        )
        print(
            f"INFO: Preparing population for heatmap took [bold magenta]{(datetime.now() - start_time).total_seconds()}s[/bold magenta]."
        )
        print(
            "#################################################################################################################"
        )

    # == PUBLIC TRANSPORT INDICATORS ==#

    async def count_pt_service_stations(
        self, db: AsyncSession, start_time, end_time, weekday, study_area_id, return_type
    ) -> Any:
        """Get count of public transport stations for every service."""

        template_sql = SQLReturnTypes[return_type.value].value
        stations_count = await db.execute(
            text(
                template_sql
                % f"""
                SELECT * FROM basic.count_public_transport_services_station(:study_area_id, :start_time, :end_time, :weekday)
                """
            ),
            {
                "study_area_id": study_area_id,
                "start_time": timedelta(seconds=start_time),
                "end_time": timedelta(seconds=end_time),
                "weekday": weekday,
            },
        )
        stations_count = stations_count.fetchall()[0][0]
        return stations_count

    async def compute_oev_gueteklassen(
        self,
        db: AsyncSession,
        start_time,
        end_time,
        weekday,
        study_area_id,
    ) -> FeatureCollection:
        """
        Calculate the OEV-Gueteklassen for a given time period and weekday.
        """
        # TODO: Use isochrone calculation instead of buffer
        station_config = {
            "groups": {
                "0": "B",  # route_type: category of public transport route
                "1": "A",
                "2": "A",
                "3": "C",
                "4": "B",
                "5": "B",
                "6": "B",
                "7": "B",
                "11": "B",
                "12": "B",
            },
            "time_frequency": [0, 4, 10, 19, 39, 60, 120],
            "categories": [
                {
                    "A": 1,  # i.e. types of transports in category A are in transport stop category I
                    "B": 1,
                    "C": 2,
                },
                {"A": 1, "B": 2, "C": 3},
                {"A": 2, "B": 3, "C": 4},
                {"A": 3, "B": 4, "C": 5},
                {"A": 4, "B": 5, "C": 6},
                {"A": 5, "B": 6, "C": 6},
            ],
            "classification": {
                "1": {300: "A", 500: "A", 750: "B", 1000: "C"},
                "2": {300: "A", 500: "B", 750: "C", 1000: "D"},
                "3": {300: "B", 500: "C", 750: "D", 1000: "E"},
                "4": {300: "C", 500: "D", 750: "E", 1000: "F"},
                "5": {300: "D", 500: "E", 750: "F"},
                "6": {300: "E", 500: "F"},
                "7": {300: "F"},
            },
        }

        time_window = (end_time - start_time) / 60
        stations = await db.execute(
            text(
                """
                SELECT trip_cnt, ST_TRANSFORM(geom, 3857) as geom 
                FROM basic.count_public_transport_services_station(:study_area_id, :start_time, :end_time, :weekday)
                """
            ),
            {
                "study_area_id": study_area_id,
                "start_time": timedelta(seconds=start_time),
                "end_time": timedelta(seconds=end_time),
                "weekday": weekday,
            },
        )
        stations = stations.fetchall()

        project = pyproj.Transformer.from_crs(
            pyproj.CRS("EPSG:3857"), pyproj.CRS("EPSG:4326"), always_xy=True
        ).transform
        classificiation_buffers = {}
        for station in stations:
            station_geom = wkb.loads(station.geom, hex=True)
            trip_cnt = station["trip_cnt"]
            # - find station group
            station_groups = []  # list of station groups e.g [A, B, C]
            acc_trips = {}  # accumulated trips per station group
            for route_type, trip_count in trip_cnt.items():
                station_group = station_config["groups"].get(str(route_type))
                if station_group:
                    station_groups.append(station_group)
                    acc_trips[station_group] = acc_trips.get(station_group, 0) + trip_count
            station_group = min(station_groups)  # the highest priority (e.g A )
            station_group_trip_count = acc_trips[station_group]
            if station_group_trip_count == 0:
                continue
            station_group_trip_time_frequency = time_window / (station_group_trip_count / 2)
            # - find station category based on time frequency and group
            time_interval = bisect.bisect_left(
                station_config["time_frequency"], station_group_trip_time_frequency
            )
            station_category = station_config["categories"][time_interval - 1].get(station_group)
            if not station_category:
                continue
            # - find station classification based on category
            station_classification = station_config["classification"][str(station_category)]
            for buffer_dist, classification in station_classification.items():

                buffer_geom = station_geom.buffer(buffer_dist)
                # add geom in classfication_shapes
                if classification not in classificiation_buffers:
                    classificiation_buffers[classification] = [buffer_geom]
                else:
                    classificiation_buffers[classification].append(buffer_geom)

        features = []
        agg_union = None
        for classification, shapes in dict(sorted(classificiation_buffers.items())).items():
            union_geom = unary_union(shapes)
            difference_geom = union_geom
            if agg_union:
                difference_geom = union_geom.difference(agg_union)
                agg_union = agg_union.union(union_geom)
            else:
                agg_union = union_geom
            feature = Feature(
                geometry=transform(project, difference_geom),
                properties={"class": classification},
            )
            if feature.geometry is not None:
                features.append(feature)

        return FeatureCollection(features)


indicator = CRUDIndicator()

# def main():

#     from src.db.session import async_session, sync_session
#     test_user = models.User(id=15, active_study_area_id=83110000)
#     asyncio.get_event_loop().run_until_complete(CRUDHeatmap().bulk_compute_reached_pois(db=async_session(), current_user=test_user))


# main()
# db = async_session()
# db_sync = sync_session()
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().prepare_starting_points(db=db, current_user=test_user))
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().clean_tables(db=db))
# asyncio.get_event_loop().run_until_complete(
#          CRUDHeatmap().compute_traveltime(db=db, db_sync=db_sync, current_user=test_user)
# )
# asyncio.get_event_loop().run_until_complete(
#          CRUDHeatmap().finalize_connectivity_heatmap(db=db)
# )
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().bulk_compute_reached_pois(db=async_session(), current_user=test_user))
# asyncio.get_event_loop().run_until_complete(CRUDHeatmap().compute_population_heatmap(db=async_session()))
