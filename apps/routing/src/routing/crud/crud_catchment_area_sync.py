import os
import time
import uuid
from typing import Any

import polars as pl
from routing.core.config import settings
from routing.schemas.catchment_area import (
    SEGMENT_DATA_SCHEMA,
    VALID_BICYCLE_CLASSES,
    VALID_CAR_CLASSES,
    VALID_WALKING_CLASSES,
    CatchmentAreaRoutingTypeActiveMobility,
    CatchmentAreaRoutingTypeCar,
    CatchmentAreaTravelTimeCostActiveMobility,
    CatchmentAreaTravelTimeCostMotorizedMobility,
    ICatchmentAreaActiveMobility,
    ICatchmentAreaCar,
)
from routing.schemas.error import BufferExceedsNetworkError, DisconnectedOriginError
from routing.utils import make_dir
from tqdm import tqdm

####################################################################################################
# TODO: Refactor and fix
####################################################################################################


class FetchRoutingNetwork:
    def __init__(self, db_cursor):
        self.db_cursor = db_cursor

    def fetch(self):
        """Fetch routing network (processed segments) and load into memory."""

        start_time = time.time()

        # Get network H3 cells
        h3_3_grid = []
        try:
            # TODO Don't hardcode PT geofence, compute for all of Europe
            # Buffer geofence by 80 km while computing Germany matrix to process border regions correctly
            sql_get_h3_3_grid = """
                WITH region AS (
                    SELECT ST_Buffer(ST_Union(geom)::geography, 80000)::geometry AS geom FROM basic.geofence_pt
                )
                SELECT g.h3_short FROM region r,
                LATERAL basic.fill_polygon_h3_3(r.geom) g;
            """
            self.db_cursor.execute(sql_get_h3_3_grid)
            result = self.db_cursor.fetchall()
            for h3_index in result:
                h3_3_grid.append(h3_index[0])
        except Exception as e:
            print(e)
            # TODO Throw appropriate exception

        # Load segments into polars data frames
        segments_df = {}
        df_size = 0.0
        try:
            # Create cache dir if it doesn't exist
            make_dir(settings.CACHE_DIR)

            for index in tqdm(
                range(len(h3_3_grid)), desc="Loading H3_3 grid", unit=" cell"
            ):
                h3_index = h3_3_grid[index]

                if os.path.exists(f"{settings.CACHE_DIR}/{h3_index}.parquet"):
                    segments_df[h3_index] = pl.read_parquet(
                        f"{settings.CACHE_DIR}/{h3_index}.parquet"
                    )
                else:
                    segments_df[h3_index] = pl.read_database_uri(
                        query=f"""
                            SELECT
                                edge_id AS id, length_m, length_3857, class_, impedance_slope, impedance_slope_reverse,
                                impedance_surface, CAST(coordinates_3857 AS TEXT) AS coordinates_3857,
                                maxspeed_forward, maxspeed_backward, source, target, h3_3, h3_6
                            FROM user_data.street_network_line_b6ddb594bfed4a8788b214af45378d75
                            WHERE h3_3 = {h3_index}
                        """,
                        uri=settings.POSTGRES_DATABASE_URI,
                        schema_overrides=SEGMENT_DATA_SCHEMA,
                    )
                    segments_df[h3_index] = segments_df[h3_index].with_columns(
                        pl.col("coordinates_3857").str.json_extract()
                    )

                    with open(f"{settings.CACHE_DIR}/{h3_index}.parquet", "wb") as file:
                        segments_df[h3_index].write_parquet(file)

                df_size += segments_df[h3_index].estimated_size("gb")
        except Exception as e:
            print(e)

        print(f"Network load time: {round((time.time() - start_time) / 60, 1)} min")
        print(f"Network in-memory size: {round(df_size, 1)} GB")

        return segments_df


class CRUDCatchmentArea:
    def __init__(self, db_connection, db_cursor) -> None:
        self.db_connection = db_connection
        self.db_cursor = db_cursor

    def read_network(
        self,
        routing_network: dict,
        obj_in: ICatchmentAreaActiveMobility | ICatchmentAreaCar,
        input_table: str,
        num_points: int,
        origin_point_cell_resolution: int,
    ) -> Any:
        """Read relevant sub-network for catchment area calculation from polars dataframe."""

        # Get valid segment classes based on transport mode
        if type(obj_in) == ICatchmentAreaActiveMobility:
            valid_segment_classes = (
                VALID_WALKING_CLASSES
                if obj_in.routing_type == "walking"
                else VALID_BICYCLE_CLASSES
            )
        else:
            valid_segment_classes = VALID_CAR_CLASSES

        # Compute buffer distance for identifying relevant H3_6 cells
        if type(obj_in.travel_cost) == CatchmentAreaTravelTimeCostActiveMobility:
            buffer_dist = obj_in.travel_cost.max_traveltime * (
                (obj_in.travel_cost.speed * 1000) / 60
            )
        elif type(obj_in.travel_cost) == CatchmentAreaTravelTimeCostMotorizedMobility:
            buffer_dist = obj_in.travel_cost.max_traveltime * (
                (settings.CATCHMENT_AREA_CAR_BUFFER_DEFAULT_SPEED * 1000) / 60
            )
        else:
            buffer_dist = obj_in.travel_cost.max_distance

        # Identify H3_3 & H3_6 cells relevant to this catchment area calculation
        h3_3_cells = set()
        h3_6_cells = set()

        sql_get_relevant_cells = f"""
            WITH point AS (
                SELECT geom FROM temporal.\"{input_table}\" LIMIT {num_points}
            ),
            buffer AS (
                SELECT ST_Buffer(point.geom::geography, {buffer_dist})::geometry AS geom
                FROM point
            ),
            cells AS (
                SELECT h3_index
                FROM buffer,
                LATERAL basic.fill_polygon_h3_6(buffer.geom)
            )
            SELECT basic.to_short_h3_3(h3_cell_to_parent(h3_index, 3)::bigint) AS h3_3, ARRAY_AGG(basic.to_short_h3_6(h3_index::bigint)) AS h3_6
            FROM cells
            GROUP BY h3_3;
        """
        self.db_cursor.execute(sql_get_relevant_cells)
        for h3_3_cell in self.db_cursor.fetchall():
            h3_3_cells.add(h3_3_cell[0])
            for h3_6_cell in h3_3_cell[1]:
                h3_6_cells.add(h3_6_cell)

        # Get relevant segments & connectors
        sub_network = pl.DataFrame()
        for h3_3 in h3_3_cells:
            sub_df = routing_network.get(h3_3)

            if sub_df is None:
                raise BufferExceedsNetworkError(
                    "Catchment area buffer exceeds available H3_3 network cells."
                )

            sub_df = sub_df.filter(
                pl.col("h3_6").is_in(h3_6_cells)
                & pl.col("class_").is_in(valid_segment_classes)
            )
            if sub_network.width > 0:
                sub_network.extend(sub_df)
            else:
                sub_network = sub_df

        # Create necessary artifical segments and add them to our sub network
        origin_point_connectors = []
        origin_point_cell_index = []
        origin_point_h3_3 = []
        segments_to_discard = []
        sql_get_artificial_segments = f"""
            SELECT
                point_id,
                old_id,
                id, length_m, length_3857, class_, impedance_slope,
                impedance_slope_reverse, impedance_surface,
                CAST(coordinates_3857 AS TEXT) AS coordinates_3857,
                maxspeed_forward, maxspeed_backward, source, target,
                h3_3, h3_6, point_cell_index, point_h3_3
            FROM basic.get_artificial_segments(
                {obj_in.street_network_edge_layer_project_id},
                '{input_table}',
                {num_points},
                '{",".join(valid_segment_classes)}',
                {origin_point_cell_resolution}
            );
        """
        self.db_cursor.execute(sql_get_artificial_segments)
        result = self.db_cursor.fetchall()
        for a_seg in result:
            if a_seg[0] is not None:
                origin_point_connectors.append(a_seg[12])
                origin_point_cell_index.append(a_seg[16])
                origin_point_h3_3.append(a_seg[17])
                segments_to_discard.append(a_seg[1])

            new_df = pl.DataFrame(
                [
                    {
                        "id": a_seg[2],
                        "length_m": a_seg[3],
                        "length_3857": a_seg[4],
                        "class_": a_seg[5],
                        "impedance_slope": a_seg[6],
                        "impedance_slope_reverse": a_seg[7],
                        "impedance_surface": a_seg[8],
                        "coordinates_3857": a_seg[9],
                        "maxspeed_forward": a_seg[10],
                        "maxspeed_backward": a_seg[11],
                        "source": a_seg[12],
                        "target": a_seg[13],
                        "h3_3": a_seg[14],
                        "h3_6": a_seg[15],
                    }
                ],
                schema_overrides=SEGMENT_DATA_SCHEMA,
            )
            new_df = new_df.with_columns(pl.col("coordinates_3857").str.json_extract())
            sub_network.extend(new_df)

        if len(origin_point_connectors) == 0:
            raise DisconnectedOriginError(
                "Starting point(s) are disconnected from the street network."
            )

        # Remove segments which are now replaced by artificial segments
        sub_network = sub_network.filter(~pl.col("id").is_in(segments_to_discard))

        # TODO: We need to read the scenario network dynamically from DB if a scenario is selected.

        # Replace all NULL values in the impedance columns with 0
        sub_network = sub_network.with_columns(pl.col("impedance_surface").fill_null(0))

        # Compute cost for each segment
        if type(obj_in.travel_cost) in [
            CatchmentAreaTravelTimeCostActiveMobility,
            CatchmentAreaTravelTimeCostMotorizedMobility,
        ]:
            # If producing a travel time cost based catchment area, compute segment cost accordingly
            sub_network = self.compute_segment_cost(
                sub_network=sub_network,
                mode=obj_in.routing_type,
                speed=(
                    obj_in.travel_cost.speed / 3.6
                    if type(obj_in.travel_cost)
                    == CatchmentAreaTravelTimeCostActiveMobility
                    else None
                ),
            )
        else:
            # TODO: Refactor this into a separate function as slope / surface impedance should be included
            # for bicycle / pedelec routing and one-ways should be avoided for car routing
            # If producing a distance cost based catchment area, use the segment length as cost
            sub_network = sub_network.with_columns(
                pl.col("length_m").alias("cost"),
                pl.col("length_m").alias("reverse_cost"),
            )

        # Select columns required for computing catchment area and convert to dictionary of numpy arrays
        sub_network = {
            "id": sub_network.get_column("id").to_numpy().copy(),
            "source": sub_network.get_column("source").to_numpy().copy(),
            "target": sub_network.get_column("target").to_numpy().copy(),
            "cost": sub_network.get_column("cost").to_numpy().copy(),
            "reverse_cost": sub_network.get_column("reverse_cost").to_numpy().copy(),
            "length": sub_network.get_column("length_3857").to_numpy().copy(),
            "geom": sub_network.get_column("coordinates_3857").to_numpy().copy(),
        }

        return (
            sub_network,
            origin_point_connectors,
            origin_point_cell_index,
            origin_point_h3_3,
        )

    def create_input_table(self, obj_in: ICatchmentAreaActiveMobility):
        """Create the input table for the catchment area calculation."""

        # Generate random table name
        table_name = str(uuid.uuid4()).replace("-", "_")

        # Create temporary table for storing catchment area starting points
        self.db_cursor.execute(
            f"""
                CREATE TABLE temporal.\"{table_name}\" (
                    id serial PRIMARY KEY,
                    geom geometry(Point, 4326)
                );
            """
        )

        # Insert catchment area starting points into the temporary table
        insert_string = ""
        for i in range(len(obj_in.starting_points.latitude)):
            latitude = obj_in.starting_points.latitude[i]
            longitude = obj_in.starting_points.longitude[i]
            insert_string += (
                f"(ST_SetSRID(ST_MakePoint({longitude}, {latitude}), 4326)),"
            )
        self.db_cursor.execute(
            f"""
                INSERT INTO temporal.\"{table_name}\" (geom)
                VALUES {insert_string.rstrip(",")};
            """
        )

        self.db_connection.commit()

        return table_name, len(obj_in.starting_points.latitude)

    def delete_input_table(self, table_name: str):
        """Delete the input table after reading the relevant sub-network."""

        self.db_cursor.execute(f'DROP TABLE temporal."{table_name}";')
        self.db_connection.commit()

    def compute_segment_cost(self, sub_network, mode, speed):
        """Compute the cost of a segment based on the mode, speed, impedance, etc."""

        if mode == CatchmentAreaRoutingTypeActiveMobility.walking:
            return sub_network.with_columns(
                (pl.col("length_m") / speed).alias("cost"),
                (pl.col("length_m") / speed).alias("reverse_cost"),
            )
        elif mode == CatchmentAreaRoutingTypeActiveMobility.bicycle:
            return sub_network.with_columns(
                pl.when(
                    (pl.col("class_") != "pedestrian")
                    & (pl.col("class_") != "crosswalk")
                )
                .then(
                    (
                        pl.col("length_m")
                        * (1 + pl.col("impedance_slope") + pl.col("impedance_surface"))
                    )
                    / speed
                )
                .otherwise(
                    pl.col("length_m") / speed
                )  # This calculation is invoked when the segment class requires cyclists to walk their bicycle
                .alias("cost"),
                pl.when(
                    (pl.col("class_") != "pedestrian")
                    & (pl.col("class_") != "crosswalk")
                )
                .then(
                    (
                        pl.col("length_m")
                        * (
                            1
                            + pl.col("impedance_slope_reverse")
                            + pl.col("impedance_surface")
                        )
                    )
                    / speed
                )
                .otherwise(
                    pl.col("length_m") / speed
                )  # This calculation is invoked when the segment class requires cyclists to walk their bicycle
                .alias("reverse_cost"),
            )
        elif mode == CatchmentAreaRoutingTypeActiveMobility.pedelec:
            return sub_network.with_columns(
                pl.when(
                    (pl.col("class_") != "pedestrian")
                    & (pl.col("class_") != "crosswalk")
                )
                .then((pl.col("length_m") * (1 + pl.col("impedance_surface"))) / speed)
                .otherwise(
                    pl.col("length_m") / speed
                )  # This calculation is invoked when the segment class requires cyclists to walk their pedelec
                .alias("cost"),
                pl.when(
                    (pl.col("class_") != "pedestrian")
                    & (pl.col("class_") != "crosswalk")
                )
                .then((pl.col("length_m") * (1 + pl.col("impedance_surface"))) / speed)
                .otherwise(
                    pl.col("length_m") / speed
                )  # This calculation is invoked when the segment class requires cyclists to walk their pedelec
                .alias("reverse_cost"),
            )
        elif mode == CatchmentAreaRoutingTypeCar.car:
            return sub_network.with_columns(
                (pl.col("length_m") / ((pl.col("maxspeed_forward") * 0.7) / 3.6)).alias(
                    "cost"
                ),
                pl.when(pl.col("maxspeed_backward") is not None)
                .then(pl.col("length_m") / ((pl.col("maxspeed_backward") * 0.7) / 3.6))
                .otherwise(
                    99999
                )  # This is a one-way segment, so assign a very high cost to the reverse direction
                .alias("reverse_cost"),
            )
        else:
            return None
