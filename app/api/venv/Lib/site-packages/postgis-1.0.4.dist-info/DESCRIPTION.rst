[![Circle CI](https://img.shields.io/circleci/project/yohanboniface/psycopg-postgis.svg)](https://circleci.com/gh/yohanboniface/psycopg-postgis) [![PyPI](https://img.shields.io/pypi/v/psycopg-postgis.svg)](https://pypi.python.org/pypi/psycopg-postgis) [![PyPI](https://img.shields.io/pypi/pyversions/psycopg-postgis.svg)](https://pypi.python.org/pypi/psycopg-postgis) [![PyPI](https://img.shields.io/pypi/implementation/psycopg-postgis.svg)](https://pypi.python.org/pypi/psycopg-postgis) [![PyPI](https://img.shields.io/pypi/status/psycopg-postgis.svg)](https://pypi.python.org/pypi/psycopg-postgis)

# python-postgis

PostGIS helpers for psycopg2 and asyncpg.

## Install

    pip install postgis

If you want a compiled version, first install `cython`:

    pip install cython
    pip install postgis


## Usage

You need to register the extension:

    # With psycopg2
    > from postgis.psycopg import register
    > register(connection)

    # With asyncpg
    > from postgis.asyncpg import register
    > await register(connection)

Then you can pass python geometries instance to psycopg:

    > cursor.execute('INSERT INTO table (geom) VALUES (%s)', [Point(x=1, y=2, srid=4326)])

And retrieve data as python geometries instances:

    > cursor.execute('SELECT geom FROM points LIMIT 1')
    > geom = cursor.fetchone()[0]
    > geom
    <Point POINT(1.0 2.0)>


## Example with psycopg2

    > import psycopg2
    > from postgis import LineString
    > from postgis.psycopg import register
    > db = psycopg2.connect(dbname="test")
    > register(db)
    > cursor.execute('CREATE TABLE IF NOT EXISTS mytable ("geom" geometry(LineString) NOT NULL)')
    > cursor.execute('INSERT INTO mytable (geom) VALUES (%s)', [LineString([(1, 2), (3, 4)], srid=4326)])
    > cursor.execute('SELECT geom FROM mytable LIMIT 1')
    > geom = cursor.fetchone()[0]
    > geom
    <LineString LINESTRING(1.0 2.0, 3.0 4.0)>
    > geom[0]
    <Point POINT(1.0 2.0)>
    > geom.coords
    ((1.0, 2.0), (3.0, 4.0))
    > geom.geojson
    {'coordinates': ((1.0, 2.0), (3.0, 4.0)), 'type': 'LineString'}
    > str(geom.geojson)
    '{"type": "LineString", "coordinates": [[1, 2], [3, 4]]}'


## Example with asyncpg

    from postgis.asyncpg import register
    pool = await create_pool(**DB_CONFIG, loop=loop, max_size=100,
                             init=register)


