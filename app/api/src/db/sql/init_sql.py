from pathlib import Path

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from alembic_utils.pg_view import PGView


def sql_function_entities():
    sql_function_entities = []

    for p in Path(str(Path().resolve()) + "/src/db/sql/functions").rglob('*.sql'):
        pg_function_entitity = PGFunction.from_sql(p.read_text())
        sql_function_entities.append(pg_function_entitity)
    return sql_function_entities


def sql_view_entities():
    sql_view_entities = []
    for p in Path("./views").glob("*.sql"):
        pg_view_entity = PGView.from_sql(p.read_text())
        sql_view_entities.append(pg_view_entity)
    return sql_view_entities


def sql_trigger_entities():
    sql_trigger_entities = []
    for p in Path("./triggers").glob("*.sql"):
        pg_trigger_entity = PGTrigger.from_sql(p.read_text())
        sql_trigger_entities.append(pg_trigger_entity)
    return sql_trigger_entities
