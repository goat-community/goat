CREATE
OR REPLACE VIEW layer_metadata AS WITH metadata AS (
      SELECT
            p.proname,
            regexp_replace(
                  d.description,
                  '\*\*FOR\-API\*\*|\]|\[|RETURNS col_names|geom,|geom|geometry,|geometry|origin_geometry,|origin_geometry|\s',
                  '',
                  'g'
            ) as "columns",
            'function' AS layer_type,
            'geom' AS geom_columns,
            '4326' AS srid
      FROM
            pg_proc p
            LEFT JOIN pg_description d ON d.objoid = p.oid
      WHERE
            description LIKE '%**FOR-API**%'
      UNION
      SELECT
            t.table_name AS "proname",
            string_agg(c2.column_name, ',') AS "columns",
            'table' AS layer_type,
            'geom' AS geom_columns,
            '4326' AS srid
      FROM
            information_schema.tables t
            JOIN information_schema.columns c ON c.table_name = t.table_name
            AND c.table_schema = t.table_schema
            JOIN information_schema.columns c2 ON t.table_name = c2.table_name
            AND c2.column_name NOT IN('geom', 'geometry', 'origin_geometry')
      WHERE
            c.column_name = 'geom'
            AND t.table_schema NOT IN('information_schema', 'pg_catalog')
            AND t.table_type = 'BASE TABLE'
      GROUP BY
            t.table_name,
            t.table_schema
),
json_rows AS (
      SELECT
            proname,
            json_build_object(
                  'columns',
                  "columns",
                  'layer_type',
                  layer_type,
                  'geom',
                  geom_columns,
                  'srid',
                  srid
            ) AS json_data
      FROM
            metadata
)
SELECT
      json_object_agg(proname, json_data)
FROM
      json_rows