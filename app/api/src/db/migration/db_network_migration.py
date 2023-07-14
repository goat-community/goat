from src.db.migration.db_migration_base import DBMigrationBase
from src.utils import print_info
from src.db.session import legacy_engine
from sqlalchemy import text

# TODO: Check if this should be done based on study area logic
class DBNetworkMigration(DBMigrationBase):

    def __init__(self, legacy_engine):
        """Migration class.

        Args:
            legacy_engine (_type_): Sync SQLAlchemy engine.
        """
        super().__init__(legacy_engine=legacy_engine)

    def network_migration(self):

        # Get network size
        edge_max_id = self.legacy_engine.execute(text(f"SELECT max(id) FROM {self.schema_bridge}.edge")).fetchone()[0]
        node_max_id  = self.legacy_engine.execute(text(f"SELECT max(id) FROM {self.schema_bridge}.node")).fetchone()[0]

        # Truncate tables
        self.legacy_engine.execute(text(f"TRUNCATE TABLE {self.schema}.edge CASCADE"))
        #self.legacy_engine.execute(text(f"TRUNCATE TABLE {self.schema}.node CASCADE"))

        # Insert nodes in bulks of 100000
        for i in range(0, node_max_id, 100000):
            print_info(f"Inserting nodes {i} to {i+100000}")
            self.legacy_engine.execute(text(f"""
                INSERT INTO {self.schema}.node
                SELECT * FROM {self.schema_bridge}.node
                WHERE id >= {i} AND id < {i+100000}
            """))

        # Insert edges in bulks of 100000
        for i in range(0, edge_max_id, 100000):
            print_info(f"Inserting edges {i} to {i+100000}")
            self.legacy_engine.execute(text(f"""
                INSERT INTO {self.schema}.edge
                SELECT * FROM {self.schema_bridge}.edge
                WHERE id >= {i} AND id < {i+100000}
            """))


db_network_migration = DBNetworkMigration(legacy_engine=legacy_engine).network_migration()

