from sqlalchemy.engine import create_engine

from src.core.config import SyncPostgresDsn, settings


def get_db_uri(dbname):
    return SyncPostgresDsn.build(
            scheme="postgresql",
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            path=f"/{dbname}",
        )

staging_uri = get_db_uri('staging')
chapar_uri = get_db_uri('chapar')

chapar_engine = create_engine(chapar_uri, future=False)
