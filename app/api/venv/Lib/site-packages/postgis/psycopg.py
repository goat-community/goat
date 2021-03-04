from psycopg2 import extensions

from .geometry import Geometry


def register(connection):
    if isinstance(connection, extensions.cursor):
        # Retrocompat.
        cursor = connection
    else:
        cursor = connection.cursor()
    cursor.execute("SELECT NULL::geometry")
    oid = cursor.description[0][1]
    GEOMETRY = extensions.new_type((oid, ), "GEOMETRY", Geometry.from_ewkb)
    extensions.register_type(GEOMETRY)

    cursor.execute("SELECT NULL::geography")
    oid = cursor.description[0][1]
    GEOGRAPHY = extensions.new_type((oid, ), "GEOGRAPHY", Geometry.from_ewkb)
    extensions.register_type(GEOGRAPHY)
