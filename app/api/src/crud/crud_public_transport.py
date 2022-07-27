import bisect
import datetime
from typing import Any

import pyproj
from geojson import Feature, FeatureCollection
from rich import print
from shapely import wkb
from shapely.ops import transform, unary_union
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from src.db import models
from src.resources.enums import ReturnType, SQLReturnTypes


class CRUDPublicTransport:
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
                "start_time": datetime.timedelta(seconds=start_time),
                "end_time": datetime.timedelta(seconds=end_time),
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
            "time_frequency": [0, 4, 10, 19, 39, 60],
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
                {"B": 7, "C": 7},
            ],
            "classification": {
                "1": {300: "A", 500: "A", 750: "B", 1000: "C"},
                "2": {300: "A", 500: "B", 750: "C", 1000: "D"},
                "3": {
                    300: "B",
                    500: "C",
                    750: "D",
                },
                "4": {300: "C", 500: "D"},
                "5": {300: "D"},
                "6": {300: "E"},
                "7": {300: "F"},
            },
        }

        time_window = (end_time - start_time) / 60
        stations = await db.execute(
            text(
                """
                SELECT trip_cnt, ST_TRANSFORM(geom, 3857) as geom FROM basic.count_public_transport_services_station(:study_area_id, :start_time, :end_time, :weekday)
                """
            ),
            {
                "study_area_id": study_area_id,
                "start_time": datetime.timedelta(seconds=start_time),
                "end_time": datetime.timedelta(seconds=end_time),
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
            station_group_trip_time_frequency = time_window / station_group_trip_count
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
            features.append(feature)
        return FeatureCollection(features)


public_transport = CRUDPublicTransport()
