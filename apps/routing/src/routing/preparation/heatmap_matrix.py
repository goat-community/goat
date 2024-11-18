from concurrent.futures import ProcessPoolExecutor

from routing.core.config import settings
from routing.preparation.heatmap_matrix_process import HeatmapMatrixProcess
from routing.schemas.catchment_area import CatchmentAreaRoutingTypeActiveMobility


class HeatmapMatrixPreparation:
    def __init__(self):
        # User configurable
        self.ROUTING_TYPE = CatchmentAreaRoutingTypeActiveMobility.walking
        self.NUM_THREADS = 20

    def get_cells_to_process(self, db_cursor):
        """Get list of parent H3_6 cells to process."""

        # Get cells from pre-defined table
        sql_get_cells_to_process = """
            SELECT h3_index
            FROM basic.geofence_heatmap_grid;
        """
        db_cursor.execute(sql_get_cells_to_process)
        result = db_cursor.fetchall()

        cells_to_process = []
        for h3_index in result:
            cells_to_process.append(h3_index[0])

        return cells_to_process

    def split_cells_into_chunks(self, cells_to_process):
        """Split cells to process into NUM_THREADS chunks."""

        # Calculate chunk size and remainder
        chunk_size = len(cells_to_process) // self.NUM_THREADS
        remainder = len(cells_to_process) % self.NUM_THREADS

        # Split cells to process into thunks of size chunk_size + remainder
        chunks = []
        start = 0
        for i in range(self.NUM_THREADS):
            end = start + chunk_size + (i < remainder)
            chunks.append([i, cells_to_process[start:end]])
            start = end

        return chunks

    def initialize_traveltime_matrix_table(self, db_cursor, db_connection):
        """Create table to store traveltime matrix."""

        # Drop table if it already exists
        sql_drop_table = f"""
            DROP TABLE IF EXISTS basic.traveltime_matrix_{self.ROUTING_TYPE.value};
        """
        db_cursor.execute(sql_drop_table)

        # Create table
        sql_create_table = f"""
            CREATE TABLE basic.traveltime_matrix_{self.ROUTING_TYPE.value} (
                orig_id h3index,
                dest_id h3index[],
                traveltime smallint,
                h3_3 int,
                PRIMARY KEY (orig_id, traveltime, h3_3)
            );
        """
        db_cursor.execute(sql_create_table)

        # Distribute table using CITUS
        sql_distribute_table = f"""
            SELECT create_distributed_table(
                'basic.traveltime_matrix_{self.ROUTING_TYPE.value}',
                'h3_3'
            );
        """
        db_cursor.execute(sql_distribute_table)

        # Commit changes
        db_connection.commit()

    def process_chunk(self, chunk):
        HeatmapMatrixProcess(
            thread_id=chunk[0],
            chunk=chunk[1],
            routing_type=self.ROUTING_TYPE,
        ).run()

    def run(self):
        # Connect to database
        db_connection = psycopg2.connect(settings.POSTGRES_DATABASE_URI)
        db_cursor = db_connection.cursor()

        # Get full list of parent H3_6 cells within our region of interest
        cells_to_process = self.get_cells_to_process(db_cursor)

        # Split cells to process into NUM_THREADS chunks to be processed in parallel
        chunks = self.split_cells_into_chunks(cells_to_process)

        # Initialize traveltime matrix table
        self.initialize_traveltime_matrix_table(db_cursor, db_connection)

        # Close database connection
        db_connection.close()

        try:
            # Spawn NUM_THREADS processes to compute matrix in parallel
            with ProcessPoolExecutor(max_workers=self.NUM_THREADS) as process_pool:
                process_pool.map(self.process_chunk, chunks)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    HeatmapMatrixPreparation().run()
