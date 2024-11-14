"""
---------------------------------------------------------------------------------
This code is based on or incorporates material from the project:
https://github.com/developmentseed/tipg

The original code/repository is licensed under MIT License.
---------------------------------------------------------------------------------
"""

import json
from inspect import signature
from typing import Any, Callable, Dict, List, Optional, Tuple

from buildpg import RawDangerous, asyncpg, clauses, logic, render
from buildpg import SqlBlock as BuildPgSqlBlock
from buildpg import funcs as pg_funcs
from buildpg.funcs import any
from buildpg.logic import Func
from fastapi import Query
from morecantile import Tile, TileMatrixSet  # type: ignore
from pygeofilter.ast import AstType
from pygeofilter.parsers.cql2_json import parse as cql2_json_parser
from starlette.requests import Request
from tipg.collections import Collection, Column, debug_query
from tipg.errors import (
    InvalidDatetimeColumnName,
    InvalidGeometryColumnName,
    InvalidLimit,
    InvalidPropertyName,
    MissingDatetimeColumn,
)
from tipg.filter.evaluate import to_filter
from tipg.filter.filters import bbox_to_wkt
from tipg.settings import MVTSettings
from typing_extensions import Annotated


def show(component: Any) -> None:
    sql, params = render(":c", c=component)
    print(f'sql="{sql}" params={params}')


# TODO: Add test for the functions

mvt_settings = MVTSettings()


def real_columns(properties: Optional[List[Any]]) -> List[str]:
    """Return table columns optionally filtered to only include columns from properties."""
    if not properties or properties in [[], [""]]:
        return []

    cols = [
        c.description
        for c in properties
        if hasattr(c, "description") and c.type not in ["geometry", "geography"]
    ]

    return cols


def replace_properties(data: Any, replacements: Any) -> None:
    """Replace the property value in CQL2 JSON with the actual column name."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "property" and value in replacements:
                data[key] = replacements[value]
            else:
                replace_properties(value, replacements)
    elif isinstance(data, list):
        for item in data:
            replace_properties(item, replacements)


def format_to_uuid(hex_string: str) -> str:
    if len(hex_string) != 32:
        raise ValueError("The input string must be exactly 32 characters long.")

    return f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:]}"


def filter_query(
    request: Request,
    query: Annotated[
        Optional[str], Query(description="CQL2 Filter", alias="filter")
    ] = None,
) -> Optional[AstType]:
    """Parse Filter Query."""

    # Get layer_id from collectionId
    collection_id = request.path_params["collectionId"].split(".")[1]
    filter_layer_id = {
        "op": "=",
        "args": [{"property": "layer_id"}, format_to_uuid(collection_id)],
    }

    if query is not None:
        layer = request.app.state.collection_catalog["collections"].get(
            request.path_params["collectionId"]
        )
        column_mapping = {}
        for column in layer.properties:
            column_mapping[column.name] = column.description
        # Replace the properties
        cql_dict = json.loads(query)
        replace_properties(cql_dict, column_mapping)

        # Add layer_id filter
        cql_dict = {"op": "and", "args": [cql_dict, filter_layer_id]}

        data = cql2_json_parser(json.dumps(cql_dict))
        return data
    else:
        cql_dict = filter_layer_id

    return cql2_json_parser(json.dumps(cql_dict))


class ExtCollection(Collection):
    # These are the function that need to be patched.
    def _from(self, function_parameters: Optional[Dict[str, str]]) -> clauses.From:
        """Construct a FROM statement for the table."""
        if self.type == "Function":
            if not function_parameters:
                return clauses.From(self.id) + RawDangerous("()")
            params = []
            for p in self.parameters:
                if p.name in function_parameters:
                    params.append(
                        pg_funcs.cast(
                            pg_funcs.cast(function_parameters[p.name], "text"),
                            p.type,
                        )
                    )
            return clauses.From(logic.Func(self.id, *params))
        return clauses.From(self.dbschema + "." + self.table)

    def get_mvt_point(
        self,
        tile: Tile,
        tms: TileMatrixSet,
        geometry_column: Column,
        function_parameters: Optional[Dict[str, str]],
        ids: Optional[List[str]] = None,
        datetime: Optional[List[str]] = None,
        bbox: Optional[List[float]] = None,
        properties: Optional[List[str]] = None,
        cql: Optional[AstType] = None,
        geom: Optional[str] = None,
        dt: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Tuple[str, Tuple[Any, ...]]:
        """Construct a FROM statement for the table using a clustering logic build using h3."""
        select_clause = self._select_mvt(
            properties=properties,
            geometry_column=geometry_column,
            tms=tms,
            tile=tile,
        )
        from_clause = clauses.From(self.dbschema + "." + self.table)

        where_clause = self._where(
            ids=ids,
            datetime=datetime,
            bbox=bbox,
            properties=properties,  # type: ignore
            cql=cql,
            geom=geom,
            dt=dt,
            tile=tile,
            tms=tms,
        )
        limit_clause = clauses.Limit(limit)

        # Build the custom column selection query
        select_unique_values = ""
        for column in self.table_columns:
            if column.name not in ["geom", "id", "layer_id", "h3_3"]:
                select_unique_values += (
                    f"(ARRAY_AGG({column.description}))[1] AS {column.description}, "
                )
        select_unique_values = select_unique_values[:-2]

        # Get the h3 resolution based on the zoom level
        mapping_zoom_h3_resolution = {
            11: 8,
            10: 8,
            9: 7,
            8: 7,
            7: 6,
            6: 6,
            5: 5,
            4: 5,
            3: 4,
            2: 4,
            1: 3,
            0: 3,
        }
        h3_resolution = mapping_zoom_h3_resolution[tile.z]

        q, p = render(
            f"""
          WITH clustered_points AS (
              SELECT (ARRAY_AGG(layer_id))[1] AS layer_id, {select_unique_values}, (ARRAY_AGG(id))[1] AS id, (ARRAY_AGG(h3_3))[1] AS h3_3, (ARRAY_AGG(geom))[1] AS geom
              :from_clause
              :where_clause
              AND cluster_keep = TRUE
              AND ST_Intersects(geom, ST_Transform(ST_TileEnvelope({tile.z}, {tile.x}, {tile.y}), 4326))
              GROUP BY h3_cell_to_parent(h3_group, {h3_resolution})
          ),
          selected AS (
              :select_clause
              FROM clustered_points
              :limit_clause
          )
          SELECT ST_AsMVT(t.*, :layer_name) FROM selected t
          """,
            from_clause=from_clause,
            where_clause=where_clause,
            select_clause=select_clause,
            limit_clause=limit_clause,
            layer_name=self.table
            if mvt_settings.set_mvt_layername is True
            else "default",
        )

        return q, p

    def single_select_h3(
        self,
        tile: Tile,
        geometry_column: Column,
        tms: TileMatrixSet,
        properties: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        datetime: Optional[List[str]] = None,
        bbox: Optional[List[float]] = None,
        cql: Optional[AstType] = None,
        geom: Optional[str] = None,
        dt: Optional[str] = None,
        limit: Optional[int] = None,
        h3_3: Optional[int] = None,
    ) -> Dict[str, clauses.Clause]:
        select_clause = self._select_mvt(
            properties=properties,
            geometry_column=geometry_column,
            tms=tms,
            tile=tile,
        )
        from_clause = clauses.From(self.dbschema + "." + self.table)

        where_clause = self._where(
            ids=ids,
            datetime=datetime,
            bbox=bbox,
            properties=properties,  # type: ignore
            cql=cql,
            geom=geom,
            dt=dt,
            tile=tile,
            tms=tms,
            h3_3=h3_3,
        )
        limit_clause = clauses.Limit(limit)
        return {
            "select_clause": select_clause,
            "from_clause": from_clause,
            "where_clause": where_clause,
            "limit_clause": limit_clause,
        }

    def _where(
        self,
        ids: Optional[List[str]] = None,
        datetime: Optional[List[str]] = None,
        bbox: Optional[List[float]] = None,
        properties: Optional[List[Tuple[str, Any]]] = None,
        cql: Optional[AstType] = None,
        geom: Optional[str] = None,
        dt: Optional[str] = None,
        tile: Optional[Tile] = None,
        tms: Optional[TileMatrixSet] = None,
        h3_3: Optional[int] = None,
    ) -> clauses.Where:
        """Construct WHERE query."""
        wheres = [logic.S(True)]

        # `ids` filter
        if ids is not None:
            if len(ids) == 1:
                wheres.append(
                    logic.V(self.id_column)
                    == pg_funcs.cast(
                        pg_funcs.cast(ids[0], "text"),
                        self.id_column_info.type,  # type: ignore
                    )
                )
            else:
                w = [
                    logic.V(self.id_column)
                    == logic.S(
                        pg_funcs.cast(
                            pg_funcs.cast(i, "text"), self.id_column_info.type
                        )  # type: ignore
                    )
                    for i in ids
                ]
                wheres.append(pg_funcs.OR(*w))

        # `properties filter
        if properties is not None:
            w = []
            for prop, val in properties:
                col = self.get_column(prop)
                if not col:
                    raise InvalidPropertyName(f"Invalid property name: {prop}")

                w.append(
                    logic.V(col.name)
                    == logic.S(pg_funcs.cast(pg_funcs.cast(val, "text"), col.type))
                )

            if w:
                wheres.append(pg_funcs.AND(*w))

        # `bbox` filter
        geometry_column = self.get_geometry_column(geom)
        if bbox is not None and geometry_column is not None:
            wheres.append(
                logic.Func(
                    "ST_Intersects",
                    logic.S(bbox_to_wkt(bbox)),
                    logic.V(geometry_column.name),
                )
            )

        # `datetime` filter
        if datetime:
            if not self.datetime_columns:
                raise MissingDatetimeColumn(
                    "Must have timestamp typed column to filter with datetime."
                )

            datetime_column = self.get_datetime_column(dt)
            if not datetime_column:
                raise InvalidDatetimeColumnName(f"Invalid Datetime Column: {dt}.")

            wheres.append(self._datetime_filter_to_sql(datetime, datetime_column.name))

        # `CQL` filter
        if cql is not None:
            wheres.append(to_filter(cql, [p.description for p in self.properties]))  # type: ignore

        if tile and tms and geometry_column:
            # Get Tile Bounds in Geographic CRS (usually epsg:4326)
            left, bottom, right, top = tms.bounds(tile)

            # Truncate bounds to the max TMS bbox
            left, bottom = tms.truncate_lnglat(left, bottom)
            right, top = tms.truncate_lnglat(right, top)

            wheres.append(
                logic.Func(
                    "ST_Intersects",
                    logic.Func(
                        "ST_Transform",
                        logic.Func(
                            "ST_Segmentize",
                            logic.Func(
                                "ST_MakeEnvelope",
                                left,
                                bottom,
                                right,
                                top,
                                4326,
                            ),
                            right - left,
                        ),
                        pg_funcs.cast(geometry_column.srid, "int"),
                    ),
                    logic.V(geometry_column.name),
                )
            )
        if h3_3:
            wheres.append(logic.V("h3_3") == logic.S(h3_3))
        return clauses.Where(pg_funcs.AND(*wheres))

    def _select_no_geo(
        self, properties: Optional[List[str]], addid: bool = True
    ) -> BuildPgSqlBlock:
        """Construct a SELECT statement for the table."""

        nocomma = False
        columns = self.columns(properties)
        old_columns = real_columns(self.properties)
        if columns:
            select_query = "SELECT "
            for i, column in enumerate(columns):
                # Check if the column is a jsonb column and cast it to text
                if "jsonb" in old_columns[i]:
                    select_query = (
                        select_query
                        + old_columns[i]
                        + "::text"
                        + ' AS "'
                        + column
                        + '", '
                    )
                else:
                    select_query = (
                        select_query + old_columns[i] + ' AS "' + column + '", '
                    )
            select_query = select_query[:-2]
            sel = logic.as_sql_block(RawDangerous(select_query))
        else:
            sel = logic.as_sql_block(RawDangerous("SELECT "))
            nocomma = True

        if addid:
            if self.id_column:
                id_clause = logic.V(self.id_column.name).as_("tipg_id")
            else:
                id_clause = RawDangerous(" ROW_NUMBER () OVER () AS tipg_id ")
            if nocomma:
                sel = clauses.Clauses(sel, id_clause)
            else:
                sel = sel.comma(id_clause)

        return logic.as_sql_block(sel)

    def get_column(self, property_name: str) -> Optional[Column]:
        """Return column info."""
        for p in self.properties:
            if p.description == property_name:
                return p

        return None

    async def get_tile(
        self,
        *,
        pool: asyncpg.BuildPgPool,
        tms: TileMatrixSet,
        tile: Tile,
        ids_filter: Optional[List[str]] = None,
        bbox_filter: Optional[List[float]] = None,
        datetime_filter: Optional[List[str]] = None,
        properties_filter: Optional[List[Tuple[str, str]]] = None,
        function_parameters: Optional[Dict[str, str]] = None,
        cql_filter: Optional[AstType] = None,
        sortby: Optional[str] = None,
        properties: Optional[List[str]] = None,
        geom: Optional[str] = None,
        dt: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Any:
        """Build query to get Vector Tile."""

        # TODO: Define this in the .env. For now changes where not taken effect from .env. Fix this.
        mvt_settings.max_features_per_tile = 15000
        min_zoom_clustering = 11
        min_feature_cnt_clustering = 50000

        limit = limit or mvt_settings.max_features_per_tile
        geometry_column = self.get_geometry_column(geom)
        if not geometry_column:
            raise InvalidGeometryColumnName(f"Invalid Geometry Column Name {geom}")

        if limit > mvt_settings.max_features_per_tile:
            raise InvalidLimit(
                f"Limit can not be set higher than the `tipg_max_features_per_tile` setting of {mvt_settings.max_features_per_tile}"
            )

        # Build sql query to count the number of points in the tile
        select_limit = self._select
        from_limit = self._from(function_parameters)

        # Get order by geomtry size or length depending on the geometry type
        if geometry_column.geometry_type == "point":
            order_by = ""
        elif geometry_column.geometry_type == "line":
            order_by = "ORDER BY ST_LENGTH(geom) DESC"
        elif geometry_column.geometry_type == "polygon":
            order_by = "ORDER BY ST_AREA(geom) DESC"

        # If the layer is a point layer and the zoom level is less than 11, use clustering
        if geometry_column.geometry_type == "point" and tile.z < min_zoom_clustering:
            # Check if column h3_group and cluster_keep exists
            q, p = render(
                """
              SELECT column_name
              FROM information_schema.columns
              WHERE table_schema = :schema AND table_name = :table
              AND column_name IN ('cluster_keep', 'h3_group')
              """,
                schema=self.dbschema,
                table=self.table,
            )
            debug_query(q, *p)  # type: ignore
            async with pool.acquire() as conn:
                columns = await conn.fetch(q, *p)

            if len(columns) == 2:
                # Check the total feature count of the layer and therefore adapt the where query to only layer_id
                filter_by_layer_id = {
                    "op": "=",
                    "args": [
                        {"property": "layer_id"},
                        format_to_uuid(self.id.split(".")[1]),
                    ],
                }
                filter_by_layer_id = cql2_json_parser(json.dumps(filter_by_layer_id))
                filter_by_layer_id = to_filter(
                    filter_by_layer_id, [p.description for p in self.properties]
                )  # type: ignore
                where_cnt = clauses.Where(filter_by_layer_id)
                q, p = render(
                    f"""WITH features_to_count AS (
                      SELECT id
                      :from_limit
                      :where_limit
                      AND ST_Intersects(geom, ST_Transform(ST_TileEnvelope({tile.z}, {tile.x}, {tile.y}), 4326))
                      :limit
                  )
                  SELECT COUNT(*) FROM features_to_count
                  """,
                    select_limit=select_limit,
                    from_limit=from_limit,
                    where_limit=where_cnt,
                    limit=clauses.Limit(min_feature_cnt_clustering),
                )
                async with pool.acquire() as conn:
                    count = await conn.fetchval(q, *p)

                if count >= limit:
                    q, p = self.get_mvt_point(
                        function_parameters=function_parameters,
                        ids=ids_filter,
                        datetime=datetime_filter,
                        bbox=bbox_filter,
                        properties=properties,
                        cql=cql_filter,
                        geom=geom,
                        dt=dt,
                        tile=tile,
                        tms=tms,
                        geometry_column=geometry_column,
                        limit=limit,
                    )
                    async with pool.acquire() as conn:
                        return await conn.fetchval(q, *p)

        # Check if distributed table to get relevant h3_3_grids
        if self.distributed is True:  # type: ignore
            q, p = render(
                f"""
              SELECT DISTINCT h3_3
              FROM basic.h3_3
              WHERE ST_Intersects(geom, ST_Transform(ST_TileEnvelope({tile.z}, {tile.x}, {tile.y}), 4326))
              """
            )
            debug_query(q, *p)  # type: ignore
            async with pool.acquire() as conn:
                h3_3_grids = await conn.fetch(q, *p)
                h3_3_grids = [row["h3_3"] for row in h3_3_grids]

            # Build query for each h3_3_grid and merge with union all
            union_query = ""
            query_values = {}
            for h3_3_grid in h3_3_grids:
                h3_3_grid_string = str(h3_3_grid)
                query = self.single_select_h3(
                    properties=properties,
                    geometry_column=geometry_column,
                    ids=ids_filter,
                    datetime=datetime_filter,
                    bbox=bbox_filter,
                    cql=cql_filter,
                    geom=geom,
                    dt=dt,
                    tile=tile,
                    tms=tms,
                    limit=limit,
                    h3_3=h3_3_grid,
                )
                union_query += f"""
                  (
                      :select_clause_{h3_3_grid_string}
                      :from_clause_{h3_3_grid_string}
                      :where_clause_{h3_3_grid_string}
                      {order_by}
                      :limit_clause_{h3_3_grid_string}
                  )
                  UNION ALL
                  """
                query_values.update(
                    {
                        f"select_clause_{h3_3_grid_string}": query["select_clause"],
                        f"from_clause_{h3_3_grid_string}": query["from_clause"],
                        f"where_clause_{h3_3_grid_string}": query["where_clause"],
                        f"limit_clause_{h3_3_grid_string}": query["limit_clause"],
                    }
                )

            union_query = union_query[:-26]
            q, p = render(
                f"""
              WITH
              t AS (
                  {union_query}
              )
              SELECT ST_AsMVT(t.*, :l) FROM t
              """,
                **query_values,
                l=self.table if mvt_settings.set_mvt_layername is True else "default",
            )

        else:
            q, p = render(
                f"""
              WITH
              t AS (
                  :select_clause
                  :from_clause
                  :where_clause
                  {order_by}
                  :limit_clause
              )
              SELECT ST_AsMVT(t.*, :l) FROM t
              """,
                select_clause=self._select_mvt(
                    properties=properties,
                    geometry_column=geometry_column,
                    tms=tms,
                    tile=tile,
                ),
                from_clause=self._from(function_parameters),
                where_clause=self._where(
                    ids=ids_filter,
                    datetime=datetime_filter,
                    bbox=bbox_filter,
                    properties=properties_filter,
                    cql=cql_filter,
                    geom=geom,
                    dt=dt,
                    tms=tms,
                    tile=tile,
                ),
                limit_clause=clauses.Limit(limit),
                l=self.table if mvt_settings.set_mvt_layername is True else "default",
            )

        async with pool.acquire() as conn:
            return await conn.fetchval(q, *p)


class Operator:
    """Filter Operators."""

    OPERATORS: Dict[str, Callable[..., Any]] = {
        "is_null": lambda f, a=None: f.is_(None),
        "is_not_null": lambda f, a=None: f.isnot(None),
        "==": lambda f, a: f == a,
        "=": lambda f, a: f == a,
        "eq": lambda f, a: f == a,
        "!=": lambda f, a: f != a,
        "<>": lambda f, a: f != a,
        "ne": lambda f, a: f != a,
        ">": lambda f, a: f > a,
        "gt": lambda f, a: f > a,
        "<": lambda f, a: f < a,
        "lt": lambda f, a: f < a,
        ">=": lambda f, a: f >= a,
        "ge": lambda f, a: f >= a,
        "<=": lambda f, a: f <= a,
        "le": lambda f, a: f <= a,
        "like": lambda f, a: f.like(a),
        "ilike": lambda f, a: f.ilike(a),
        "not_ilike": lambda f, a: ~f.ilike(a),
        "in": lambda f, a: f == any(a),
        "not_in": lambda f, a: ~f == any(a),
        "any": lambda f, a: f.any(a),
        "not_any": lambda f, a: f.not_(f.any(a)),
        "INTERSECTS": lambda f, a: Func(
            "st_intersects",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "DISJOINT": lambda f, a: Func(
            "st_disjoint",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "CONTAINS": lambda f, a: Func(
            "st_contains",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "WITHIN": lambda f, a: Func(
            "st_within",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "TOUCHES": lambda f, a: Func(
            "st_touches",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "CROSSES": lambda f, a: Func(
            "st_crosses",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "OVERLAPS": lambda f, a: Func(
            "st_overlaps",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "EQUALS": lambda f, a: Func(
            "st_equals",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
        ),
        "RELATE": lambda f, a, pattern: Func(
            "st_relate",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
            pattern,
        ),
        "DWITHIN": lambda f, a, distance: Func(
            "st_dwithin",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
            distance,
        ),
        "BEYOND": lambda f, a, distance: ~Func(
            "st_dwithin",
            f,
            Func("st_transform", Func("st_geomfromtext", a), Func("st_srid", f)),
            distance,
        ),
        "+": lambda f, a: f + a,
        "-": lambda f, a: f - a,
        "*": lambda f, a: f * a,
        "/": lambda f, a: f / a,
    }

    def __init__(self, operator: str | None = None) -> None:
        """Init."""
        if not operator:
            operator = "=="

        if operator not in self.OPERATORS:
            raise Exception("Operator `{}` not valid.".format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)
