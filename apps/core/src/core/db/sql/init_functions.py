from sqlalchemy import create_engine
from core.core.config import settings
from core.db.sql.create_functions import FunctionManager


def main():
    engine = create_engine(settings.POSTGRES_DATABASE_URI)
    function_manager = FunctionManager(engine, "/src/db/sql/functions", "basic")
    function_manager.update_functions()


if __name__ == "__main__":
    main()
