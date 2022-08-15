#! /usr/bin/env python
import argparse
import sys
import textwrap
from pathlib import Path

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from alembic_utils.pg_view import PGView
from sqlalchemy import text

from src.core.config import settings
from src.db.session import legacy_engine
from src.db.sql.utils import report, sorted_path_by_dependency


def sql_function_entities():
    sql_function_entities = []
    function_paths = Path(str(Path().resolve()) + "/src/db/sql/functions").rglob("*.sql")
    function_paths = sorted_path_by_dependency(function_paths)
    for p in function_paths:
        pg_function_entitity = PGFunction.from_sql(p.read_text())
        pg_function_entitity.schema = settings.POSTGRES_FUNCTIONS_SCHEMA
        sql_function_entities.append(pg_function_entitity)
    return sql_function_entities


# def sql_view_entities():
#     sql_view_entities = []
#     for p in Path(str(Path().resolve()) + "./views").glob("*.sql"):
#         pg_view_entity = PGView.from_sql(p.read_text())
#         sql_view_entities.append(pg_view_entity)
#     return sql_view_entities


def sql_trigger_entities():

    triger_paths = Path(str(Path().resolve()) + "/src/db/sql/triggers").glob("*.sql")
    triger_paths = sorted_path_by_dependency(triger_paths)
    sql_trigger_entities = []
    for p in triger_paths:
        pg_trigger_entity = PGFunction.from_sql(p.read_text())
        pg_trigger_entity.schema = settings.POSTGRES_FUNCTIONS_SCHEMA
        sql_trigger_entities.append(pg_trigger_entity)
    return sql_trigger_entities


def downgrade_functions():
    sql_function_entities_ = sql_function_entities()
    sql_function_entities_.reverse()
    for function in sql_function_entities_:
        statement = function.to_sql_statement_drop()
        legacy_engine.execute(text(statement.text))


def upgrade_functions():
    sql_function_entities_ = sql_function_entities()
    for function in sql_function_entities_:
        for statement in function.to_sql_statement_create_or_replace():
            legacy_engine.execute(text(statement.text))


def downgrade_triggers():
    sql_trigger_entities_ = sql_trigger_entities()
    sql_trigger_entities_.reverse()
    for triger in sql_trigger_entities_:
        statement = triger.to_sql_statement_drop()
        legacy_engine.execute(text(statement.text))


def upgrade_triggers():
    sql_trigger_entities_ = sql_trigger_entities()
    for triger in sql_trigger_entities_:
        for statement in triger.to_sql_statement_create_or_replace():
            legacy_engine.execute(text(statement.text))


def run(args):
    action = args.action
    material = args.material
    if action == "report":
        report()
    else:
        globals()[f"{action}_{material}"]()
        print(f"{action.title()} {material} complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade and Downgrade sql functions and triggers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            example usage:
                cd /app
                python src/db/sql/init_sql.py upgrade -m functions
                python src/db/sql/init_sql.py downgrade -m triggers
                python src/db/sql/init_sql.py report
        """
        ),
    )
    parser.add_argument(
        "action",
        help="The action to do on database",
        choices=["upgrade", "downgrade", "report"],
        type=str,
    )
    parser.add_argument(
        "--material",
        "-m",
        required="upgrade" in sys.argv or "downgrade" in sys.argv,
        help="functions or triggers",
        choices=["functions", "triggers"],
        type=str,
    )
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
