import time
from uuid import UUID

import polars as pl
from routing.core.config import settings
from routing.core.street_network.street_network_cache import StreetNetworkCache
from routing.schemas.catchment_area import CONNECTOR_DATA_SCHEMA, SEGMENT_DATA_SCHEMA
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class StreetNetworkUtil:
    def __init__(self, db_connection: AsyncSession) -> None:
        self.db_connection = db_connection

    async def _get_user_id(self, layer_id: UUID) -> UUID:
        """Get the user ID of the specified layer ID."""

        user_id: UUID | None = None

        try:
            # Get the user ID of the layer
            result = await self.db_connection.execute(
                text(
                    f"""SELECT user_id
                FROM {settings.CUSTOMER_SCHEMA}.layer
                WHERE id = '{layer_id}';"""
                )
            )
            row = result.fetchone()
            if row is None or len(row) == 0:
                raise ValueError(f"Layer ID {layer_id} not found.")
            user_id = UUID(str(row[0]))
        except Exception:
            raise ValueError(f"Could not fetch user ID for layer ID {layer_id}.")

        return user_id

    async def _get_street_network_tables(
        self,
        edge_layer_id: UUID,
        node_layer_id: UUID,
    ) -> tuple[str | None, str | None]:
        """Get table names and layer IDs of the edge and node tables."""

        edge_table = None
        node_table = None

        # Get edge table name if a layer ID is specified
        if edge_layer_id:
            try:
                # Get the edge layer ID and associated user ID
                user_id = await self._get_user_id(edge_layer_id)

                # Produce the edge table name
                edge_table = f"{settings.USER_DATA_SCHEMA}.street_network_line_{str(user_id).replace('-', '')}"
            except Exception:
                raise ValueError(
                    f"Could not fetch edge table name for layer ID {edge_layer_id}."
                )

        # Get node table name if a layer ID is specified
        if node_layer_id:
            try:
                # Get the node layer ID and associated user ID
                user_id = await self._get_user_id(node_layer_id)

                # Produce the node table name
                node_table = f"{settings.USER_DATA_SCHEMA}.street_network_point_{str(user_id).replace('-', '')}"
            except Exception:
                raise ValueError(
                    f"Could not fetch node table name for layer ID {node_layer_id}."
                )

        return edge_table, node_table

    async def _get_street_network_region_h3_3_cells(self, region_geofence_table: str) -> list[str]:
        """Get list of H3_3 cells covering the street network region."""

        h3_3_cells = []
        try:
            sql_fetch_h3_3_cells = f"""
                WITH region AS (
                    SELECT ST_Union(geom) AS geom FROM {region_geofence_table}
                )
                SELECT g.h3_short FROM region r,
                LATERAL basic.fill_polygon_h3_3(r.geom) g;
            """
            result = (
                await self.db_connection.execute(text(sql_fetch_h3_3_cells))
            ).fetchall()

            for h3_short in result:
                h3_3_cells.append(h3_short[0])
        except Exception:
            raise ValueError(
                f"Could not fetch H3_3 grid for street network geofence {settings.NETWORK_REGION_TABLE}."
            )

        return h3_3_cells

    async def fetch(
        self,
        edge_layer_id: UUID,
        node_layer_id: UUID,
        region_geofence_table: str,
    ) -> tuple[dict[str, pl.DataFrame], dict[str, pl.DataFrame]]:
        """Fetch street network from specified layer and load into Polars dataframes."""

        # Street network is stored as a dictionary of Polars dataframes, with the H3_3 index as the key
        street_network_edge = {}
        street_network_node = {}

        start_time = time.time()
        street_network_size: float = 0.0

        # Get H3_3 cells covering the street network region
        street_network_region_h3_3_cells = (
            await self._get_street_network_region_h3_3_cells(region_geofence_table)
        )

        # Get table names and layer IDs of the edge and node tables
        (
            street_network_edge_table,
            street_network_node_table,
        ) = await self._get_street_network_tables(edge_layer_id, node_layer_id)

        # Initialize cache
        street_network_cache = StreetNetworkCache()

        try:
            for h3_short in street_network_region_h3_3_cells:
                if edge_layer_id is not None:
                    if street_network_cache.edge_cache_exists(edge_layer_id, h3_short):
                        # Read edge data from cache
                        edge_df = street_network_cache.read_edge_cache(
                            edge_layer_id, h3_short
                        )
                    else:
                        if settings.ENVIRONMENT == "dev":
                            print(
                                f"Fetching street network edge data for H3_3 cell {h3_short}"
                            )

                        # Read edge data from database
                        edge_df = pl.read_database_uri(
                            query=f"""
                                SELECT
                                    edge_id AS id, length_m, length_3857, class_, impedance_slope, impedance_slope_reverse,
                                    impedance_surface, CAST(coordinates_3857 AS TEXT) AS coordinates_3857, maxspeed_forward,
                                    maxspeed_backward, source, target, h3_3, h3_6
                                FROM {street_network_edge_table}
                                WHERE h3_3 = {h3_short}
                                AND layer_id = '{str(edge_layer_id)}'
                            """,
                            uri=settings.POSTGRES_DATABASE_URI,
                            schema_overrides=SEGMENT_DATA_SCHEMA,
                        )
                        edge_df = edge_df.with_columns(
                            pl.col("coordinates_3857").str.json_decode()
                        )

                        # Write edge data into cache
                        street_network_cache.write_edge_cache(
                            edge_layer_id, h3_short, edge_df
                        )
                    # Update street network edge dictionary and memory usage
                    street_network_edge[h3_short] = edge_df
                    street_network_size += edge_df.estimated_size("gb")

                if node_layer_id is not None:
                    if street_network_cache.node_cache_exists(node_layer_id, h3_short):
                        # Read node data from cache
                        node_df = street_network_cache.read_node_cache(
                            node_layer_id, h3_short
                        )
                    else:
                        if settings.ENVIRONMENT == "dev":
                            print(
                                f"Fetching street network node data for H3_3 cell {h3_short}"
                            )

                        # Read node data from database
                        node_df = pl.read_database_uri(
                            query=f"""
                                SELECT node_id AS id, h3_3, h3_6
                                FROM {street_network_node_table}
                                WHERE h3_3 = {h3_short}
                                AND layer_id = '{str(node_layer_id)}'
                            """,
                            uri=settings.POSTGRES_DATABASE_URI,
                            schema_overrides=CONNECTOR_DATA_SCHEMA,
                        )

                        # Write node data into cache
                        street_network_cache.write_node_cache(
                            node_layer_id, h3_short, node_df
                        )

                    # Update street network node dictionary and memory usage
                    street_network_node[h3_short] = node_df
                    street_network_size += node_df.estimated_size("gb")
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch street network data from database, error: {e}"
            )

        # Raise error if a edge layer project ID is specified but no edge data is fetched
        if edge_layer_id is not None and len(street_network_edge) == 0:
            raise RuntimeError(
                f"Failed to fetch street network edge data for layer project ID {edge_layer_id}."
            )

        # Raise error if a node layer project ID is specified but no node data is fetched
        if node_layer_id is not None and len(street_network_node) == 0:
            raise RuntimeError(
                f"Failed to fetch street network node data for layer project ID {node_layer_id}."
            )

        end_time = time.time()

        print(f"Street network load time: {round((end_time - start_time) / 60, 1)} min")
        print(f"Street network in-memory size: {round(street_network_size, 1)} GB")

        return street_network_edge, street_network_node
