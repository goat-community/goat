from src.db.migration.db_migration_base import DBMigrationBase
from src.resources.enums import MigrationTables
from src.utils import print_info, print_warning, print_hashtags
from src.db.session import legacy_engine
from sqlalchemy import text


#TODO: Finish this
#TODO: Add logic for the other tables
class DBMigration(DBMigrationBase):

    def __init__(self, legacy_engine, study_area_ids: list[int]):
        """Migration class.

        Args:
            legacy_engine (_type_): Sync SQLAlchemy engine.
            study_area_ids (list[int]): List of study area ids.
        """
        super().__init__(legacy_engine=legacy_engine)
        self.study_area_ids = study_area_ids


    def check_table_schema_matches(self, table_name: MigrationTables):
        """Check if the schema of the old table matches the schema of the foreign table.

        Args:
            table_name (str): Table name.

        Raises:
            Exception: If the schema of the old table does not match the schema of the foreign table.
        """
        stmt = text(
            f"""
                SELECT column_name, udt_name
                FROM {self.information_schema}.columns
                WHERE table_schema = '{self.schema}'
                AND table_name   = '{table_name}'
                EXCEPT
                SELECT column_name, udt_name
                FROM {self.information_schema_bridge}.columns
                WHERE table_schema = '{self.schema_foreign}'
                AND table_name   = '{table_name}'
            """
        )
        result = self.legacy_engine.execute(stmt)

        # Check if result is empty if not the schema is not the same and the migration should be aborted.
        if result.rowcount > 0:
            raise Exception(
                f"Schema of table {table_name} does not match the schema of the foreign table."
            )
        else:
            print_info(f"Schema of table {table_name} matches the schema of the foreign table.")

    def prepare_migration_table(self, table_name: MigrationTables, column_names: list[str], column_types: list[str], index_columns: list[str]):
        """Prepare the empty migration table for the migration.

        Args:
            table_name (MigrationTables): Table name.
            column_names (list[str]): Column names.
            column_types (list[str]): Column types.
            index_columns (list[str]): Index columns. It will create the default PostgreSQL index for the specified columns together.
        """

        # Create columns for migration table.
        columns_type = ""
        for column_name, column_type in zip(column_names, column_types):
            columns_type += f"{column_name} {column_type}, "
        columns_type = columns_type[:-2]

        sql_base = f"""
            DROP TABLE IF EXISTS {self.schema_bridge}.{table_name}_to_migrate;
            CREATE TABLE {self.schema_bridge}.{table_name}_to_migrate (
                {columns_type},
                action text CHECK (action in ('insert', 'update', 'delete'))
            );"""
        self.legacy_engine.execute(text(sql_base))

        # Create index for migration table.
        index_columns = ", ".join(index_columns)
        sql_index = f"""
            CREATE INDEX {table_name}_index ON {self.schema_bridge}.{table_name}_to_migrate ({index_columns});
        """
        self.legacy_engine.execute(text(sql_index))

    def get_column_from_table(self, table_name: MigrationTables) -> list[list[str]]:

        """Gets the column names and their types from the table.

        Args:
            table_name (MigrationTables): Table name.

        Returns:
            list[list[str]]: Nested list with column names and their types.
        """

        # Get columns of table and their types.
        get_columns = text(
            f"""
                SELECT column_name, udt_name
                FROM {self.information_schema}.columns
                WHERE table_schema = '{self.schema}'
                AND table_name = '{table_name}'
            """
        )
        columns = self.legacy_engine.execute(get_columns)
        columns = [list(column) for column in columns.fetchall()]
        return columns

    def create_on_condition(self, columns_to_match: list[str]) -> str:
        """Create the join 'and' condition based on the columns that should be matched.

        Args:
            columns_to_match (list[str]): Define the column names that are used to match the rows via 'and' condition.

        Returns:
            str: SQL query part.
        """

        sql_on_condition = ""
        for column in columns_to_match:
            sql_on_condition += f"old_data.{column} = new_data.{column} AND "
        sql_on_condition = sql_on_condition[:-5]
        return sql_on_condition

    def select_relevant_rows_query(self, table_name: MigrationTables, study_area_id: int) -> str:
        """Prepares a query to select the relevant rows from the table using study area filter and table specific logic.

        Args:
            table_name (MigrationTables): Table name.

        Raises:
            Exception: Raises expection when a table name is passed that is not supported for migration.

        Returns:
            str: SQL query.
        """

        # Custom logic for each supported table.
        if table_name == MigrationTables.study_area.value:
            sql_select_query = f"""
                SELECT *
                FROM {self.schema_bridge}.{table_name}
                WHERE id = {study_area_id}
            """
        elif table_name == MigrationTables.sub_study_area.value:
            sql_select_query = f"""
                SELECT *
                FROM {self.schema_bridge}.{table_name}
                WHERE study_area_id = {study_area_id}
            """
        elif table_name == MigrationTables.poi.value:
            sql_select_query = f"""
                SELECT p.*
                FROM {self.schema_bridge}.{table_name} p, {self.schema_bridge}.study_area s
                WHERE s.id = {study_area_id}
                AND ST_Intersects(s.geom, p.geom)
            """
        else:
            raise Exception(f"Table {table_name} is not supported for migration.")

        return sql_select_query


    def prepare_rows_to_update(self, table_name: MigrationTables, columns_to_match: list[str], study_area_id: int, columns_to_exclude: list[str] = []):
        """Select the rows that have a match in the existing table and inserts them into the migration table.

        Args:
            table_name (MigrationTables): Table name.
            columns_to_match (list[str]): Define the column names that are used to match the rows via 'and' condition.
            columns_to_exclude (list[str], optional): Specify the columns that should be excluded for the update. Defaults to [].
        """

        # Get columns of table and their types.
        columns = self.get_column_from_table(table_name)

        # Create the On condition for the SQL join.
        sql_on_condition = self.create_on_condition(columns_to_match)

        # Create the Where condition for the SQL join.
        # TODO: Add different logic for geometry type and work on performance. Hausdorff distance?
        sql_where_condition = ""
        sql_select_condition = ""
        column_names = []
        for column in columns:
            column_name, data_type = column

            # Check if column is in the list of columns to exclude then avoid the check and set check type to be excluded.
            if column_name in columns_to_exclude:
                sql_select_condition += f"new_data.{column_name}, 'excluded' AS {column_name}_check,"

            elif column_name == "id":
                sql_select_condition += f"old_data.{column_name}, 'excluded' AS {column_name}_check,"

            # Check if column is a geometry column and use ST_ASTEXT to compare the geometry.
            elif data_type == "geometry":
                sql_select_condition += f"""
                    new_data.{column_name}, CASE WHEN ST_ASTEXT(old_data.{column_name}) <> ST_ASTEXT(new_data.{column_name})
                    THEN 'changed' ELSE 'unchanged'
                    END AS {column_name}_check,
                """
                sql_where_condition += f"ST_ASTEXT(old_data.{column_name}) <> ST_ASTEXT(new_data.{column_name}) OR "
            # If column is not a geometry column then use the <> operator to compare the values.
            else:
                sql_select_condition += f"""
                    new_data.{column_name}, CASE WHEN old_data.{column_name} <> new_data.{column_name}
                    THEN 'changed' ELSE 'unchanged'
                    END AS {column_name}_check,
                """
                sql_where_condition += f"old_data.{column_name} <> new_data.{column_name} OR "
            column_names.append(column_name)
            column_names.append(f"{column_name}_check")

        sql_where_condition = sql_where_condition[:-4]

        # Create the empty migration table.
        data_types = []
        for column in columns:
            data_types.append(column[1])
            data_types.append("text")
        self.prepare_migration_table(table_name, column_names, data_types, columns_to_match)

        # Create the query to select the relevant rows to be checked for migration.
        select_relevant_rows = self.select_relevant_rows_query(table_name, study_area_id)

        # Merge query parts.
        stmt = text(
            f"""
                INSERT INTO {self.schema_bridge}.{table_name}_to_migrate ({', '.join(column_names)}, action)
                SELECT {sql_select_condition} 'update' as action
                FROM {self.schema}.{table_name} old_data
                LEFT JOIN ({select_relevant_rows}) new_data
                ON {sql_on_condition}
                AND ({sql_where_condition})
                WHERE new_data.{columns_to_match[0]} IS NOT NULL;
            """
        )
        self.legacy_engine.execute(stmt)

    def prepare_rows_to_insert(self, table_name: MigrationTables, columns_to_match: list[str], study_area_id: int):
        """Select the new rows and inserts them into the migration table.

        Args:
            table_name (MigrationTables): Table name.
            columns_to_match (list[str]): Define the column names that are used to match the rows via 'and' condition.
        """
        # Get columns of table and their types.
        columns = self.get_column_from_table(table_name)

        # Get on condition for the SQL join.
        sql_on_condition = self.create_on_condition(columns_to_match)

        # Create the query to select the relevant rows to be checked for migration.
        select_relevant_rows = self.select_relevant_rows_query(table_name, study_area_id)

        # Insert statement for new data.
        stmt = text(
            f"""
                INSERT INTO {self.schema_bridge}.{table_name}_to_migrate ({', '.join([column[0] for column in columns])}, action)
                SELECT new_data.*, 'insert' as action
                FROM  ({select_relevant_rows}) new_data
                LEFT JOIN {self.schema}.{table_name} old_data
                ON {sql_on_condition}
                WHERE old_data.{columns_to_match[0]} IS NULL;
            """
        )
        self.legacy_engine.execute(stmt)


    def perform_migration(self, table_name: MigrationTables, columns_to_match: list[str], columns_to_exclude: list[str] = []):
        """Perform the migration for the given table using the provided conditions.

        Args:
            table_name (MigrationTables): Table name.
            columns_to_match (list[str]): Define the column names that are used to match the rows via 'and' condition.
            columns_to_exclude (list[str], optional): Specify the columns that should be excluded for the update. Defaults to [].

        Raises:
            Exception: Raises expection when the user does answer with n.
            Exception: Raises expection when the user does answer with n or y.
        """

        print_info(f"Starting migration for table {table_name}...")

        # Check if table schema matches the schema in the migration table.
        self.check_table_schema_matches(table_name)
        # Prepare rows to be updated and inserted.

        for study_area_id in self.study_area_ids:
            print_info(f"Starting migration for study area {study_area_id}...")
            self.prepare_rows_to_update(table_name, columns_to_match, study_area_id=study_area_id, columns_to_exclude=columns_to_exclude)
            self.prepare_rows_to_insert(table_name, columns_to_match=columns_to_match, study_area_id=study_area_id)

        # Ask user if migration table has been checked.
        print_warning("Have you checked the migration table? (y/n)")
        answer = input()
        if answer == "n":
            raise Exception("Please check the migration table before performing the migration.")
        elif answer == "y":
            print_info("Starting migration...")
        else:
            raise Exception("Please answer with y or n.")


        # Get columns of table and their types.
        columns = self.get_column_from_table(table_name)

        # Insert new data from migration table
        stmt = text(
            f"""
                INSERT INTO {self.schema}.{table_name} ({', '.join([column[0] for column in columns])})
                SELECT {', '.join([column[0] for column in columns])}
                FROM {self.schema_bridge}.{table_name}_to_migrate
                WHERE action = 'insert';
            """
        )
        self.legacy_engine.execute(stmt)

        # Update existing data from migration table
        # Build the SET part of the SQL statement. Make sure to only update the columns that have changed.
        update_column_sql = ""
        for column in columns:
            update_column_sql += f"""{column[0]} = CASE WHEN migration_table.{column[0]}_check IN ('unchanged', 'excluded') THEN {self.schema}.{table_name}.{column[0]} ELSE migration_table.{column[0]} END,"""
        update_column_sql = update_column_sql[:-1]

        # Combine the SQL statement parts.
        stmt = text(
            f"""
                UPDATE {self.schema}.{table_name}
                SET {update_column_sql}
                FROM {self.schema_bridge}.{table_name}_to_migrate migration_table
                WHERE {self.schema}.{table_name}.id = migration_table.id
                AND migration_table.action = 'update';
            """
        )
        self.legacy_engine.execute(stmt)

def main():

    print_hashtags()
    print_info("Starting migration...")
    print_hashtags()


    migration = DBMigration(legacy_engine=legacy_engine, study_area_ids=[5334,5358,5370,8315,8316,9161,9163,9173,9174,9175,9177,9178,9179,9184,9186,9188,9261,9262,9263,9274,9361,9362,9363,9461,9462,9463,9464,9474,9561,9562,9563,9564,9565,9572,9573,9574,9576,9661,9662,9663,9761,9762,9763,9764,14626,83110000,91620000])
    migration.initialize()

    # Perform migration for Study Area and Sub Study Area.
    # migration.perform_migration("study_area", columns_to_match=["id"], columns_to_exclude=["setting"])
    # migration.perform_migration("sub_study_area", columns_to_match=["id"])
    migration.perform_migration("poi", columns_to_match=["uid"])


    print_hashtags()
    print_info("Migration finished.")
    print_hashtags()

if __name__ == "__main__":
    main()
