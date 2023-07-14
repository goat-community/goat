#! /usr/bin/env python
import argparse
import sys
import textwrap
from pathlib import Path

from alembic_utils.pg_function import PGFunction
from psycopg2.errors import UndefinedFunction
from sqlalchemy import text

from src.core.config import settings
from src.db.session import legacy_engine
from src.db.sql.utils import report, sorted_path_by_dependency
from src.utils import print_hashtags, print_info


def sql_function_entities():
    sql_function_entities = []
    function_paths = Path(str(Path().resolve()) + "/src/db/sql/functions").rglob("*.sql")
    function_paths = sorted_path_by_dependency(function_paths)
    for p in function_paths:
        pg_function_entitity = PGFunction.from_sql(p.read_text())
        pg_function_entitity.schema = settings.POSTGRES_FUNCTIONS_SCHEMA
        sql_function_entities.append(pg_function_entitity)
    return sql_function_entities


def sql_trigger_entities():
    trigger_paths = Path(str(Path().resolve()) + "/src/db/sql/triggers").glob("*.sql")
    trigger_paths = sorted_path_by_dependency(trigger_paths)
    sql_trigger_entities = []
    for p in trigger_paths:
        pg_trigger_entity = PGFunction.from_sql(p.read_text())
        pg_trigger_entity.schema = settings.POSTGRES_FUNCTIONS_SCHEMA
        sql_trigger_entities.append(pg_trigger_entity)
    return sql_trigger_entities


def drop_functions():
    # Drop all functions in the schema 'basic'
    stmt_list_functions = text(
        "SELECT proname FROM pg_proc WHERE pronamespace = 'basic'::regnamespace"
    )
    functions = legacy_engine.execute(stmt_list_functions).fetchall()
    functions = [f[0] for f in functions]
    for function in functions:
        # Skip trigger functions as they should be dropped by drop_triggers()
        if "trigger" in function:
            continue
        print_info(f"Dropping {function}()")
        statement = f"DROP FUNCTION IF EXISTS basic.{function} CASCADE;"
        try:
            legacy_engine.execute(text(statement))
        except UndefinedFunction as e:
            print(e)
    print_info(f"{len(functions)} functions dropped!")


def add_functions():
    sql_function_entities_ = sql_function_entities()
    for function in sql_function_entities_:
        for statement in function.to_sql_statement_create_or_replace():
            legacy_engine.execute(text(statement.text))
            function_name = function.literal_signature.split("(")[0][1:-1]
            print_info(f"Adding {function_name}()")
    print_info(f"{len(sql_function_entities_)} functions added!")


def drop_triggers():
    sql_trigger_entities_ = sql_trigger_entities()
    sql_trigger_entities_.reverse()
    for trigger in sql_trigger_entities_:
        statement = trigger.to_sql_statement_drop(cascade=True)
        try:
            legacy_engine.execute(text(statement.text))
        except UndefinedFunction as e:
            print(e)
        trigger_name = trigger.literal_signature.split("(")[0][1:-1]
        print_info(f"Dropping {trigger_name}()")

    print_info(f"{len(sql_trigger_entities_)} triggers dropped!")


def add_triggers():
    sql_trigger_entities_ = sql_trigger_entities()
    for trigger in sql_trigger_entities_:
        for statement in trigger.to_sql_statement_create_or_replace():
            legacy_engine.execute(text(statement.text))
            trigger_name = trigger.literal_signature.split("(")[0][1:-1]
            print_info(f"Adding {trigger_name}()")
    print_info(f"{len(sql_trigger_entities_)} triggers added!")


def update_functions():
    # It will drop all functions and add them again
    drop_functions()
    print_hashtags()
    add_functions()


def update_triggers():
    # It will drop all triggers and add them again
    drop_triggers()
    print_hashtags()
    add_triggers()


def run(args):
    action = args.action
    material = args.material
    if action == "report":
        report()
    else:
        print_hashtags()
        print_info(f"{action.title()} {material}...")
        print_hashtags()
        # Execute the function with the name of the action and material
        globals()[f"{action}_{material}"]()

        print_hashtags()
        print_info(f"{action.title()} {material} complete!")
        print_hashtags()


def main():
    parser = argparse.ArgumentParser(
        description="add and drop sql functions and triggers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            example usage:
                cd /app
                python src/db/sql/init_sql.py add -m functions
                python src/db/sql/init_sql.py drop -m triggers
                pyhton src/db/sql/init_sql.py update -m functions
                python src/db/sql/init_sql.py report

            Update will execute drop and add.
        """
        ),
    )
    parser.add_argument(
        "action",
        help="The action to do on database",
        choices=["add", "drop", "update", "report"],
        type=str,
    )
    parser.add_argument(
        "--material",
        "-m",
        required="add" in sys.argv or "drop" in sys.argv or "add" in sys.argv,
        help="functions or triggers",
        choices=["functions", "triggers"],
        type=str,
    )
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
