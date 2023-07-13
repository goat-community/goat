import bisect
from datetime import timedelta
from typing import Any

import json
import pyproj
from geojson import Feature, FeatureCollection
from geopandas import read_postgis
from shapely import wkb
from shapely.ops import transform, unary_union
from src.db.session import legacy_engine as db_sync_engine
from pandas.io.sql import read_sql

class CRUDIndicator:
    async def count_pt_service_stations(
        self, start_time, end_time, weekday, study_area_id
    ) -> Any:
        """Get count of public transport stations for every service."""
        stations_count = read_postgis(
            f"""
            SELECT * FROM basic.count_public_transport_services_station({study_area_id},
            '{timedelta(seconds=start_time)}',
            '{timedelta(seconds=end_time)}',
            {weekday})
            """,
            con=db_sync_engine,
        )
        stations_count = json.loads(stations_count.to_json())

        return stations_count

    async def compute_oev_gueteklassen(
        self,
        start_time,
        end_time,
        weekday,
        study_area_ids,
        station_config,
    ) -> FeatureCollection:
        """
        Calculate the OEV-Gueteklassen for a given time period and weekday.
        """
        # TODO: Use isochrone calculation instead of buffer

        time_window = (end_time - start_time) / 60

        # Get max buffer size from config to find buffer size for study area
        buffer_distances = []
        for cls in station_config["classification"].items():
            buffer_distances = buffer_distances + list(cls[1].keys())
        max_buffer_distance = max(map(int, buffer_distances))

        stations = []
        for study_area_id in study_area_ids:

            fetched_stations = read_sql(
                f"""
                    SELECT trip_cnt, ST_TRANSFORM(geom, 3857) as geom
                    FROM basic.count_public_transport_services_station({study_area_id},
                    '{timedelta(seconds=start_time)}',
                    '{timedelta(seconds=end_time)}',
                    {weekday},
                    {max_buffer_distance},
                    ARRAY[{list(station_config["groups"].keys())}])
                """,
                con=db_sync_engine,
            )

            fetched_stations = list(fetched_stations.to_records(index=False))
            stations = stations + fetched_stations

        project = pyproj.Transformer.from_crs(
            pyproj.CRS("EPSG:3857"), pyproj.CRS("EPSG:4326"), always_xy=True
        ).transform
        classificiation_buffers = {}
        for station in stations:
            station_geom = wkb.loads(station.geom, hex=True)
            trip_cnt = station["trip_cnt"]
            # - find station group
            station_groups = []  # list of station groups e.g [A, B, C]
            station_group_trip_count = 0  # accumulated trips per station group
            for route_type, trip_count in trip_cnt.items():
                station_group = station_config["groups"].get(str(route_type))
                if station_group:
                    station_groups.append(station_group)
                    station_group_trip_count += trip_count

            station_group = min(station_groups)  # the highest priority (e.g A )
            if station_group_trip_count == 0:
                continue
            station_group_trip_time_frequency = time_window / (station_group_trip_count / 2)
            # - find station category based on time frequency and group
            time_interval = bisect.bisect_left(
                station_config["time_frequency"], station_group_trip_time_frequency
            )
            if time_interval == len(station_config["time_frequency"]):
                continue  # no category found
            station_category = station_config["categories"][time_interval - 1].get(station_group)

            if not station_category:
                continue
            # - find station classification based on category
            station_classification = station_config["classification"][str(station_category)]
            for buffer_dist, classification in station_classification.items():

                buffer_geom = station_geom.buffer(int(buffer_dist))
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
