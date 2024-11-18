import asyncpg
from routing.core.config import settings
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker


async def set_type_codec(
    conn,
    typenames,
    encode=lambda a: a,
    decode=lambda a: a,
    schema="pg_catalog",
    format="text",
):
    conn._check_open()
    for typename in typenames:
        typeinfo = await conn.fetchrow(
            asyncpg.introspection.TYPE_BY_NAME, typename, schema
        )
        if not typeinfo:
            raise ValueError(f"unknown type: {schema}.{typename}")

        oid = typeinfo["oid"]
        conn._protocol.get_settings().add_python_codec(
            oid, typename, schema, "scalar", encode, decode, format
        )

    # Statement cache is no longer valid due to codec changes.
    conn._drop_local_statement_cache()


async def setup(conn):
    # Register geometry type
    await conn.set_type_codec(
        "geometry", encoder=str, decoder=str, schema="public", format="text"
    )

    # Register integer array type
    await set_type_codec(
        conn,
        ["_int4"],
        encode=lambda a: "{"
        + ",".join(map(str, a))
        + "}",  # Convert list to PostgreSQL array literal
        decode=lambda a: (
            list(map(int, a.strip("{}").split(","))) if a else []
        ),  # Convert PostgreSQL array literal to list
        schema="pg_catalog",
        format="text",
    )

    # Register UUID array type
    await set_type_codec(
        conn,
        ["_uuid"],
        encode=lambda a: "{" + ",".join(a) + "}",  # Directly join UUID strings
        decode=lambda a: (
            a.strip("{}").split(",") if a else []
        ),  # Split string into UUID strings
        schema="pg_catalog",
        format="text",
    )


def register_event_listeners(async_engine):
    @event.listens_for(async_engine.sync_engine, "connect")
    def register_custom_types(dbapi_connection, connection_record):
        dbapi_connection.run_async(setup)


async_engine = create_async_engine(
    settings.ASYNC_SQLALCHEMY_DATABASE_URI, pool_pre_ping=True
)

async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
register_event_listeners(async_engine)
