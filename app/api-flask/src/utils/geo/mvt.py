# https://github.com/pramsey/minimal-mvt/blob/master/minimal-mvt.py
import re
from urllib import parse

class MVT:

    # Search REQUEST_PATH for /{z}/{x}/{y}.{format} patterns
    def pathToTile(self, path):
        m = re.search(r"^\/(\d+)\/(\d+)\/(\d+)\.(\w+)", path)
        if m:
            return {
                "zoom": int(m.group(1)),
                "x": int(m.group(2)),
                "y": int(m.group(3)),
                "format": m.group(4),
            }
        else:
            return None

    # Do we have all keys we need?
    # Do the tile x/y coordinates make sense at this zoom level?

    def tileIsValid(self, tile):
        if not ("x" in tile and "y" in tile and "zoom" in tile):
            return False
        if "format" not in tile or tile["format"] not in ["pbf", "mvt"]:
            return False
        size = 2 ** tile["zoom"]
        if tile["x"] >= size or tile["y"] >= size:
            return False
        if tile["x"] < 0 or tile["y"] < 0:
            return False
        return True

    # Calculate envelope in "Spherical Mercator" (https://epsg.io/3857)

    def tileToEnvelope(self, tile):
        # Width of world in EPSG:3857
        worldMercMax = 20037508.3427892
        worldMercMin = -1 * worldMercMax
        worldMercSize = worldMercMax - worldMercMin
        # Width in tiles
        worldTileSize = 2 ** tile["zoom"]
        # Tile width in EPSG:3857
        tileMercSize = worldMercSize / worldTileSize
        # Calculate geographic bounds from tile coordinates
        # XYZ tile coordinates are in "image space" so origin is
        # top-left, not bottom right
        env = dict()
        env["xmin"] = worldMercMin + tileMercSize * tile["x"]
        env["xmax"] = worldMercMin + tileMercSize * (tile["x"] + 1)
        env["ymin"] = worldMercMax - tileMercSize * (tile["y"] + 1)
        env["ymax"] = worldMercMax - tileMercSize * (tile["y"])
        return env

    # Generate SQL to materialize a query envelope in EPSG:3857.
    # Densify the edges a little so the envelope can be
    # safely converted to other coordinate systems.

    def envelopeToBoundsSQL(self, env):
        DENSIFY_FACTOR = 4
        env["segSize"] = (env["xmax"] - env["xmin"]) / DENSIFY_FACTOR
        sql_tmpl = "ST_Segmentize(ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}, 3857),{segSize})"
        return sql_tmpl.format(**env)

    # Generate a SQL query to pull a tile worth of MVT data
    # from the table of interest.

    def toSQL(self, tbl):
        # Materialize the bounds
        # Select the relevant geometry and clip to MVT bounds
        # Convert to MVT format
        sql_tmpl = """
            WITH 
            bounds AS (
                SELECT {env} AS geom, 
                       {env}::box2d AS b2d
            ),
            mvtgeom AS (
                SELECT ST_AsMVTGeom(ST_Transform(t.{geomColumn}, 3857), bounds.b2d) AS geom, 
                       {attrColumns}
                FROM {table} t, bounds
                WHERE ST_Intersects(t.{geomColumn}, ST_Transform(bounds.geom, {srid}))
            ) 
            SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
        """
        return sql_tmpl.format(**tbl)



