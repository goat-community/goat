import asyncio
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import text

from src.core.config import settings
from src.db.session import session_manager
from src.endpoints.deps import get_db_session
from src.main import app

now = datetime.now().strftime("%Y%m%d%H%M%S")
dbname = f"{now}_goat_test"
test_db = factories.postgresql_noproc(
    host=settings.POSTGRES_SERVER,
    port=5432,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    dbname=dbname,
)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def session_fixture(test_db, event_loop):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password

    with DatabaseJanitor(pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password):
        # Create database
        test_db_url = f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        session_manager.init(test_db_url)
        yield
        await session_manager.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables(session_fixture):
    async with session_manager.connect() as connection:
        # Create customer schema
        await connection.execute(text("""CREATE SCHEMA IF NOT EXISTS customer"""))
        await connection.execute(text("""CREATE EXTENSION IF NOT EXISTS postgis"""))
        await connection.execute(text("""CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""""))
        await session_manager.drop_all(connection)
        await session_manager.create_all(connection)
        # run triggers
        # triggers_file = os.path.join(Path(__file__).resolve().parent.parent, "src/db/triggers.sql")
        # command = f'psql "postgresql://{settings.MASTER_POSTGRES_USER}:{settings.MASTER_POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{dbname}" -f {triggers_file}'
        # process = subprocess.Popen(
        #     command,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     shell=True,
        #     universal_newlines=True,
        # )
        # output, error = process.communicate()
        # if process.returncode != 0:
        #     raise Exception(f"Error running psql command: {error}")
        # print("Triggers created")


@pytest_asyncio.fixture(autouse=True)
async def session_override(session_fixture):
    async def get_db_override():
        async with session_manager.session() as session:
            yield session

    app.dependency_overrides[get_db_session] = get_db_override


@pytest_asyncio.fixture
async def db_session():
    async with session_manager.session() as session:
        yield session
