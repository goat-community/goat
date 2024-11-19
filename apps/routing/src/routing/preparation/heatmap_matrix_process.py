import math

import numpy as np
from routing.core.config import settings
from routing.core.isochrone import (
    construct_adjacency_list_,
    dijkstra_h3,
    network_to_grid_h3,
    prepare_network_isochrone,
)
from routing.crud.crud_catchment_area_sync import CRUDCatchmentArea, FetchRoutingNetwork
from routing.schemas.catchment_area import (
    CatchmentAreaRoutingTypeActiveMobility,
    CatchmentAreaRoutingTypeCar,
    CatchmentAreaStartingPoints,
    CatchmentAreaType,
    ICatchmentAreaActiveMobility,
    ICatchmentAreaCar,
)
from routing.schemas.error import BufferExceedsNetworkError, DisconnectedOriginError
from routing.schemas.heatmap import MATRIX_RESOLUTION_CONFIG, ROUTING_COST_CONFIG
from tqdm import tqdm


class HeatmapMatrixProcess:
    def __init__(
        self,
        thread_id: int,
        chunk: list,
        routing_type: (
            CatchmentAreaRoutingTypeActiveMobility | CatchmentAreaRoutingTypeCar
        ),
    ):
        self.thread_id = thread_id
        self.routing_network = None
        self.chunk = chunk
        self.routing_type = routing_type
        self.INSERT_BATCH_SIZE = 800
        self.matrix_resolution = MATRIX_RESOLUTION_CONFIG[routing_type.value]

        max_traveltime = ROUTING_COST_CONFIG[routing_type.value].max_traveltime
        if type(routing_type) == CatchmentAreaRoutingTypeActiveMobility:
            self.buffer_distance = max_traveltime * (
                (ROUTING_COST_CONFIG[routing_type.value].speed * 1000) / 60
            )
        else:
            self.buffer_distance = max_traveltime * (
                (settings.CATCHMENT_AREA_CAR_BUFFER_DEFAULT_SPEED * 1000) / 60
            )

    def generate_multi_catchment_area_request(self, db_cursor, h3_6_index: str):
        """Produce a multi-catchment area request for a given H3_6 index and routing type."""

        # Get the centroid coordinates for all child cells of the supplied H3_6 parent cell
        sql_get_centroid = f"""
            WITH centroid AS (
                SELECT ST_SetSRID(h3_cell_to_lat_lng(h3_index)::geometry, 4326) AS geom
                FROM h3_cell_to_children('{h3_6_index}'::h3index, {self.matrix_resolution}) AS h3_index
            )
            SELECT ST_X(geom), ST_Y(geom)
            FROM centroid;
        """
        db_cursor.execute(sql_get_centroid)
        result = db_cursor.fetchall()

        # Group centroid coordinates into latitude and longitude lists
        origin_lat = []
        origin_lng = []
        for centroid in result:
            origin_lat.append(centroid[1])
            origin_lng.append(centroid[0])

        # Produce final ICatchmentAreaActiveMobility object (request for CRUDCatchmentArea)
        return (
            ICatchmentAreaActiveMobility(
                starting_points=CatchmentAreaStartingPoints(
                    latitude=origin_lat,
                    longitude=origin_lng,
                ),
                routing_type=self.routing_type,
                travel_cost=ROUTING_COST_CONFIG[self.routing_type.value],
                scenario_id=None,
                catchment_area_type=CatchmentAreaType.polygon,
                polygon_difference=True,
                result_table="",
                layer_id=None,
            )
            if type(self.routing_type) == CatchmentAreaRoutingTypeActiveMobility
            else ICatchmentAreaCar(
                starting_points=CatchmentAreaStartingPoints(
                    latitude=origin_lat,
                    longitude=origin_lng,
                ),
                routing_type=self.routing_type,
                travel_cost=ROUTING_COST_CONFIG[self.routing_type.value],
                scenario_id=None,
                catchment_area_type=CatchmentAreaType.polygon,
                polygon_difference=True,
                result_table="",
                layer_id=None,
            )
        )

    def get_cell_grid(self, db_cursor, h3_6_index: str):
        sql_get_relevant_cells = f"""
            WITH cells AS (
                SELECT h3_grid_disk(origin_h3_index, radius.value) AS h3_index
                FROM h3_cell_to_center_child('{h3_6_index}', {self.matrix_resolution}) AS origin_h3_index,
                LATERAL (SELECT (h3_get_hexagon_edge_length_avg(6, 'm') + {self.buffer_distance})::int AS dist) AS buffer,
                LATERAL (SELECT (buffer.dist / (h3_get_hexagon_edge_length_avg({self.matrix_resolution}, 'm') * 1.5)::int) AS value) AS radius
            )
            SELECT h3_index, ST_X(centroid), ST_Y(centroid)
            FROM cells,
            LATERAL (
                SELECT ST_Transform(ST_SetSRID(point::geometry, 4326), 3857) AS centroid
                FROM h3_cell_to_lat_lng(h3_index) AS point
            ) sub;
        """
        db_cursor.execute(sql_get_relevant_cells)
        result = db_cursor.fetchall()

        h3_index = []
        x_centroids = np.empty(len(result))
        y_centroids = np.empty(len(result))
        for i in range(len(result)):
            h3_index.append(result[i][0])
            x_centroids[i] = result[i][1]
            y_centroids[i] = result[i][2]

        return h3_index, x_centroids, y_centroids

    def add_to_insert_string(self, orig_id, dest_id, costs, orig_h3_3):
        cost_map = {}
        for i in range(len(dest_id)):
            if math.isnan(costs[i]) or int(costs[i]) == 0:
                continue
            cost = int(costs[i])
            if cost not in cost_map:
                cost_map[cost] = []
            cost_map[cost].append(dest_id[i])

        if 1 not in cost_map:
            cost_map[1] = [orig_id]
        elif orig_id not in cost_map[1]:
            cost_map[1].append(orig_id)

        for traveltime in cost_map:
            self.insert_string += f"""(
                '{orig_id}'::h3index,
                ARRAY{cost_map[traveltime]}::h3index[],
                {traveltime},
                {orig_h3_3}
            ),"""
            self.num_rows_queued += 1

    def write_to_db(self, db_cursor, db_connection):
        db_cursor.execute(
            f"""
                INSERT INTO basic.traveltime_matrix_{self.routing_type.value} (orig_id, dest_id, traveltime, h3_3)
                VALUES {self.insert_string.rstrip(",")};
            """
        )
        db_connection.commit()

    def run(self):
        db_connection = psycopg2.connect(settings.POSTGRES_DATABASE_URI)
        db_cursor = db_connection.cursor()

        crud_catchment_area = CRUDCatchmentArea(db_connection, db_cursor)

        # Fetch routing network (processed segments) and load into memory
        if self.routing_network is None:
            self.routing_network = FetchRoutingNetwork(db_cursor).fetch()

        for index in tqdm(
            range(len(self.chunk)), desc=f"Thread {self.thread_id}", unit=" cell"
        ):
            h3_6_index = self.chunk[index]

            catchment_area_request = self.generate_multi_catchment_area_request(
                db_cursor=db_cursor,
                h3_6_index=h3_6_index,
            )

            sub_routing_network = None
            origin_connector_ids = None
            origin_point_cell_index = None
            origin_point_h3_3 = None
            try:
                # Create input table for catchment area origin points
                input_table, num_points = crud_catchment_area.create_input_table(
                    catchment_area_request
                )

                # Read & process routing network to extract relevant sub-network
                (
                    sub_routing_network,
                    origin_connector_ids,
                    origin_point_cell_index,
                    origin_point_h3_3,
                ) = crud_catchment_area.read_network(
                    self.routing_network,
                    catchment_area_request,
                    input_table,
                    num_points,
                    self.matrix_resolution,
                )

                # Delete input table for catchment area origin points
                crud_catchment_area.delete_input_table(input_table)
            except Exception as e:
                db_connection.rollback()
                if isinstance(e, DisconnectedOriginError):
                    print(
                        f"Thread {self.thread_id}: Skipping {h3_6_index} due to disconnected origin. Starting points: [temporal.{input_table}]"
                    )
                    continue
                elif isinstance(e, BufferExceedsNetworkError):
                    print(
                        f"Thread {self.thread_id}: Skipping {h3_6_index} due to buffer exceeding network. Starting points: [temporal.{input_table}]"
                    )
                    continue
                else:
                    print(e)
                    print(
                        f"Thread {self.thread_id}: Error processing {h3_6_index}, exiting."
                    )
                    break

            # Compute heatmap grid utilizing processed sub-network
            if type(catchment_area_request) == ICatchmentAreaActiveMobility:
                speed = catchment_area_request.travel_cost.speed / 3.6
            else:
                speed = None

            if type(catchment_area_request) == ICatchmentAreaActiveMobility:
                zoom = 12
            else:
                zoom = 10  # Use lower resolution grid for car catchment areas
            try:
                (
                    edges_source,
                    edges_target,
                    edges_cost,
                    edges_reverse_cost,
                    edges_length,
                    unordered_map,
                    node_coords,
                    extent,
                    geom_address,
                    geom_array,
                ) = prepare_network_isochrone(edge_network_input=sub_routing_network)

                adj_list = construct_adjacency_list_(
                    len(unordered_map),
                    edges_source,
                    edges_target,
                    edges_cost,
                    edges_reverse_cost,
                )

                start_vertices_ids = np.array(
                    [unordered_map[v] for v in origin_connector_ids]
                )
                distances_list = dijkstra_h3(
                    start_vertices_ids,
                    adj_list,
                    catchment_area_request.travel_cost.max_traveltime,
                    False,
                )

                (
                    h3_index,
                    h3_centroid_x,
                    h3_centroid_y,
                ) = self.get_cell_grid(
                    db_cursor,
                    h3_6_index,
                )

                self.insert_string = ""
                self.num_rows_queued = 0
                for i in range(len(origin_point_cell_index)):
                    mapped_cost = network_to_grid_h3(
                        extent=extent,
                        zoom=zoom,
                        edges_source=edges_source,
                        edges_target=edges_target,
                        edges_length=edges_length,
                        geom_address=geom_address,
                        geom_array=geom_array,
                        distances=distances_list[i],
                        node_coords=node_coords,
                        speed=speed,
                        max_traveltime=catchment_area_request.travel_cost.max_traveltime,
                        centroid_x=h3_centroid_x,
                        centroid_y=h3_centroid_y,
                        is_distance_based=False,
                    )

                    self.add_to_insert_string(
                        orig_id=origin_point_cell_index[i],
                        dest_id=h3_index,
                        costs=mapped_cost,
                        orig_h3_3=origin_point_h3_3[i],
                    )

                    if (
                        self.num_rows_queued >= self.INSERT_BATCH_SIZE
                        or i == len(origin_point_cell_index) - 1
                    ):
                        self.write_to_db(
                            db_cursor,
                            db_connection,
                        )
                        self.insert_string = ""
                        self.num_rows_queued = 0

            except Exception as e:
                db_connection.rollback()
                print(e)
                print(
                    f"Thread {self.thread_id}: Error processing {h3_6_index}, exiting."
                )
                break

        db_connection.close()

        print(f"Thread {self.thread_id} finished.")
