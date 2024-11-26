from routing.core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# async def set_type_codec(
#     conn: asyncpg.Connection,
#     typenames: list[str],
#     encode: Callable[[str], str] = lambda a: a,
#     decode: Callable[[str], str] = lambda a: a,
#     schema: str = "pg_catalog",
#     format: str = "text",
# ) -> None:
#     conn._check_open()
#     for typename in typenames:
#         typeinfo = await conn.fetchrow(
#             asyncpg.introspection.TYPE_BY_NAME, typename, schema
#         )
#         if not typeinfo:
#             raise ValueError(f"unknown type: {schema}.{typename}")

#         oid = typeinfo["oid"]
#         conn._protocol.get_settings().add_python_codec(
#             oid, typename, schema, "scalar", encode, decode, format
#         )

#     # Statement cache is no longer valid due to codec changes.
#     conn._drop_local_statement_cache()


# async def setup(conn: asyncpg.Connection) -> None:
#     # Register geometry type
#     await conn.set_type_codec(
#         "geometry", encoder=str, decoder=str, schema="public", format="text"
#     )

#     # Register integer array type
#     await set_type_codec(
#         conn,
#         ["_int4"],
#         encode=lambda a: "{"
#         + ",".join(map(str, a))
#         + "}",  # Convert list to PostgreSQL array literal
#         decode=lambda a: (
#             list(map(int, a.strip("{}").split(","))) if a else []
#         ),  # Convert PostgreSQL array literal to list
#         schema="pg_catalog",
#         format="text",
#     )

#     # Register UUID array type
#     await set_type_codec(
#         conn,
#         ["_uuid"],
#         encode=lambda a: "{" + ",".join(a) + "}",  # Directly join UUID strings
#         decode=lambda a: (
#             a.strip("{}").split(",") if a else []
#         ),  # Split string into UUID strings
#         schema="pg_catalog",
#         format="text",
#     )

# async def setup(conn: asyncpg.Connection) -> None:
#     """
#     Cockroachdb sets array types of native types in the same namespace as pg native type in 'pg_catalog.pg_type'
#     asyncpg assumes that all new composite types are not going to be in there, so it does not have native codecs for arrays of native types, and goes through a very expensive introspection process to infer the types.

#     This lists all array types in cockroachdb and creates codecs for them and registers them as well.

#     Some array types have been commented out since they're not used in the code.

#     Solution loosely based on the one in here https://github.com/MagicStack/asyncpg/issues/413
#     """

#     # got the array types by querying:
#     # """SELECT *
#     # FROM pg_catalog.pg_type
#     # where typcategory = 'A';"""

#     typenames = [
#         "_bit",
#         "_bool",
#         "_bpchar",
#         "_bytea",
#         "_char",
#         "_date",
#         "_float4",
#         "_float8",
#         "_int2",
#         "_int4",
#         "_int8",
#         "_interval",
#         "_name",
#         "_numeric",
#         "_text",
#         "_time",
#         "_timestamp",
#         "_timestamptz",
#         "_timetz",
#         "_uuid",
#         "_varchar",
#     ]
#     schema = "pg_catalog"
#     conn._check_open()

#     timeout = 5  # seconds

#     type_by_names = f"""\
#     SELECT
#         t.oid,
#         t.typelem AS elemtype,
#         t.typtype AS kind,
#         t.typname as name,
#         parent.typname as elemtype_name,
#         'pg_catalog' as ns,
#         parent.typdelim as elemdelim,
#         0 as depth,
#         NULL as basetype,
#         NULL as range_subtype,
#         NULL as attrtypoids,
#         NULL as attrnames,
#         NULL as basetype_name,
#         NULL as range_subtype_name
#     FROM
#         pg_catalog.pg_type AS t
#     LEFT JOIN
#         pg_catalog.pg_type as parent on parent.oid = t.typelem
#     WHERE
#         t.typname in {str(tuple(typenames))}
#     """
#     array_types_records = []

#     query_args = []

#     array_type = await conn._execute(
#         type_by_names,
#         query_args,
#         0,
#         timeout,
#         ignore_custom_codec=True,
#     )
#     array_types_records.extend(array_type)

#     conn._protocol.get_settings().register_data_types(array_types_records)


# def register_event_listeners(async_engine):
#     @event.listens_for(async_engine.sync_engine, "connect")
#     def register_custom_types(dbapi_connection, connection_record):
#         dbapi_connection.run_async(setup)


async_engine = create_async_engine(
    str(settings.ASYNC_SQLALCHEMY_DATABASE_URI), pool_pre_ping=True
)

async_session = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False
)
# register_event_listeners(async_engine)
